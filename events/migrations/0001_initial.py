# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-10 17:17
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
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
                ('assistants', models.PositiveIntegerField(default=0)),
                ('interested', models.PositiveIntegerField(default=0)),
                ('score', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(default='media/None/no-img.jpg', upload_to=events.models.get_image_filename)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name_tag', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('events_tags', models.ManyToManyField(to='events.Event')),
            ],
        ),
        migrations.AddField(
            model_name='category',
            name='events_categories',
            field=models.ManyToManyField(to='events.Event'),
        ),
    ]
