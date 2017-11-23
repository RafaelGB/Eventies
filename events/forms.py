from django import forms
from .models import Event, Tag, Category

class NewEventForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'De que va la cosa?'}
        ),
        max_length=5000,
        help_text='The max length of the text is 5000.'
    )

    class Meta:
        model = Event
        fields = ['title', 'description' ,'summary' ]