from django.contrib.gis.db import models
from django_countries.fields import CountryField

# Create your models here.
class Site(models.Model):
    national_site_code = models.IntegerField()
    name = models.CharField()
    country_iso = CountryField()
    parish = models.CharField()
    location = models.PointField()
    surrounding_polygon = models.PolygonField()
    user = models.ForeignKey()

class Occurrence(models.Model):
    name = models.CharField()
    acronym = models.CharField()
    toponym = models.CharField()
    owner = models.CharField()
    altitude = models.IntegerField()
    location = models.PointField()
    bounding_polygon = models.PolygonField()
    site = models.ForeignKey()
    user = models.ForeignKey()

class File(models.Model):
    name = models.CharField()
    file = models.FileField()
    type = models.CharField() # check data type. Maybe list of types could be a table
    site = models.ManyToManyField()
    occurrence = models.ManyToManyField()
    user = models.ForeignKey()

class MetricType(models.Model):
    name = models.CharField()

class Metric(models.Model):
    type = models.ForeignKey()
    auto_value = models.FloatField()
    confirmed_value = models.FloatField()
    occurrence = models.ForeignKey()

class AttributeCategory(models.Model):
    name = models.CharField()

class AttributeValue(models.Model):
    category = models.ForeignKey()
    value = models.CharField()

class Attribute(models.Model):
    category = models.ForeignKey()
    value = models.ForeignKey()
    occurrence = models.ForeignKey()
