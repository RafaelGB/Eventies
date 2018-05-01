from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import datetime
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'birth_date': _('Edad') 
        }

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("Esta cuenta esta inactiva"),
                code='inactive',
            )

class UserForm(forms.ModelForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('first_name','last_name','email', 'bio', 'birth_date', 'location','avatar')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'first_name': _('Nombre'),
            'last_name': _('Apellidos'),
            'bio': _('Breve descripcion tuya'),
            'birth_date': _('Edad'),
            'location': _('Ciudad'),
            'avatar': _('Foto de avatar')
        }