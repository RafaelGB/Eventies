from __future__ import unicode_literals
import math
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.template.defaultfilters import slugify
from django.utils.html import mark_safe
from markdown import markdown




from django.contrib.gis.db import models as gisModels
from django.contrib.gis.geos import Point


"""
**********************************************************
                        Geolocation
**********************************************************
"""
class Geolocation(gisModels.Model):
    coordinates = gisModels.PointField(help_text="Para generar el mapa con la localizacion")
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return u"%i" % self.pk


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
                       Detalles
    ---------------------------------------------------------
    
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    """
                       Relaciones oneToMany
    ---------------------------------------------------------
    
    """
    created_by = models.ForeignKey(User, related_name='events')
    """
                       Relaciones onoToOne
    ---------------------------------------------------------

    """    
    geopos_at = models.OneToOneField(
        Geolocation,
        on_delete=models.CASCADE,
        null=True,
    )
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.title

    def for_user(self, user):
        return self.get_query_set().filter(created_by=user)

"""
**********************************************************
                        Photo
**********************************************************
"""
def get_image_filename(instance, filename):
    title = instance.event.pk
    print(title)
    slug = slugify(title)
    print(slug)
    return "Events/%s/%s" % (slug, filename) 

class Photo(models.Model):
    picture = models.ImageField(
            upload_to =get_image_filename,
            default = 'none/no-img.jpg',
            )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.picture.name
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
        return self.name_category