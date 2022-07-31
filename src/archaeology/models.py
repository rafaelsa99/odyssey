# Create your models here.
from django.contrib.gis.db import models
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse
from django_countries.fields import CountryField
from geonode.documents.models import Document

# Create your models here.
class AttributeCategory(models.Model):
    """Model representing a category for an attribute (e.g. chronology, geological context)."""
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute_category'
        verbose_name = "Attribute Category"
        verbose_name_plural = "Attribute Categories"
        ordering = ['name']

class AttributeChoice(models.Model):
    """Model to represent a choice option for an attribute category (e.g. for Chronology: neolithic, full bronze)."""
    category = models.ForeignKey(AttributeCategory, on_delete=models.CASCADE)
    value = models.CharField(max_length=254)

    def __str__(self):
        return '{0}: {1}'.format(self.category, self.value)

    class Meta:
        db_table = 'attribute_choice'
        verbose_name = "Attribute Choice"
        verbose_name_plural = "Attribute Choices"
        ordering = ['category', 'value']

class Site(models.Model):
    """Model representing an archaeological site."""
    name = models.CharField(max_length=254)
    national_site_code = models.IntegerField(null=True, blank=True, unique=True)
    country_iso = CountryField(verbose_name="country", default="PT")
    parish = models.CharField(max_length=254, blank=True)
    location = models.PointField(null=True, blank=True)
    surrounding_polygon = models.PolygonField(null=True, blank=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    document = models.ManyToManyField(AttributeChoice, blank=True)
    attribute = models.ManyToManyField(Document, blank=True)

    def __str__(self):  
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular archaeological site."""
        return reverse('update_site', args=[str(self.id)])

    def clean(self):
        # Checks if at least one of the spatial fields is filled in (Model Level)
        if not self.location and not self.surrounding_polygon:
            raise ValidationError('At least one of the spatial fields (point or polygon) is required.')
    
    class Meta:
        db_table = 'site'
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        ordering = ['national_site_code', 'name']
        # Checks if at least one of the spatial fields is filled in (DB Level)
        constraints = [
            models.CheckConstraint(
                name="Site_location_and_or_surrounding_polygon",
                check=(
                    models.Q(location__isnull=False)
                    | models.Q(surrounding_polygon__isnull=False)
                ),
            )
        ]

class Occurrence(models.Model):
    """Model representing an archaeological occurrence within a site."""
    designation = models.CharField(max_length=254)
    acronym = models.CharField(max_length=254, blank=True)
    toponym = models.CharField(max_length=254, blank=True)
    owner = models.CharField(max_length=254, blank=True)
    altitude = models.IntegerField(null=True, blank=True)
    position = models.PointField(null=True, blank=True)
    bounding_polygon = models.PolygonField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    document = models.ManyToManyField(AttributeChoice, blank=True)
    attribute = models.ManyToManyField(Document, blank=True)

    def __str__(self):
        return self.designation

    def clean(self):
        # Checks if at least one of the spatial fields is filled in (Model Level)
        if not self.position and not self.bounding_polygon:
            raise ValidationError('At least one of the spatial fields (point or polygon) is required.')

    def get_absolute_url(self):
        """Returns the url to access a particular occurrence."""
        return reverse('update_occurrence', args=[str(self.id)])

    class Meta:
        db_table = 'occurrence'
        verbose_name = "Occurrence"
        verbose_name_plural = "Occurrences"
        ordering = ['designation']
        # Checks if at least one of the spatial fields is filled in (DB Level)
        constraints = [
            models.CheckConstraint(
                name="Occurrence_position_and_or_bounding_polygon",
                check=(
                    models.Q(position__isnull=False)
                    | models.Q(bounding_polygon__isnull=False)
                ),
            )
        ]

class MetricType(models.Model):
    """Model representing a type of metric (e.g. area, width, height)."""
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'metric_type'
        verbose_name = "Metric Type"
        verbose_name_plural = "Metric Types"
        ordering = ['name']

class Metric(models.Model):
    """Model representing a metric of an occurrence."""
    type = models.ForeignKey(MetricType, on_delete=models.PROTECT)
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE)
    auto_value = models.DecimalField(verbose_name="automatic value", max_digits= 10, decimal_places=2, null=True, blank=True)
    confirmed_value = models.DecimalField(max_digits= 10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return '{0} ({1})'.format(self.type, self.occurrence)

    class Meta:
        db_table = 'metric'
        verbose_name = "Metric"
        verbose_name_plural = "Metrics"
        ordering = ['type']
