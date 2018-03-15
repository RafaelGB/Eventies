from django.db.models import Count
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render, reverse
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.forms.formsets import formset_factory
from django.contrib.gis.db.models.functions import Distance

from django.contrib.gis.geos import Point

from django.contrib.gis.measure import D
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from .models import Event, Tag, Category, Photo, Geolocation
from .forms import EventForm, PhotoForm, BasePhotoFormSet, GeolocationForm
from .decorators import user_is_event_author


def HomeView(request):
    return render(request, 'home.html')

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
        #contador de visitas se incrementa
        self.object.views += 1
        self.object.save()
        #definimos el contexto
        context = super(EventObjectView, self).get_context_data(**kwargs)
        #.annotate(q_count=Count('events_tags')).order_by('q_count') ?? para ordenar por veces repetidas???
        eventTags = Tag.objects.filter(events_tags=self.object).values_list('name_tag', flat=True)
        print(eventTags.query)
        eventTags_dic ={}
        for tag in eventTags:
            eventTags_dic[tag] = Tag.objects.get(name_tag=tag).events_tags.count()             
        context["eventTags"] = eventTags_dic
        context["coor"] = {"x": str(context["object"].geopos_at.coordinates.x), "y":str(context["object"].geopos_at.coordinates.y) }
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
        context = super(EventFilterView, self).get_context_data(**kwargs)

        if self.request.GET:
            for getObject in self.request.GET:
                context[getObject] = self.request.GET[getObject]
        # Call the base implementation first to get a context
        
        return context


    def get_queryset(self):

        """
        ----------------------------------------------------------
            filtro de type
        ----------------------------------------------------------
        """
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
        else:
            queryset = Event.objects.all()

        
        """
        ----------------------------------------------------------
            filtros extra
        ----------------------------------------------------------
        """
        if('distance' in self.request.GET):
            distance = self.request.GET['distance']
            if distance:
                distance = int(distance)
                lat , lng = [float(self.request.GET['lat']),float(self.request.GET['lng'])]
                ref_location = Point(lat, lng )
                queryset = queryset.filter(geopos_at__coordinates__distance_lt=(ref_location, D(m=distance))).order_by('-geopos_at__coordinates')
        
        if 'tags' in self.request.GET and self.request.GET['tags']:
            tags = self.request.GET['tags'].split(',')
            for tag in tags:
                queryset = queryset.filter(tags__name_tag=tag)
        return queryset

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_event_author, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    template_name = 'update_event.html'
    context_object_name = 'event'
    form_class = EventForm
    formGeo_class = GeolocationForm
    """
    ----------------------------------------------------------
        funciones de la clase
    ----------------------------------------------------------
    """
    def get_context_data(self, **kwargs):
        #recuperamos argumentos ya inicializados
        context = super(EventUpdateView, self).get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)  
        context['formGeo'] = self.formGeo_class(instance=self.object.geopos_at)
        """
            obtencion de los tags relacionados con el evento
        .........................................................
            
        """
        concatTags = ""
        eventTags = Tag.objects.filter(events_tags=self.object).values_list('name_tag', flat=True)
        for tag in eventTags:
            concatTags = concatTags+tag+','
        context['valueTags'] = concatTags

        #obtencion y dar formato a tags para fucion de autocompletado
        if not 'autoTags' in context:
            allTags = list(Tag.objects.values('name_tag'))
            allTags = str(allTags).replace("'name_tag'","name_tag")
            context['autoTags'] = allTags
        return context

    def get(self, request, *args, **kwargs):
        super(EventUpdateView, self).get(request, *args, **kwargs)
        form = self.form_class
        formGeo = GeolocationForm

        return self.render_to_response(self.get_context_data(
            object=self.object, form=form ,formGeo=formGeo))

    def post(self, request, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        formGeo = self.formGeo_class(request.POST)
        if all([form.is_valid(),formGeo.is_valid()]):
            """
                               Tratamiento de Event
            .........................................................
            
            """
            self.object.title = form.cleaned_data['title']
            self.object.description = form.cleaned_data['description']
            self.object.summary = form.cleaned_data['summary']
            self.object.budget = form.cleaned_data['budget']
            self.object.duration = form.cleaned_data['duration']
            self.object.updated_at = timezone.now()
            #tratamiento interno de geolocalización
            updateGeo = Geolocation.objects.get( pk=self.object.geopos_at.pk )           
            updateGeo.coordinates = formGeo.cleaned_data['coordinates']            
            updateGeo.save()
            self.object.save()
            """
                               Tratamiento de Tags
            .........................................................
            
            """
            primalTags = Tag.objects.filter(events_tags=self.object).values_list('name_tag', flat=True)
            myTags = request.POST["myTags"]
            arrayTags = myTags.split(',')
            for tag in arrayTags:
                newTag = None
                tagExist = Tag.objects.filter(name_tag=tag).exists()
                if not tagExist:
                    #crear nuevo tag
                    newTag = Tag(name_tag=tag)
                    newTag.save()
                    newTag.events_tags.add(self.object.pk)
                   
                elif tag not in primalTags:
                    #add evento al maytomany del tag
                    newTag = Tag.objects.get(name_tag=tag)
                    newTag.events_tags.add(self.object.pk)
                else:
                    #borramos de la lista si existe y ya esta en los originales
                    primalTags = primalTags.exclude(name_tag=tag)
            print (primalTags)
            for tag in primalTags:
                removeTag = Tag.objects.get(name_tag=tag)
                if removeTag.events_tags.count()   == 1:
                    #este tag solo se usaba na vez y queda borrado
                    removeTag.delete()
                else:
                    #este tag existe en otros eventos por lo que solo se elimina de este
                    removeTag.events_tags.remove(self.object.pk)
            return redirect('eventDetails', pk=self.object.pk)  
        else:
            return self.render_to_response(
              self.get_context_data(form=form,formGeo=formGeo))

@login_required
def NewEvent(request):
     # Create the formset, specifying the form and formset we want to use.
    PhotoFormSet = formset_factory(PhotoForm, formset=BasePhotoFormSet)
    if request.method == 'POST':
        form = EventForm(request.POST)
        formGeo = GeolocationForm(request.POST)
        formset = PhotoFormSet(request.POST or None, request.FILES or None)

        if all([form.is_valid(),formset.is_valid(),formGeo.is_valid()]):

            """
                               Tratamiento de Event
            .........................................................
            
            """
            myGeo = formGeo.save()
            event = form.save(commit=False)
            event.geopos_at = myGeo
            event.created_by = request.user
            event.save()
            """
                               Tratamiento de los Tags
            .........................................................
            
            """
            myTags = request.POST['myTags']
            arrayTags = myTags.split(',')
            for tag in arrayTags:
                newTag = None
                if not Tag.objects.filter(name_tag=tag).exists():
                    newTag = Tag(name_tag=tag)
                    newTag.save()
                else:
                    newTag = Tag.objects.get(name_tag=tag)
                newTag.events_tags.add(event.pk)
            """
                               Tratamiento de las Categorias
            .........................................................
            
            """
            return redirect('eventDetails', pk=event.pk)
    
    form = EventForm()
    formGeo = GeolocationForm()
    formset = PhotoFormSet()
    #obtencion y dar formato a tags para fucion de autocompletado
    allTags = list(Tag.objects.values('name_tag'))
    allTags = str(allTags).replace("'name_tag'","name_tag")

    return render(
        request,
        'new_event.html',
        {'form': form , 'formGeo':formGeo, 'formset':formset, 'allTags':allTags }
        )
