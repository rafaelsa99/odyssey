# Create your models here.
from django.contrib.gis.db import models
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse
from django_countries.fields import CountryField
from geonode.documents.models import Document
from geonode.layers.models import LayerFile
from django.utils.translation import ugettext_lazy

# Create your models here.
class AlgorithmExecution(models.Model):
    """Model representing an execution of the automatic identification algorithm."""
    
    STATUS_CHOICES = (
    ("E", ugettext_lazy("Executing")),
    ("F", ugettext_lazy("Finished")))

    PURPOSE_CHOICES = (
    ("training", ugettext_lazy("Training")),
    ("inference", ugettext_lazy("Inference")))

    name = models.CharField(max_length=254, verbose_name=ugettext_lazy('Name'))
    executed_at = models.DateTimeField(auto_now_add = True, verbose_name=ugettext_lazy('Executed at'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="E", verbose_name=ugettext_lazy('Status'))
    purpose = models.CharField(max_length=15, choices=PURPOSE_CHOICES, default="inference", verbose_name=ugettext_lazy('Purpose'))
    executed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name=ugettext_lazy('Executed by'))
    layers_used = models.ManyToManyField(LayerFile, verbose_name=ugettext_lazy('Layers Used'))
    aoi = models.PolygonField(verbose_name=ugettext_lazy('Area of Interest'))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular archaeological site."""
        return reverse('view_execution', args=[str(self.id)])

    class Meta:
        db_table = 'algorithm_execution'
        verbose_name = ugettext_lazy('Algorithm Execution')
        verbose_name_plural = ugettext_lazy('Algorithm Executions')
        ordering = ['-executed_at']

class AttributeCategory(models.Model):
    """Model representing a category for an attribute (e.g. chronology, geological context)."""
    name = models.CharField(max_length=254, verbose_name=ugettext_lazy('Name'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute_category'
        verbose_name = ugettext_lazy('Attribute Category')
        verbose_name_plural = ugettext_lazy('Attribute Categories')
        ordering = ['name']

class AttributeChoice(models.Model):
    """Model to represent a choice option for an attribute category (e.g. for Chronology: neolithic, full bronze)."""
    category = models.ForeignKey(AttributeCategory, on_delete=models.CASCADE, verbose_name=ugettext_lazy('Category'))
    value = models.CharField(max_length=254, verbose_name=ugettext_lazy('Value'))

    def __str__(self):
        return '{0}: {1}'.format(self.category, self.value)

    class Meta:
        db_table = 'attribute_choice'
        verbose_name = ugettext_lazy('Attribute Choice')
        verbose_name_plural = ugettext_lazy('Attribute Choices')
        ordering = ['category', 'value']

class Site(models.Model):
    """Model representing an archaeological site."""

    STATE_CHOICES = (
        ("N", ugettext_lazy("Not Verified")),
        ("V", ugettext_lazy("Verified")))

    name = models.CharField(max_length=254, verbose_name=ugettext_lazy('Name'))
    national_site_code = models.IntegerField(null=True, blank=True, unique=True, verbose_name=ugettext_lazy('National Site Code'))
    country_iso = CountryField(verbose_name=ugettext_lazy('Country'), default="PT")
    parish = models.CharField(max_length=254, blank=True, verbose_name=ugettext_lazy('Parish'))
    location = models.PointField(null=True, blank=True, verbose_name=ugettext_lazy('Location'))
    surrounding_polygon = models.PolygonField(null=True, blank=True, verbose_name=ugettext_lazy('Surrounding Polygon'))
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name=ugettext_lazy('Added by'))
    document_site = models.ManyToManyField(Document, blank=True, verbose_name=ugettext_lazy('documents'))
    attribute_site = models.ManyToManyField(AttributeChoice, blank=True, verbose_name=ugettext_lazy('attributes'))
    created_by_execution = models.ForeignKey(AlgorithmExecution, null=True, on_delete=models.SET_NULL, default=None, verbose_name=ugettext_lazy('Created by execution'))
    status_site = models.CharField(max_length=1, choices=STATE_CHOICES, default="V", verbose_name=ugettext_lazy('Status'))

    def __str__(self):  
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular archaeological site."""
        return reverse('view_site', args=[str(self.id)])

    def clean(self):
        # Checks if at least one of the spatial fields is filled in (Model Level)
        if not self.location and not self.surrounding_polygon:
            raise ValidationError(ugettext_lazy('At least one of the spatial fields (point or polygon) is required.'))
    
    class Meta:
        db_table = 'site'
        verbose_name = ugettext_lazy('Site')
        verbose_name_plural = ugettext_lazy('Sites')
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

    STATE_CHOICES_OCCURRENCE = (
        ("N", ugettext_lazy("Not Verified")),
        ("V", ugettext_lazy("Verified")),
        ("T", ugettext_lazy("Verified - True Positive")),
        ("F", ugettext_lazy("Verified - False Positive")))

    designation = models.CharField(max_length=254, verbose_name=ugettext_lazy('Designation'))
    acronym = models.CharField(max_length=254, blank=True, verbose_name=ugettext_lazy('Acronym'))
    toponym = models.CharField(max_length=254, blank=True, verbose_name=ugettext_lazy('Toponym'))
    owner = models.CharField(max_length=254, blank=True, verbose_name=ugettext_lazy('Owner'))
    altitude = models.IntegerField(null=True, blank=True, verbose_name=ugettext_lazy('Altitude'))
    position = models.PointField(null=True, blank=True, verbose_name=ugettext_lazy('Position'))
    bounding_polygon = models.PolygonField(null=True, blank=True, verbose_name=ugettext_lazy('Bounding Polygon'))
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name=ugettext_lazy('Site'))
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name=ugettext_lazy('Added by'))
    document_occurrence = models.ManyToManyField(Document, blank=True, verbose_name=ugettext_lazy('documents'))
    attribute_occurrence = models.ManyToManyField(AttributeChoice, blank=True, verbose_name=ugettext_lazy('attributes'))
    algorithm_execution = models.ForeignKey(AlgorithmExecution, null=True, on_delete=models.SET_NULL, default=None, verbose_name=ugettext_lazy('Created by execution'))
    status_occurrence = models.CharField(max_length=1, choices=STATE_CHOICES_OCCURRENCE, default="V", verbose_name=ugettext_lazy('Status'))

    def __str__(self):
        return self.designation

    def clean(self):
        # Checks if at least one of the spatial fields is filled in (Model Level)
        if not self.position and not self.bounding_polygon:
            raise ValidationError(ugettext_lazy('At least one of the spatial fields (point or polygon) is required.'))

    def get_absolute_url(self):
        """Returns the url to access a particular occurrence."""
        return reverse('view_occurrence', args=[str(self.id)])

    class Meta:
        db_table = 'occurrence'
        verbose_name = ugettext_lazy('Occurrence')
        verbose_name_plural = ugettext_lazy('Occurrences')
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
    name = models.CharField(max_length=254, verbose_name=ugettext_lazy('Name'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'metric_type'
        verbose_name = ugettext_lazy('Metric Type')
        verbose_name_plural = ugettext_lazy('Metric Types')
        ordering = ['name']

class Metric(models.Model):
    """Model representing a metric of an occurrence."""
    type = models.ForeignKey(MetricType, on_delete=models.PROTECT, verbose_name=ugettext_lazy('Type'))
    occurrence = models.ForeignKey(Occurrence, on_delete=models.CASCADE, verbose_name=ugettext_lazy('Occurrence'))
    auto_value = models.DecimalField(verbose_name=ugettext_lazy('automatic value'), max_digits= 10, decimal_places=2, null=True, blank=True)
    confirmed_value = models.DecimalField(max_digits= 10, decimal_places=2, null=True, blank=True, verbose_name=ugettext_lazy('Confirmed Value'))
    unit_measurement = models.CharField(verbose_name=ugettext_lazy('unit of measurement'), max_length=50, null=True, blank=True)

    def __str__(self):
        if self.confirmed_value:
            return '{0} ({1}) = {2} {3}'.format(self.type, self.occurrence, self.confirmed_value, self.unit_measurement)
        elif self.auto_value:
            return '{0} ({1}) = {2} {3}'.format(self.type, self.occurrence, self.auto_value, self.unit_measurement)
        else:
            return '{0} ({1})'.format(self.type, self.occurrence)

    class Meta:
        db_table = 'metric'
        verbose_name = ugettext_lazy('Metric')
        verbose_name_plural = ugettext_lazy('Metrics')
        ordering = ['type']
