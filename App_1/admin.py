from django.contrib.gis import admin

# Register your models here.
from .models import Attribute, AttributeCategory, AttributeChoice, Metric, MetricType, Occurrence, Site, File

admin.site.register(Site, admin.ModelAdmin)
admin.site.register(Occurrence, admin.ModelAdmin)
admin.site.register(File, admin.ModelAdmin)
admin.site.register(MetricType, admin.ModelAdmin)
admin.site.register(Metric, admin.ModelAdmin)
admin.site.register(AttributeCategory, admin.ModelAdmin)
admin.site.register(AttributeChoice, admin.ModelAdmin)
admin.site.register(Attribute, admin.ModelAdmin)