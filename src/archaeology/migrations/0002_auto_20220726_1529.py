# Generated by Django 2.2.24 on 2022-07-26 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archaeology', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='occurrence',
            options={'ordering': ['designation'], 'verbose_name': 'Occurrence', 'verbose_name_plural': 'Occurrences'},
        ),
        migrations.RenameField(
            model_name='occurrence',
            old_name='name',
            new_name='designation',
        ),
    ]
