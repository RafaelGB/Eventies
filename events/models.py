import math
from django.db import models
from django.contrib.auth.models import User
from django_google_maps import fields as map_fields
from photologue.models import Gallery
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils.text import Truncator
from django.utils.html import mark_safe
from markdown import markdown

"""
**********************************************************
                        Event
**********************************************************
"""
class Event(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=5000)
    summary = models.CharField(max_length=50)
    budget = models.DecimalField(null=True, max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], default=Decimal(0.00))
    """
                    duracion y como usarla
    ---------------------------------------------------------
    --  import datetime
    --
    --  my_model = MyModel()
    --  my_model.duration = datetime.timedelta(days=x,hours=y,minutes=z)
    ---------------------------------------------------------
    """
    duration = models.DurationField()
    """
                Contadores creados por defecto
    ---------------------------------------------------------

    """
    views = models.PositiveIntegerField(default=0)
    assistants = models.PositiveIntegerField(default=0)
    interested = models.PositiveIntegerField(default=0)
    score = models.IntegerField(default=0)
    """
                direccion con google maps API
    ---------------------------------------------------------

    """
    address = map_fields.AddressField(max_length=200)
    geolocation = map_fields.GeoLocationField(max_length=100)
    """
                       Galeria photologue
    ---------------------------------------------------------
    
    """
    gallery = models.OneToOneField(Gallery, related_name='extended')
    #autogestionado
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='events')
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.title

"""
**********************************************************
                        Tag
**********************************************************
"""
class Tag(models.Model):
    name_tag = models.CharField(max_length=15, primary_key=True)
    events_tags = models.ManyToManyField(Event) #relacion many_to_many con Event
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.name_tag


"""
**********************************************************
                        Category
**********************************************************
"""
class Category(models.Model):
    name_category = models.CharField(max_length=20, primary_key=True)
    description = models.TextField(max_length=280)
    events_categories = models.ManyToManyField(Event) #relacion many_to_many con Event
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.name_Category