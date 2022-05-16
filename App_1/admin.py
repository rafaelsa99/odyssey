from django.contrib.gis import admin

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

admin.site.register(Site, CustomGeoWidgetAdmin)
admin.site.register(Occurrence, CustomGeoWidgetAdmin)
admin.site.register(File, admin.ModelAdmin)
admin.site.register(MetricType, admin.ModelAdmin)
admin.site.register(Metric, admin.ModelAdmin)
admin.site.register(AttributeCategory, admin.ModelAdmin)
admin.site.register(AttributeChoice, admin.ModelAdmin)
admin.site.register(Attribute, admin.ModelAdmin)