from django.db.models import Count
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render, reverse
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.forms.formsets import formset_factory
from django.contrib.gis.geos import *
from django.contrib.gis.measure import D
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Event, Tag, Category, Photo
from .forms import EventForm, PhotoForm, BasePhotoFormSet, GeolocationCreateForm

def HomeView(request):
    return render(request, 'home.html')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return HttpResponse(ip)

"""
**********************************************************
        Carga los valores de un evento concreto
**********************************************************
"""
class EventObjectView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'eventDetails.html'
    """
	----------------------------------------------------------
        funciones de la clase
	----------------------------------------------------------
	"""
    def get_context_data(self, **kwargs):
        context = super(EventObjectView, self).get_context_data(**kwargs)
        return context
"""
**********************************************************
        Carga los valores de un evento concreto
**********************************************************
"""
class EventFilterView(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'eventFilter.html'

    paginate_by = 8
    """
	----------------------------------------------------------
        funciones de la clase
	----------------------------------------------------------
	"""
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EventFilterView, self).get_context_data(**kwargs)
        return context


    def get_queryset(self):
        # Comprobamos si hay variable get de búsqueda y si no está vacía
        if self.kwargs['type'] == 'search':
            contains = self.request.GET['search']
            queryset = (
                Event.objects.filter(title__icontains=contains) | 
                Event.objects.filter(summary__icontains=contains)
                )
        elif self.kwargs['type'] == 'own':
            queryset = (
                Event.objects.filter(created_by=self.request.user.pk)
                )
            """
        elif self.kwargs['type'] == 'distance':
            queryset = (
                Event.objects.filter(geopos_at__distance_lte=(ref_location, D(m=distance))).distance(ref_location).order_by('distance')
                )   
            """        
        else:
            queryset = Event.objects.all()
        return queryset

@method_decorator(login_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    template_name = 'update_event.html'
    context_object_name = 'event'
    form_class = EventForm
    #formset_class = formset_factory(PhotoForm, formset=BasePhotoFormSet, can_delete=True)
    """
    ----------------------------------------------------------
        funciones de la clase
    ----------------------------------------------------------
    """
    def get_context_data(self, **kwargs):
        context = super(EventUpdateView, self).get_context_data(**kwargs)
        if all(['form' not in context,context['form'].data]):
            context['form'] = self.form_class(instance=self.object)
        #if 'formset' not in context:
        #context['formset'] = self.formset_class(initial=[{'pk': x.pk} for x in Photo.objects.filter(event=self.object)])
        return context

    def get(self, request, *args, **kwargs):
        super(EventUpdateView, self).get(request, *args, **kwargs)
        form = self.form_class
        #formset = self.formset_class
        return self.render_to_response(self.get_context_data(
            object=self.object, form=form))#, formset=formset

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        #formset = self.formset_class(request.POST or None, request.FILES or None)
        if all([form.is_valid(),formset.is_valid()]):
            self.object.title = form.cleaned_data['title']
            self.object.description = form.cleaned_data['description']
            self.object.summary = form.cleaned_data['summary']
            self.object.budget = form.cleaned_data['budget']
            self.object.duration = form.cleaned_data['duration']
            """
            'categories',
            'tags'
            """
            self.object.updated_at = timezone.now()
            self.object.save()
            print(formset.as_table())
            """
            instances = formset.save(commit=False)
            for obj in instances.deleted_objects:
                obj.delete()
            """
            return redirect('eventDetails', pk=self.object.pk)  
        else:
            return self.render_to_response(
              self.get_context_data(form=form, formset=formset))

@login_required
def NewEvent(request):
     # Create the formset, specifying the form and formset we want to use.
    PhotoFormSet = formset_factory(PhotoForm, formset=BasePhotoFormSet)
    if request.method == 'POST':
        form = EventForm(request.POST)
        formset = PhotoFormSet(request.POST or None, request.FILES or None)
        if all([form.is_valid(),formset.is_valid(),formGeo.is_valid()]):
            myGeo = formGeo.save(commit=False)
            event = form.save(commit=False)
            event.geopos_at = myGeo
            event.created_by = request.user
            event.save()
            myGeo.save()
            for subformset in formset.cleaned_data:
                photo = subformset.get('picture')
                newphoto = Photo(picture=photo,event=event)  
                newphoto.save()

            return redirect('eventDetails', pk=event.pk)
    else:
        form = EventForm()
        formGeo = GeolocationCreateForm()
        formset = PhotoFormSet()
    return render(
        request,
        'new_event.html',
        {'form': form , 'formGeo':formGeo, 'formset':formset}
        )
