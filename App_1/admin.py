from django.contrib.gis import admin

from App_1.forms import AtLeastOneFormSet, OccurrenceForm, SiteForm

# Register your models here.
from .models import AttributeOccurrence, AttributeCategory, AttributeChoice, AttributeSite, Metric, MetricType, Occurrence, Site, File

class CustomGeoWidgetAdmin(admin.GISModelAdmin):
    """Custom GISModelAdmin with default coordinates to Portugal."""
    gis_widget_kwargs = {
        'attrs': {
            'default_zoom': 6,
            'default_lon': -8.130229,
            'default_lat': 39.694819,
        },
    }

class OccurrencesInline(admin.TabularInline):
    model = Occurrence
    fields = ('name', 'latitude', 'longitude')
    show_change_link = True
    extra = 1
    formset = AtLeastOneFormSet
    form = OccurrenceForm

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
class SiteAdmin(CustomGeoWidgetAdmin):
    list_display = ('name', 'national_site_code', 'parish', 'added_by')
    list_filter = ('added_by',)
    search_fields = ['name', 'national_site_code', 'parish',]
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
    form = SiteForm

@admin.register(Occurrence)
class OccurrenceAdmin(CustomGeoWidgetAdmin):
    list_display = ('name', 'acronym', 'site', 'added_by')
    list_filter = ('added_by',)
    search_fields = ['name', 'acronym', 'site',]
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

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ('type', 'occurrence')
    list_filter = ('type',)
    search_fields = ['type', 'occurrence']
    fields = ('type', 'occurrence', ('auto_value', 'confirmed_value'))

@admin.register(AttributeCategory)
class AttributeCategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    inlines = [AttributeChoicesInline]

@admin.register(AttributeChoice)
class AttributeChoicesAdmin(admin.ModelAdmin):
    list_display = ('value', 'category')
    list_filter = ('category',)
    search_fields = ['value', 'category']

@admin.register(AttributeOccurrence)
class AttributeOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('value', 'occurrence')
    list_filter = ('value',)
    search_fields = ['value', 'occurrence']

@admin.register(AttributeSite)
class AttributeSiteAdmin(admin.ModelAdmin):
    list_display = ('value', 'site')
    list_filter = ('value',)
    search_fields = ['value', 'site']
