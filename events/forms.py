from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import BaseFormSet
from mapwidgets.widgets import GooglePointFieldWidget, GoogleStaticMapWidget, GoogleStaticOverlayMapWidget
from .models import Event, Tag, Category, Photo, Geolocation
from datetimewidget.widgets import DateTimeWidget
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
        	'summary',
            'date',
            'description',
        	'budget',
        	'duration'
        ]
        #Cambia el nombre del campo por el que se desea mostrar en html
        labels = {
            'date': _('Fecha'),
            'title': _('Título'),
            'summary': _('Resumen'),
            'budget': _('Precio aproximado'),
            'duration': _('Duración aproximada')  
        }

        widgets = {
            'date': DateTimeWidget(attrs={'id':"id_date"}, usel10n = True, bootstrap_version=3),
            'duration': forms.TextInput(attrs={'placeholder': "ejemplo '52:06:07'  siendo horas:minutos:segundos"})
        
        }
        
class BasePhotoFormSet(BaseFormSet):
    def clean(self):
        """
        COmprueba que no haya 2 fotos con el mismo contenido
        y que todas las fotos tengan contenido.
        """
        if any(self.errors):
            return

        pictures = []
        duplicates = False

        for form in self.forms:

            print("ahora  ",form.cleaned_data)
            if form.cleaned_data:
                picture = form.cleaned_data['picture']

                # comprueba que no contengan el mismo URL
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
            'picture',
        ]

        labels = {
            'picture': _('')
        }