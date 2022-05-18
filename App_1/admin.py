from django.contrib.gis import admin

from App_1.forms import AtLeastOneFormSet, OccurrenceForm, SiteForm

# Register your models here.
from .models import Attribute, AttributeCategory, AttributeChoice, Metric, MetricType, Occurrence, Site, File

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

@admin.register(Site)
class SiteAdmin(CustomGeoWidgetAdmin):
    list_display = ('name', 'national_site_code', 'parish', 'added_by')
    list_filter = ('added_by',)
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
    inlines = [OccurrencesInline]
    form = SiteForm

@admin.register(Occurrence)
class OccurrenceAdmin(CustomGeoWidgetAdmin):
    list_display = ('name', 'acronym', 'site', 'added_by')
    list_filter = ('added_by',)
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
    # Add Inline for Metrics and Attributes


admin.site.register(File, admin.ModelAdmin)
admin.site.register(MetricType, admin.ModelAdmin)
admin.site.register(Metric, admin.ModelAdmin)
admin.site.register(AttributeCategory, admin.ModelAdmin)
admin.site.register(AttributeChoice, admin.ModelAdmin)
admin.site.register(Attribute, admin.ModelAdmin)