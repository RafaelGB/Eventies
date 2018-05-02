from __future__ import unicode_literals
import math
import os
from django.db import models, transaction
from django.db.models import F , Q 
from django.contrib.gis.measure import D
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from accounts.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import datetime
from django.template.defaultfilters import slugify
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdown import markdown
from django.contrib.gis.db.models.functions import Distance
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db import models as gisModels
from django.utils.text import Truncator

from accounts.models import User


"""
**********************************************************
                        Geolocation
**********************************************************
"""
class Geolocation(gisModels.Model):
    coordinates = gisModels.PointField(null=False, blank=False, srid=4326,help_text="Para generar el mapa con la localizacion")
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return str(self.pk)


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
    """
                       Fechas
    ---------------------------------------------------------
    
    """
    date = models.DateTimeField(default=datetime.now, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    """
                       Relaciones oneToMany
    ---------------------------------------------------------
    
    """
    created_by = models.ForeignKey(User, related_name='events')
    """
                       Relaciones oneToOne
    ---------------------------------------------------------

    """    
    geopos_at = models.OneToOneField(
        Geolocation,
        on_delete=models.CASCADE,
        null=True,
    )
    """
                       Relaciones ManyToMany
    ---------------------------------------------------------
    
    """
    interested_in = models.ManyToManyField(User,related_name='users_interested')
    not_interested_in = models.ManyToManyField(User,related_name='users_not_interested')
    signed_up = models.ManyToManyField(User,related_name='users_assistants')
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.title

    def get_description_as_markdown(self):
        return mark_safe(markdown(self.description, safe_mode='escape'))

    @classmethod
    #Llama a los eventos creados por un usuario en concreto
    def for_user(self, user):
        return self.objects.filter(created_by=user)

    @classmethod
    @transaction.atomic
    #aumenta el contador de visitas en 1
    def increment_view(self,pk):
        self.objects.filter(pk=pk).update(views=F('views')+1)

    @classmethod
    #Busca los eventos que contengan una cadena dada en diferentes campos
    def search_string(self,string):
        return Event.objects.filter(
            Q(title__icontains=string)  | 
            Q(summary__icontains=string))

    @classmethod
    #Busca los eventos que se encuentren en un rango de n metros de la posición actual , ambas pasadas por parametro
    def distance_range(self,location,meters):
        return Event.objects.filter(geopos_at__coordinates__distance_lt=(location, D(m=meters)))#.order_by('-geopos_at__coordinates')

    @classmethod
    #Ordena ,segun la posición actual, los eventos por distancia
    def distance_order(self,location,meters):
        return Event.objects.filter(geopos_at__coordinates__distance_lt=(location, D(m=meters))).annotate(distance=Distance('geopos_at__coordinates', location))

    @classmethod
    #Busca los eventos que contengan una cadena dada en diferentes campos
    def range_prices(self,min_price,max_price):
        return Event.objects.filter(
            Q(budget__lte=max_price) & 
            Q(budget__gte=min_price) )
"""
**********************************************************
                        Photo
**********************************************************
"""
def get_image_filename(instance, filename):
    title = instance.event.pk
    slug = slugify(title)
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
        return str(self.pk)

    @classmethod
    #Devuelve el numero de fotos que tiene un evento
    def number_of_photos_in(self,event):
        return self.objects.filter(event=event).count()

# borra la foto del sistema
def _delete_file(path):
    print(path)
    suffix = "/media/none/no-img.jpg"
    if os.path.isfile(path) and str(path).endswith(suffix):
        os.remove(path)

#trigger que se activa antes de llamar a borrar foto
@receiver(pre_delete, sender=Photo)
def delete_img_pre_delete_post(sender, instance, *args, **kwargs):
    if instance.picture:
        _delete_file(instance.picture.path)
"""
**********************************************************
                        Tag
**********************************************************
"""
class Tag(models.Model):
    name_tag = models.CharField(max_length=25,unique=True)
    """
                       Relaciones ManyToMany
    ---------------------------------------------------------
    
    """
    events_tags = models.ManyToManyField(Event,related_name='tags') #relacion many_to_many con Event
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.name_tag

    @classmethod
    #Llama a las etiquetas asignadas a un evento en concreto
    def for_event(self, event):
        return self.objects.filter(events_tags=event).values_list('name_tag', flat=True)

    @classmethod
    #Llama a las etiquetas asignadas a un evento en concreto
    def count_for_events(self, tag):
        return self.objects.get(name_tag=tag).events_tags.count()
"""
**********************************************************
                        Category
**********************************************************
"""
class Category(models.Model):
    name_category = models.CharField(max_length=20, primary_key=True)
    description = models.TextField(max_length=280)
    photo  = models.ImageField(upload_to='Categories',blank=True, null=True)
    """
                       Relaciones ManyToMany
    ---------------------------------------------------------
    
    """
    events_categories = models.ManyToManyField(Event,related_name='categories',blank=True) 
    user_categories = models.ManyToManyField(User,related_name='preferences',blank=True)
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return self.name_category

    @classmethod
    #Llama a las categorías asignadas a un evento en concreto
    def for_event(self, event):
        return self.objects.filter(events_categories=event).values_list('name_category', flat=True)

    @classmethod
    #Llama a las categorías asignadas a un usuario en concreto
    def for_user(self, user):
        return self.objects.filter(user_categories=user).values_list('name_category', flat=True)

"""
**********************************************************
                        Recommender
**********************************************************
"""
class MyRecommender(models.Model):
    user = models.IntegerField(primary_key=True)
    id_events = ArrayField(models.IntegerField(blank=True),default=list, null=True)
    """
    ==========================================================
                    Servicios de la clase
    ==========================================================

    """
    def __str__(self):
        return str(self.user)

"""
**********************************************************
                      Comentarios
**********************************************************
"""
class Comments(models.Model):
    message = models.TextField(max_length=4000)
    created_into  = models.ForeignKey(Event, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts')
    updated_by = models.ForeignKey(User, null=True, related_name='+')

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))