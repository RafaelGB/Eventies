# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-14 13:06
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(help_text='To generate the map for your location', srid=4326)),
                ('city_hall', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='To generate the map for your location', srid=4326)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.City')),
            ],
        ),
    ]