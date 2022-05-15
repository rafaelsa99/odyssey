from django.contrib.gis.db import models
from django.conf import settings
from django_countries.fields import CountryField

# Create your models here.
class Site(models.Model):
    national_site_code = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=254)
    country_iso = CountryField(verbose_name="country", default="PT")
    parish = models.CharField(max_length=254, blank=True)
    location = models.PointField(null=True, blank=True)
    surrounding_polygon = models.PolygonField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):  
        return self.name

    class Meta:
        db_table = 'site'
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        ordering = ['national_site_code', 'name']
        # Checks if at least one of the spatial fields is filled in
        constraints = [
            models.CheckConstraint(
                name="%App_1s_%Sites_location_and_or_surrounding_polygon",
                check=(
                    models.Q(location__isnull=False)
                    | models.Q(surrounding_polygon__isnull=False)
                ),
            )
        ]

class Occurrence(models.Model):
    name = models.CharField(max_length=254)
    acronym = models.CharField(max_length=254, blank=True)
    toponym = models.CharField(max_length=254, blank=True)
    owner = models.CharField(max_length=254, blank=True)
    altitude = models.IntegerField(null=True, blank=True)
    location = models.PointField(null=True, blank=True)
    bounding_polygon = models.PolygonField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.RESTRICT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'occurrence'
        verbose_name = "Occurrence"
        verbose_name_plural = "Occurrences"
        ordering = ['name']
        # Checks if at least one of the spatial fields is filled in
        constraints = [
            models.CheckConstraint(
                name="%App_1s_%Occurrence_location_and_or_bounding_polygon",
                check=(
                    models.Q(location__isnull=False)
                    | models.Q(bounding_polygon__isnull=False)
                ),
            )
        ]

class File(models.Model):
    name = models.CharField(max_length=254, blank=True)
    file = models.FileField()
    type = models.CharField(max_length=254) # check data type. Maybe list of types could be a table
    creation_date = models.DateTimeField(auto_now_add=True)
    site = models.ManyToManyField()
    occurrence = models.ManyToManyField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.file

    class Meta:
        db_table = 'file'
        verbose_name = "File"
        verbose_name_plural = "Files"
        ordering = ['-creation_date']

class MetricType(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'metric_type'
        verbose_name = "Metric Type"
        verbose_name_plural = "Metric Types"
        ordering = ['name']

class Metric(models.Model):
    type = models.ForeignKey(MetricType, on_delete=models.RESTRICT)
    auto_value = models.FloatField(verbose_name="automatic value")
    confirmed_value = models.FloatField()
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)

    def __str__(self):
        return '{0} ({1})'.format(self.type, self.occurrence)

    class Meta:
        db_table = 'metric'
        verbose_name = "Metric"
        verbose_name_plural = "Metrics"
        ordering = ['type']

class AttributeCategory(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute_category'
        verbose_name = "Attribute Category"
        verbose_name_plural = "Attribute Categories"
        ordering = ['name']

class AttributeChoice(models.Model):
    category = models.ForeignKey(AttributeCategory, on_delete=models.CASCADE)
    value = models.CharField(max_length=254)

    def __str__(self):
        return self.value

    class Meta:
        db_table = 'attribute_choice'
        verbose_name = "Attribute Choice"
        verbose_name_plural = "Attribute Choices"
        ordering = ['value']

class Attribute(models.Model):
    category = models.ForeignKey(on_delete=models.RESTRICT)
    value = models.ForeignKey(on_delete=models.RESTRICT)
    occurrence = models.ForeignKey(on_delete=models.CASCADE)

    def __str__(self):
        return '{0}: {1} ({2})'.format(self.category, self.value, self.occurrence)

    class Meta:
        db_table = 'attribute'
        verbose_name = "Attribute"
        verbose_name_plural = "Attributes"
        ordering = ['category']