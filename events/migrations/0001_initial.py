# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-10 19:00
from __future__ import unicode_literals

import datetime
from decimal import Decimal
from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import events.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name_category', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('description', models.TextField(max_length=280)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='Categories')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('description', models.TextField(max_length=5000)),
                ('summary', models.CharField(max_length=50)),
                ('budget', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('duration', models.DurationField()),
                ('views', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Geolocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(help_text='Para generar el mapa con la localizacion', srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(default='none/no-img.jpg', upload_to=events.models.get_image_filename)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_tag', models.CharField(max_length=25, unique=True)),
                ('events_tags', models.ManyToManyField(related_name='tags', to='events.Event')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='geopos_at',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='events.Geolocation'),
        ),
        migrations.AddField(
            model_name='event',
            name='interested_in',
            field=models.ManyToManyField(related_name='users_interested', to=settings.AUTH_USER_MODEL, verbose_name='events_interested'),
        ),
        migrations.AddField(
            model_name='event',
            name='not_interested_in',
            field=models.ManyToManyField(related_name='users_not_interested', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='signed_up',
            field=models.ManyToManyField(related_name='users_assistants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='events_categories',
            field=models.ManyToManyField(blank=True, related_name='categories', to='events.Event'),
        ),
        migrations.AddField(
            model_name='category',
            name='user_categories',
            field=models.ManyToManyField(blank=True, related_name='preferences', to=settings.AUTH_USER_MODEL),
        ),
    ]
