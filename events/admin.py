from django import forms
from django.contrib import admin
from django.contrib.gis.db import models

from .models import Event, Tag, Category, Photo



myModels = [Event,Tag,Category, Photo]

admin.site.register(myModels)
