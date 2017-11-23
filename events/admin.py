from django.contrib import admin
from django.forms.widgets import TextInput
from django_google_maps.widgets import GoogleMapsAddressWidget
from django_google_maps.fields import AddressField, GeoLocationField
from .models import Event, Tag, Category

class AddressModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        AddressField: {'widget': GoogleMapsAddressWidget},
        GeoLocationField: {'widget': TextInput(attrs={'readonly': 'readonly'})},
    }

myModels = [Event,Tag,Category]

admin.site.register(myModels, AddressModelAdmin)