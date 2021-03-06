# Generated by Django 2.2.24 on 2022-07-26 14:43

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
            ],
            options={
                'verbose_name': 'Attribute Category',
                'verbose_name_plural': 'Attribute Categories',
                'db_table': 'attribute_category',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='AttributeChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=254)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.AttributeCategory')),
            ],
            options={
                'verbose_name': 'Attribute Choice',
                'verbose_name_plural': 'Attribute Choices',
                'db_table': 'attribute_choice',
                'ordering': ['category', 'value'],
            },
        ),
        migrations.CreateModel(
            name='MetricType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
            ],
            options={
                'verbose_name': 'Metric Type',
                'verbose_name_plural': 'Metric Types',
                'db_table': 'metric_type',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('national_site_code', models.IntegerField(blank=True, null=True, unique=True)),
                ('country_iso', django_countries.fields.CountryField(default='PT', max_length=2, verbose_name='country')),
                ('parish', models.CharField(blank=True, max_length=254)),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('surrounding_polygon', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Site',
                'verbose_name_plural': 'Sites',
                'db_table': 'site',
                'ordering': ['national_site_code', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Occurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('acronym', models.CharField(blank=True, max_length=254)),
                ('toponym', models.CharField(blank=True, max_length=254)),
                ('owner', models.CharField(blank=True, max_length=254)),
                ('altitude', models.IntegerField(blank=True, null=True)),
                ('position', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('bounding_polygon', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='archaeology.Site')),
            ],
            options={
                'verbose_name': 'Occurrence',
                'verbose_name_plural': 'Occurrences',
                'db_table': 'occurrence',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='automatic value')),
                ('confirmed_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('occurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.Occurrence')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='archaeology.MetricType')),
            ],
            options={
                'verbose_name': 'Metric',
                'verbose_name_plural': 'Metrics',
                'db_table': 'metric',
                'ordering': ['type'],
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254)),
                ('file', models.FileField(upload_to='')),
                ('type', models.CharField(max_length=254)),
                ('upload_date', models.DateField(auto_now_add=True)),
                ('added_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('occurrence', models.ManyToManyField(blank=True, to='archaeology.Occurrence')),
                ('site', models.ManyToManyField(blank=True, to='archaeology.Site')),
            ],
            options={
                'verbose_name': 'File',
                'verbose_name_plural': 'Files',
                'db_table': 'file',
                'ordering': ['-upload_date'],
            },
        ),
        migrations.CreateModel(
            name='AttributeSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.Site')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='archaeology.AttributeChoice')),
            ],
            options={
                'verbose_name': 'Attribute',
                'verbose_name_plural': 'Site Attributes',
                'db_table': 'attribute_site',
                'ordering': ['value__category', 'value'],
            },
        ),
        migrations.CreateModel(
            name='AttributeOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occurrence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='archaeology.Occurrence')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='archaeology.AttributeChoice')),
            ],
            options={
                'verbose_name': 'Attribute',
                'verbose_name_plural': 'Occurrence Attributes',
                'db_table': 'attribute_occurrence',
                'ordering': ['value__category', 'value'],
            },
        ),
        migrations.AddConstraint(
            model_name='site',
            constraint=models.CheckConstraint(check=models.Q(('location__isnull', False), ('surrounding_polygon__isnull', False), _connector='OR'), name='Site_location_and_or_surrounding_polygon'),
        ),
        migrations.AddConstraint(
            model_name='occurrence',
            constraint=models.CheckConstraint(check=models.Q(('position__isnull', False), ('bounding_polygon__isnull', False), _connector='OR'), name='Occurrence_position_and_or_bounding_polygon'),
        ),
    ]
