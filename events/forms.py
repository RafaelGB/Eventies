from django import forms
from django.utils.translation import ugettext_lazy as _
from photologue.models import Gallery , Photo
from .models import Event, Tag, Category

class EventForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        label='Categorías'
        )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label='Tags'
        )

    description = forms.CharField(
    	label='Descripción',
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'De que va la cosa?'}
        ),
        max_length=5000,
        help_text='The max length of the text is 5000.'
    )

    gallery = forms.
    class Meta:
        model = Event

        fields = [
        	'title',
        	'description',
        	'summary',
        	'budget',
        	'duration',
            'categories',
            'tags',
            'gallery'
        ]
        #Cambia el nombre del campo por el que se desea mostrar en html
        labels = {
            'title': _('Título'),
            'summary': _('Resumen'),
            'budget': _('Precio aproximado'),
            'duration': _('Duración aproximada')
        }
