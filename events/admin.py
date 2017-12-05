from django import forms
from django.contrib import admin
from django.contrib.gis.db import models

from .models import Event, Tag, Category



myModels = [Event,Tag,Category]

admin.site.register(myModels)
