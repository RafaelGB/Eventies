from django import forms
from django.contrib import admin
from django.contrib.gis.db import models
from mapwidgets.widgets import GooglePointFieldWidget, GooglePointFieldInlineWidget, GoogleStaticMapWidget, \
    GoogleStaticOverlayMapWidget

from .models import Event, Tag, Category, Photo, Geolocation


class GeolocationAdminForm(forms.ModelForm):
    class Meta:
        model = Geolocation
        fields = "__all__"
        widgets = {
            'coordinates': GooglePointFieldWidget(settings={"GooglePointFieldWidget": (("zoom", 1),)}),
        }


class GeolocationAdminStaticForm(forms.ModelForm):

    class Meta:
        model = Geolocation
        fields = "__all__"
        widgets = {
            'coordinates': GoogleStaticMapWidget,
        }


class GeolocationAdmin(admin.ModelAdmin):
    list_display = ("coordinates",)


    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            self.form = GeolocationAdminForm
        else:
            self.form = GeolocationAdminStaticForm
        return super(GeolocationAdmin, self).get_form(request, obj, **kwargs)



myModels = [Event,Tag,Category, Photo]

admin.site.register(myModels)
admin.site.register(Geolocation, GeolocationAdmin)
