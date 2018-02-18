# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-21 11:57
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_city_district'),
    ]

    operations = [
        migrations.CreateModel(
            name='Geolocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(help_text='Para generar el mapa con la localizacion', srid=4326)),
                ('city_hall', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.RemoveField(
            model_name='district',
            name='city',
        ),
        migrations.DeleteModel(
            name='City',
        ),
        migrations.DeleteModel(
            name='District',
        ),
        migrations.AddField(
            model_name='event',
            name='geopos_at',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='events.Geolocation'),
        ),
    ]