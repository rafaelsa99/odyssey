from turtle import ondrag
from django.contrib.gis.db import models
from django.conf import settings
from django_countries.fields import CountryField

# Create your models here.
class Site(models.Model):
    national_site_code = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=254)
    country_iso = CountryField(default="PT")
    parish = models.CharField(max_length=254, blank=True)
    location = models.PointField()
    surrounding_polygon = models.PolygonField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):  
        return self.name

class Occurrence(models.Model):
    name = models.CharField(max_length=254)
    acronym = models.CharField(max_length=254, blank=True)
    toponym = models.CharField(max_length=254, blank=True)
    owner = models.CharField(max_length=254, blank=True)
    altitude = models.IntegerField(null=True, blank=True)
    location = models.PointField()
    bounding_polygon = models.PolygonField()
    site = models.ForeignKey(Site, on_delete=models.RESTRICT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=254, blank=True)
    file = models.FileField()
    type = models.CharField(max_length=254) # check data type. Maybe list of types could be a table
    site = models.ManyToManyField()
    occurrence = models.ManyToManyField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.file

class MetricType(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name

class Metric(models.Model):
    type = models.ForeignKey(MetricType, on_delete=models.RESTRICT)
    auto_value = models.FloatField()
    confirmed_value = models.FloatField()
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} ({1})'.format(self.type, self.occurrence)

class AttributeCategory(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name

class AttributeChoice(models.Model):
    category = models.ForeignKey(AttributeCategory, on_delete=models.CASCADE)
    value = models.CharField(max_length=254)

    def __str__(self):
        return self.value

class Attribute(models.Model):
    category = models.ForeignKey(on_delete=models.RESTRICT)
    value = models.ForeignKey(on_delete=models.RESTRICT)
    occurrence = models.ForeignKey(on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1} ({2})'.format(self.category, self.value, self.occurrence)
