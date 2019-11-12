# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 12:30:45
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-12 21:15:47
from django.contrib import admin
from django.http import Http404, JsonResponse
from django.urls import reverse

from .forms import TranslationsForm
from .models import Language, TranslatableFields, Translations


@admin.register(Language)
class AdminLanguage(admin.ModelAdmin):
    search_fields = ('iso_639_1', )


@admin.register(TranslatableFields)
class AdminTranslatableFields(admin.ModelAdmin):
    search_fields = ('name', 'title')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


@admin.register(Translations)
class AdminTranslations(admin.ModelAdmin):
    form = TranslationsForm
    list_display = ('content_object', 'lang', 'field', 'value')
    list_filter = ('content_type', )
    fieldsets = ((None, {
        'fields': (
            ('field', 'lang'),
            'object_id',
            'value',
        ),
    }), (
        'hidden',
        {
            'classes': ('hidden', ),
            'fields': ('content_type', ),
        },
    ))
    autocomplete_fields = ('field', 'lang')
    url_name = '%s:%s_%s_autocomplete'

    def _changeform_view(self, request, object_id, form_url, extra_context):
        fld_id = request.GET.get('field_id')
        id_obj = request.GET.get('id_obj')
        if fld_id:
            try:
                ct = TranslatableFields.objects.get(id=fld_id).content_type
                model = ct.model_class()
                return JsonResponse({
                    'pk': ct.pk,
                    'url': reverse(self.url_name % (self.admin_site.name, model._meta.app_label, model._meta.model_name)),
                    'text': str(model.objects.get(pk=id_obj)) if id_obj else '',
                })
            except Exception:
                return Http404('Error get content type')
        return super()._changeform_view(request, object_id, form_url, extra_context)
