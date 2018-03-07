from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet
from .models import Event, Tag, Category, Photo, Geolocation

from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticMapWidget, GoogleStaticOverlayMapWidget


class GeolocationForm(forms.ModelForm):

    class Meta:
        model = Geolocation
        fields = ("coordinates",)
        labels = {
            'coordinates': _('Coordenadas') 
        }
        widgets = {
            'coordinates': GooglePointFieldWidget
        }

class EventForm(forms.ModelForm):
    description = forms.CharField(
    	label='Descripción',
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'De que va la cosa?'}
        ),
        max_length=5000,
        help_text='maximos caracteres permitidos: 5000.'
    )

    class Meta:
        model = Event

        fields = [
        	'title',
        	'description',
        	'summary',
        	'budget',
        	'duration'
        ]
        #Cambia el nombre del campo por el que se desea mostrar en html
        labels = {
            'title': _('Título'),
            'summary': _('Resumen'),
            'budget': _('Precio aproximado'),
            'duration': _('Duración aproximada')  
        }

        widgets = {
            
        }
class BasePhotoFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two photos have the same content
        and that all photos have content.
        """
        if any(self.errors):
            return

        pictures = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                picture = form.cleaned_data['picture']

                # Check that no two links have the same anchor or URL
                if picture:
                    if picture in pictures:
                        duplicates = True
                    pictures.append(picture)


                if duplicates:
                    raise forms.ValidationError(
                        'La foto esta duplicada',
                        code='duplicate_photo'
                    )

class PhotoForm(forms.ModelForm):
   
    class Meta:
        model = Photo

        fields = [
            'picture'
        ]

        labels = {
            'picture': _('')
        }