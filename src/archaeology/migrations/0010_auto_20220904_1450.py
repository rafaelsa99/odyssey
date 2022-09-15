# Generated by Django 2.2.24 on 2022-09-04 14:50

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0068_auto_20220403_1334'),
        ('archaeology', '0009_auto_20220806_1646'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='id',
        ),
        migrations.AddField(
            model_name='site',
            name='resourcebase_ptr',
            field=models.OneToOneField(auto_created=True, default=None, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base.ResourceBase'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attributecategory',
            name='name',
            field=models.CharField(max_length=254, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='attributechoice',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.AttributeCategory', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='attributechoice',
            name='value',
            field=models.CharField(max_length=254, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='metric',
            name='confirmed_value',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Confirmed Value'),
        ),
        migrations.AlterField(
            model_name='metric',
            name='occurrence',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.Occurrence', verbose_name='Occurrence'),
        ),
        migrations.AlterField(
            model_name='metric',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='archaeology.MetricType', verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='metrictype',
            name='name',
            field=models.CharField(max_length=254, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='acronym',
            field=models.CharField(blank=True, max_length=254, verbose_name='Acronym'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='added_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Added by'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='altitude',
            field=models.IntegerField(blank=True, null=True, verbose_name='Altitude'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='bounding_polygon',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Bounding Polygon'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='designation',
            field=models.CharField(max_length=254, verbose_name='Designation'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='owner',
            field=models.CharField(blank=True, max_length=254, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='position',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Position'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.Site', verbose_name='Site'),
        ),
        migrations.AlterField(
            model_name='occurrence',
            name='toponym',
            field=models.CharField(blank=True, max_length=254, verbose_name='Toponym'),
        ),
        migrations.AlterField(
            model_name='site',
            name='added_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Added by'),
        ),
        migrations.AlterField(
            model_name='site',
            name='attribute_site',
            field=models.ManyToManyField(blank=True, to='archaeology.AttributeChoice', verbose_name='attributes'),
        ),
        migrations.AlterField(
            model_name='site',
            name='country_iso',
            field=django_countries.fields.CountryField(default='PT', max_length=2, verbose_name='Country'),
        ),
        migrations.AlterField(
            model_name='site',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(max_length=254, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='site',
            name='national_site_code',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='National Site Code'),
        ),
        migrations.AlterField(
            model_name='site',
            name='parish',
            field=models.CharField(blank=True, max_length=254, verbose_name='Parish'),
        ),
        migrations.AlterField(
            model_name='site',
            name='surrounding_polygon',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Surrounding Polygon'),
        ),
    ]
