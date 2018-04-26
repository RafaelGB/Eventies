# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-25 17:00
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyRecommender',
            fields=[
                ('user', models.IntegerField(primary_key=True, serialize=False)),
                ('id_events', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), default=list, null=True, size=None)),
            ],
        ),
        migrations.AlterField(
            model_name='event',
            name='interested_in',
            field=models.ManyToManyField(related_name='users_interested', to=settings.AUTH_USER_MODEL),
        ),
    ]