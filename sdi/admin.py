from django import forms
from django.contrib.gis import admin
from django.contrib.gis.db import models
from leaflet.admin import LeafletGeoAdmin
from sdi.forms import AtLeastOneFormSet, OccurrenceForm, SiteFormAdmin

# Register your models here.
from .models import AttributeOccurrence, AttributeCategory, AttributeChoice, AttributeSite, Metric, MetricType, Occurrence, Site, File

class OccurrencesInline(admin.TabularInline):
    model = Occurrence
    fields = ('name', 'latitude', 'longitude', 'location')
    show_change_link = True
    extra = 1
    formset = AtLeastOneFormSet
    form = OccurrenceForm
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

class FilesInlineSite(admin.TabularInline):
    model = File.site.through
    verbose_name = "Related File"
    show_change_link = True
    extra = 0

class FilesInlineOccurrence(admin.TabularInline):
    model = File.occurrence.through
    verbose_name = "Related File"
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
    inlines = [OccurrencesInline, AttributesSiteInline, FilesInlineSite]
    form = SiteFormAdmin

@admin.register(Occurrence)
class OccurrenceAdmin(LeafletGeoAdmin):
    list_display = ('name', 'acronym', 'site', 'added_by')
    list_filter = ('added_by',)
    search_fields = ['name', 'acronym', 'site__name',]
    list_per_page = 50
    form = OccurrenceForm
    fieldsets = (
        (None, {
            'fields': ('name', 'acronym', 'toponym', 'owner', 'altitude', 'site')
        }),
        ('Location', {
            'fields': ('location', tuple(['latitude', 'longitude']), 'bounding_polygon')
        }),
        (None, {
            'fields': ('added_by',)
        }),
    )
    inlines = [AttributesOccurrenceInline, MetricsInline, FilesInlineOccurrence]

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'creation_date', 'added_by')
    list_filter = ('type', 'added_by',)
    search_fields = ['name', 'creation_date']
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'file')
        }),
        ('Associations', {
            'fields': ('site', 'occurrence')
        }),
        (None, {
            'fields': ('added_by',)
        }),
    )   

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
