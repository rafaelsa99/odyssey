from django import forms
from django.contrib.gis import admin
from django.contrib.gis.db import models
from leaflet.admin import LeafletGeoAdmin
from .forms import AtLeastOneFormSet, OccurrenceFormAdmin, SiteFormAdmin

# Register your models here.
from .models import AttributeOccurrence, AttributeCategory, AttributeChoice, AttributeSite, Metric, MetricType, Occurrence, Site, DocumentOccurrence, DocumentSite

class OccurrencesInline(admin.TabularInline):
    model = Occurrence
    fields = ('designation', 'latitude_occurrence', 'longitude_occurrence', 'position')
    show_change_link = True
    extra = 1
    formset = AtLeastOneFormSet
    form = OccurrenceFormAdmin
    formfield_overrides = {
        models.PointField: {'widget': forms.HiddenInput()},
    }

class MetricsInline(admin.TabularInline):
    model = Metric
    fields = ('type', 'auto_value', 'confirmed_value')
    show_change_link = True
    extra = 0

class AttributesOccurrenceInline(admin.TabularInline):
    model = AttributeOccurrence
    fields = ('value',)
    show_change_link = True
    extra = 0
    verbose_name_plural = "Attributes"

class AttributesSiteInline(admin.TabularInline):
    model = AttributeSite
    fields = ('value',)
    show_change_link = True
    extra = 0
    verbose_name_plural = "Attributes"

class DocumentsInlineSite(admin.TabularInline):
    model = DocumentSite
    verbose_name = "Related Document"
    show_change_link = True
    extra = 0

class DocumentsInlineOccurrence(admin.TabularInline):
    model = DocumentOccurrence
    verbose_name = "Related Document"
    show_change_link = True
    extra = 0

class AttributeChoicesInline(admin.TabularInline):
    model = AttributeChoice
    show_change_link = True
    extra = 0

@admin.register(Site)
class SiteAdmin(LeafletGeoAdmin):
    list_display = ('name', 'national_site_code', 'parish', 'added_by')
    list_filter = ('added_by',)
    search_fields = ['name', 'national_site_code', 'parish',]
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': (tuple(['name', 'national_site_code']))
        }),
        ('Location', {
            'fields': ('country_iso', 'parish', 'location', tuple(['latitude', 'longitude']), 'surrounding_polygon')
        }),
        (None, {
            'fields': ('added_by',)
        }),
    )
    inlines = [OccurrencesInline, AttributesSiteInline, DocumentsInlineSite]
    form = SiteFormAdmin

@admin.register(Occurrence)
class OccurrenceAdmin(LeafletGeoAdmin):
    list_display = ('designation', 'acronym', 'site', 'added_by')
    list_filter = ('added_by',)
    search_fields = ['designation', 'acronym', 'site__name',]
    list_per_page = 50
    form = OccurrenceFormAdmin
    fieldsets = (
        (None, {
            'fields': ('designation', 'acronym', 'toponym', 'owner', 'altitude', 'site')
        }),
        ('Location', {
            'fields': ('position', tuple(['latitude_occurrence', 'longitude_occurrence']), 'bounding_polygon')
        }),
        (None, {
            'fields': ('added_by',)
        }),
    )
    inlines = [AttributesOccurrenceInline, MetricsInline, DocumentsInlineOccurrence]  

@admin.register(MetricType)
class MetricTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 50

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('type', 'occurrence')
    list_filter = ('type',)
    list_per_page = 50
    search_fields = ['type', 'occurrence__name']
    fields = ('type', 'occurrence', ('auto_value', 'confirmed_value'))

@admin.register(AttributeCategory)
class AttributeCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 50
    inlines = [AttributeChoicesInline]

@admin.register(AttributeChoice)
class AttributeChoicesAdmin(admin.ModelAdmin):
    list_display = ('value', 'category')
    list_filter = ('category',)
    list_per_page = 50
    search_fields = ['value', 'category__name']

@admin.register(AttributeOccurrence)
class AttributeOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('value', 'occurrence')
    list_filter = ('value',)
    list_per_page = 50
    search_fields = ['value', 'occurrence__name']

@admin.register(AttributeSite)
class AttributeSiteAdmin(admin.ModelAdmin):
    list_display = ('value', 'site')
    list_filter = ('value',)
    list_per_page = 50
    search_fields = ['value', 'site__name']

@admin.register(DocumentOccurrence)
class DocumentOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('document', 'occurrence')
    list_filter = ('document',)
    list_per_page = 50
    search_fields = ['document', 'occurrence__name']

@admin.register(DocumentSite)
class DocumentSiteAdmin(admin.ModelAdmin):
    list_display = ('document', 'site')
    list_filter = ('document',)
    list_per_page = 50
    search_fields = ['document', 'site__name']