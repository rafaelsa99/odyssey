from cProfile import label
from django.contrib.gis import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.contrib.gis.geos import Point
from leaflet.forms.widgets import LeafletWidget
from .models import Occurrence, Site    

class AtLeastOneFormSet(BaseInlineFormSet):
    def clean(self):
        super(AtLeastOneFormSet, self).clean()
        non_empty_forms = 0
        for form in self:
            if form.cleaned_data:
                non_empty_forms += 1
        if non_empty_forms - len(self.deleted_forms) < 1:
            raise ValidationError("Please fill at least one form.")

class SiteForm(forms.ModelForm):
    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        required=False,
        help_text="Enter coordinates as an alternative to selecting a point on the map."
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        required=False,
    )

    class Meta(object):
        model = Site
        widgets = {
            'location': LeafletWidget(),
            'surrounding_polygon': LeafletWidget(),
        }
        exclude = ['added_by',]
    
    field_order = ['name', 'national_site_code', 'country_iso', 'parish', 'location', 'latitude', 'longitude', 'surrounding_polygon']

    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        coordinates = self.initial.get("location", None)
        if isinstance(coordinates, Point):
            self.initial["longitude"], self.initial["latitude"] = coordinates.tuple

    def clean(self):
        data = super(SiteForm, self).clean()
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            lat, lng = data.pop("latitude", None), data.pop("longitude", None)
            if lat and lng:
                data["location"] = Point(lng, lat, srid=4326)
        return data

class OccurrenceForm(forms.ModelForm):
    latitude_occurrence = forms.FloatField(
        label="Latitude",
        min_value=-90,
        max_value=90,
        required=False,
        help_text="Enter coordinates as an alternative to selecting a point on the map."
    )
    longitude_occurrence = forms.FloatField(
        label="Longitude",
        min_value=-180,
        max_value=180,
        required=False,
    )

    class Meta(object):
        model = Occurrence
        widgets = {
            'position': LeafletWidget(),
            'bounding_polygon': LeafletWidget(),
        }
        exclude = ['added_by', 'site',]
    
    field_order = ['designation', 'acronym', 'toponym', 'owner', 'altitude', 'position', 'latitude_occurrence', 'longitude_occurrence', 'bounding_polygon']

    def __init__(self, *args, **kwargs):
        super(OccurrenceForm, self).__init__(*args, **kwargs)
        coordinates = self.initial.get("position", None)
        if isinstance(coordinates, Point):
            self.initial["longitude_occurrence"], self.initial["latitude_occurrence"] = coordinates.tuple

    def clean(self):
        data = super(OccurrenceForm, self).clean()
        if "latitude_occurrence" in self.changed_data or "longitude_occurrence" in self.changed_data:
            lat, lng = data.pop("latitude_occurrence", None), data.pop("longitude_occurrence", None)
            if lat and lng:
                data["position"] = Point(lng, lat, srid=4326)
        return data

class SiteFormAdmin(forms.ModelForm):
    latitude = forms.FloatField(
        min_value=-90,
        max_value=90,
        required=False,
        help_text="Enter coordinates as an alternative to selecting a point on the map."
    )
    longitude = forms.FloatField(
        min_value=-180,
        max_value=180,
        required=False,
    )

    class Meta(object):
        model = Site
        exclude = []

    def __init__(self, *args, **kwargs):
        super(SiteFormAdmin, self).__init__(*args, **kwargs)
        coordinates = self.initial.get("location", None)
        if isinstance(coordinates, Point):
            self.initial["longitude"], self.initial["latitude"] = coordinates.tuple

    def clean(self):
        data = super(SiteFormAdmin, self).clean()
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            lat, lng = data.pop("latitude", None), data.pop("longitude", None)
            if lat and lng:
                data["location"] = Point(lng, lat, srid=4326)
        return data

class OccurrenceFormAdmin(forms.ModelForm):
    latitude_occurrence = forms.FloatField(
        label="Latitude",
        min_value=-90,
        max_value=90,
        required=False,
        help_text="Enter coordinates as an alternative to selecting a point on the map."
    )
    longitude_occurrence = forms.FloatField(
        label="Longitude",
        min_value=-180,
        max_value=180,
        required=False,
    )

    class Meta(object):
        model = Occurrence
        exclude = []

    def __init__(self, *args, **kwargs):
        super(OccurrenceFormAdmin, self).__init__(*args, **kwargs)
        coordinates = self.initial.get("position", None)
        if isinstance(coordinates, Point):
            self.initial["longitude"], self.initial["latitude"] = coordinates.tuple

    def clean(self):
        data = super(OccurrenceFormAdmin, self).clean()
        if "latitude" in self.changed_data or "longitude" in self.changed_data:
            lat, lng = data.pop("latitude", None), data.pop("longitude", None)
            if lat and lng:
                data["position"] = Point(lng, lat, srid=4326)
        return data