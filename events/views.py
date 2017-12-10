from django.db.models import Count
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render, reverse
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.forms.formsets import formset_factory
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Event, Tag, Category, Photo
from .forms import EventForm, PhotoForm, BasePhotoFormSet

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
        if 'search' in self.request.GET and self.request.GET['search']:
            contains = self.request.GET['search']
            queryset = (
                Event.objects.filter(title__icontains=contains) | 
                Event.objects.filter(summary__icontains=contains)
                )
        else:
            queryset = Event.objects.all()
        return queryset

@method_decorator(login_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    fields = [
            'title',
            'description',
            'summary',
            'budget',
            'duration'
        ]
    template_name = 'update_event.html'
    context_object_name = 'event'
    form = EventForm
    """
    ----------------------------------------------------------
        funciones de la clase
    ----------------------------------------------------------
    """
    def form_valid(self, form):
        event = form.save(commit=False)
        event.updated_at = timezone.now()
        event.save()
        return redirect('eventDetails', pk=event.pk)
"""
, request.FILES,
                               queryset=Photo.objects.none()
"""
@login_required
def NewEvent(request):
     # Create the formset, specifying the form and formset we want to use.
    PhotoFormSet = formset_factory(PhotoForm, formset=BasePhotoFormSet)
    if request.method == 'POST':
        form = EventForm(request.POST)
        formset = PhotoFormSet(request.POST or None, request.FILES or None)
        if all([form.is_valid(),formset.is_valid()]):
            event = form.save(commit=False)
            event.created_by = request.user
            #photos = []
            event.save()
            for subformset in formset.cleaned_data:
                photo = subformset.get('picture')
                newphoto = Photo(picture=photo,event=event)  
                newphoto.save()
                #photos.append(newphoto)#deberian guardarse al final
                      
            
            #for picture in photos:
                #picture.save()
            return redirect('eventDetails', pk=event.pk)
    else:
        form = EventForm()
        formset = PhotoFormSet()
    print("en el return del render")
    return render(
        request,
        'new_event.html',
        {'form': form , 'formset':formset}
        )
