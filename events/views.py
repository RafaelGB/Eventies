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
from django.forms import modelformset_factory , DateTimeField
from django.contrib.gis.db.models.functions import Distance

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils.decorators import method_decorator

from django.http import HttpResponse , JsonResponse
from .models import Event, Tag, Category, Photo, Geolocation
from .forms import EventForm, PhotoForm, BasePhotoFormSet, GeolocationForm
from .decorators import user_is_event_author
from .recommender import getRecommendedEvents
def HomeView(request):
    if request.user.is_authenticated():
        
        events = getRecommendedEvents(request.user.pk) 
        return render(
            request,
            'home.html',
            {
            'events': events
            }
        )
    else:
        return render(
            request,
            'aboutUs.html'
        )

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
        Event.increment_view(self.object.pk)
        #definimos el contexto
        context = super(EventObjectView, self).get_context_data(**kwargs)
        """
            obtencion de las categorías relacionadas
        .........................................................
            
        """
        context["eventCategories"] = Category.for_event(self.object)
        """
            obtencion de las etiquetas relacionadas
        .........................................................
            
        """
        eventTags = Tag.for_event(self.object)
        eventTags_dic ={}
        for tag in eventTags:
            eventTags_dic[tag] = Tag.count_for_events(tag)       
        context["eventTags"] = eventTags_dic
        """
            tratamiento de la localizacion para su correcta visualizacion
        .........................................................
            
        """
        context["coor"] = {"x": str(context["object"].geopos_at.coordinates.x), "y":str(context["object"].geopos_at.coordinates.y) }
        """
            tratamiento de las imágenes del evento
        .........................................................
            
        """
        eventPhotos = Photo.objects.filter(event=self.object.pk)
        context["photos"] = eventPhotos
        """
            indicador de si el evento pertenece al usuario logueado
        .........................................................
            
        """
        context["is_own"] = (self.request.user == self.object.created_by)
        """
            obtención de los contadores del evento relevantes
                                    +
                        checks de opciones elegidas
        .........................................................
            
        """
        context["interested_count"]= self.object.interested_in.count()
        context["signed_up_count"]= self.object.signed_up.count()


        context["signed_up_clicked"] = (self.request.user in self.object.signed_up.all())
        context["interested_clicked"] = (self.request.user in self.object.interested_in.all())
        context["not_interested_clicked"] = (self.request.user in self.object.not_interested_in.all())
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
    ordering = ['views']
    paginate_by = 9
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

        if 'categories' in self.request.GET and self.request.GET['categories']:
            context['categories'] = self.request.GET.getlist('categories')

        if not 'autoTags' in context:
            allTags = list(Tag.objects.values('name_tag'))
            allTags = str(allTags).replace("'name_tag'","name_tag")
            context['autoTags'] = allTags

        if not 'allCategories' in context:
            context['allCategories'] = Category.objects.values_list('name_category',flat=True)
        
        if not 'type' in context:
            context['type'] = self.kwargs['type'] 


        return context


    def get_queryset(self):

        """
        ----------------------------------------------------------
            filtro de type
        ----------------------------------------------------------
        """
        if self.kwargs['type'] == 'search':
            contains = self.request.GET['search']
            queryset = Event.search_string(contains)
        if self.kwargs['type'] == 'own':
            queryset = Event.for_user(self.request.user)
        else:
            queryset = Event.objects.all()

        
        try:

            """
            ----------------------------------------------------------
                filtros extra
            ----------------------------------------------------------
            """

            if('search' in self.request.GET and self.request.GET['search']):
                contains = self.request.GET['search']
                queryset = (queryset & Event.search_string(contains))
            #---
            if('lat' in self.request.GET and self.request.GET['lat'] \
                and 'lng' in self.request.GET and self.request.GET['lng'] \
                and 'distance' in self.request.GET and self.request.GET['distance']):
                distance = self.request.GET['distance']
                distance = int(distance)
                distance =  distance if distance <= 200000 else 200000
                lat , lng = [float(self.request.GET['lat']),float(self.request.GET['lng'])]
                ref_location = Point(lat, lng )
                queryset = (queryset & Event.distance_range(ref_location,distance))
            #---
            if 'tags' in self.request.GET and self.request.GET['tags']:
                tags = self.request.GET['tags'].split(',')
                for tag in tags:
                    queryset = queryset.filter(tags__name_tag=tag)
            #---
            if 'categories' in self.request.GET and self.request.GET['categories']:
                categories = self.request.GET.getlist('categories')
                for category in categories:
                    queryset = queryset.filter(categories__name_category=category)
            #---
            if 'budget' in self.request.GET and self.request.GET['budget']:
                budget = self.request.GET['budget'].split(',')
                queryset = (queryset & Event.range_prices(budget[0],budget[1]))
            """ 
            -------------------------------------------------------
            selecciona un tipo de grupo
                    Ó
            elimina de la busqueda los que no intersan
            -------------------------------------------------------
            """
            if 'grupoIntereses' in self.request.GET and self.request.GET['grupoIntereses']:
                grupoIntereses = self.request.GET['grupoIntereses']
                if grupoIntereses =="assistant":
                    queryset = ( queryset & Event.objects.filter(signed_up__id=self.request.user.pk) )
                elif grupoIntereses =="interested":
                    queryset = ( queryset & Event.objects.filter(interested_in__id=self.request.user.pk) )
                elif grupoIntereses =="removed":
                    queryset = ( queryset & Event.objects.filter(not_interested_in__id=self.request.user.pk) )
                else:
                    queryset = queryset.exclude(not_interested_in__id=self.request.user.pk)
            else:
                queryset = queryset.exclude(not_interested_in__id=self.request.user.pk)

            """
            ----------------------------------------------------------
                selecciona un tipo de orden
            ----------------------------------------------------------
            """
            if 'orderBy' in self.request.GET and self.request.GET['orderBy']:  
                orderBy = self.request.GET['orderBy']
                if orderBy == "distance":
                    print("entro en distance")
                    lat , lng = [float(self.request.GET['lat']),float(self.request.GET['lng'])]
                    ref_location = Point(lat, lng )
                    #queryset = queryset.annotate(distance=Distance('geopos_at__coordinates', ref_location)).order_by('distance')
                    #queryset = (queryset & Event.distance_order(ref_location))
                elif orderBy == "cost":
                    print("entro en cost")
                elif orderBy == "date":
                    print("entro en date")
                elif orderBy == "views":
                    print("entro en views")
                
        except:
            print("HA HABIDO UN ERROR")
            queryset = Event.objects.all()

        #*************************************************************************
        #print("\n\n\n",queryset.query,"\n\n\n")
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

        if not 'errors' in context:
            context['form'] = self.form_class(instance=self.object)
            context['formGeo'] = self.formGeo_class(instance=self.object.geopos_at)

        """
            obtencion de las categorías relacionadas con el evento
                                        +
                        obtencion del resto de categorias
        .........................................................
            
        """
        context['allCategories'] = Category.objects.values_list('name_category',flat=True)
        context['myCategories'] = Category.objects.filter(events_categories=self.object).values_list('name_category', flat=True)
        """
            obtencion de los tags relacionados con el evento
                                    +
                        tratamiento para autocompletado
        .........................................................
            
        """
        concatTags = ""
        eventTags = Tag.objects.filter(events_tags=self.object).values_list('name_tag', flat=True)
        for tag in eventTags:
            concatTags = concatTags+tag+','
        context['valueTags'] = concatTags

        #obtencion y dar formato a tags para funcion de autocompletado
        if not 'autoTags' in context:
            allTags = list(Tag.objects.values('name_tag'))
            allTags = str(allTags).replace("'name_tag'","name_tag")
            context['autoTags'] = allTags
        return context

    def get(self, request, *args, **kwargs):
        super(EventUpdateView, self).get(request, *args, **kwargs)
        form = self.form_class
        formGeo = self.formGeo_class
        PhotoFormSet = modelformset_factory(model=Photo,form=PhotoForm)
        formset = PhotoFormSet(queryset=Photo.objects.filter(event=self.object))
        return self.render_to_response(self.get_context_data(
            object=self.object, form=form ,formGeo=formGeo ,formset=formset))

    def post(self, request, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST)
        formGeo = self.formGeo_class(request.POST)
        PhotoFormSet = modelformset_factory(model=Photo,form=PhotoForm,formset=BasePhotoFormSet,can_delete=False)
        formset = PhotoFormSet(request.POST or None, request.FILES or None)
        if all([form.is_valid(),formGeo.is_valid(),formset.is_valid()]):
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
            primalTags = list(Tag.objects.filter(events_tags=self.object).values_list('name_tag', flat=True))
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
                    primalTags.remove(tag)
            for tag in primalTags:
                removeTag = Tag.objects.get(name_tag=tag)
                if removeTag.events_tags.count()   == 1:
                    #este tag solo se usaba na vez y queda borrado
                    removeTag.delete()
                else:
                    #este tag existe en otros eventos por lo que solo se elimina de este
                    removeTag.events_tags.remove(self.object.pk)
            """
                               Tratamiento de Categorias
            .........................................................
            
            """
            arrayCategories = request.POST.getlist('myCategories')
            primalCategories= list(Category.for_event(self.object))
            
            for category in arrayCategories:
                if category not in primalCategories:
                    #si no estaba antes se añade al manytomany
                    updateCategory = Category.objects.get(name_category=category)
                    updateCategory.events_categories.add(self.object.pk)
                else:
                    #si estaba se descarta
                    primalCategories.remove(category)
            for category in primalCategories:
                #todos los no descartados quiere decir que se eliman del many to many
                updateCategory = Category.objects.get(name_category=category)
                updateCategory.events_categories.remove(self.object.pk) 
            """
                               Tratamiento de imágenes
            .........................................................
            
            """
            primalPhotos = list(Photo.objects.filter(event=self.object))
            for photo in formset.cleaned_data:
                #comprobamos que la foto no este vacía
                print("photo ",photo)
                if photo:
                    print("ok")
                    if photo['picture'] not in primalPhotos:
                        picture = photo['picture']
                        photo = Photo(event=self.object, picture=picture)
                        photo.save()
                    else:
                        primalPhotos.remove(photo['id'])
            for removed_photo in primalPhotos:
                picture = Photo.objects.get(pk=str(removed_photo))
                picture.delete()
                

            return redirect('eventDetails', pk=self.object.pk)  
        else:
            return self.render_to_response(
              self.get_context_data(errors=True,form=form,formGeo=formGeo,formset=formset))

@login_required
def NewEvent(request):
    # se crea el formSet con el objeto y formulario deseado + configuraciones extra
    PhotoFormSet = modelformset_factory(model=Photo,form=PhotoForm, extra=1)
    #formset=BasePhotoFormSet
    if request.method == 'POST':
        form = EventForm(request.POST)
        formGeo = GeolocationForm(request.POST)
        formset = PhotoFormSet(request.POST or None, request.FILES or None)

        dateform = request.POST["date"]

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
                               Tratamiento de Photos
            .........................................................
            
            """
            for tmp_form in formset.cleaned_data:
                if tmp_form:
                    picture = tmp_form['picture']
                    photo = Photo(event=event, picture=picture)
                    photo.save()
            """
                               Tratamiento de los Tags
            .........................................................
            
            """
            myTags = request.POST['myTags']
            arrayTags = myTags.split(',')

            for tag in arrayTags:
                if tag != '':
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
            arrayCategories = request.POST.getlist('myCategories')
            for category in arrayCategories:
                newCategory = Category.objects.get(name_category=category)
                newCategory.events_categories.add(event.pk)
            return redirect('eventDetails', pk=event.pk)
    else:
        form = EventForm()
        formGeo = GeolocationForm()
        formset = PhotoFormSet(queryset=Photo.objects.none())

    #obtencion de tags y darles formato para funcion de autocompletado
    autoTags = list(Tag.objects.values('name_tag'))
    autoTags = str(autoTags).replace("'name_tag'","name_tag")
    #obtencion de categorias
    allCategories = Category.objects.values_list('name_category',flat=True)
    return render(
            request,
            'new_event.html',
            {
            'form': form ,
            'formGeo':formGeo,
            'formset':formset,
            'autoTags':autoTags,
            'allCategories':allCategories 
            }
        )

@login_required
def EventFlowControl(request,**kwargs):
    if request.method == 'POST':
        id_event = request.POST['event_pk']
        user = request.user
        event = Event.objects.get(pk=id_event)

        option = None
        tipo = kwargs['type']
        remove_add = None
        if tipo == "interested":
            if user in event.interested_in.all():
                event.interested_in.remove(user)
                remove_add='removed'
            else:
                event.interested_in.add(user)
                remove_add='added'
                #si se esta interesado se deja de asistir
                if user in event.signed_up.all():
                    event.signed_up.remove(user)
        elif tipo == "assistants":
            if user in event.signed_up.all():
                event.signed_up.remove(user)
                remove_add='removed'
            else:
                event.signed_up.add(user)
                remove_add='added'
                #si se asiste se deja de estar interesado
                if user in event.interested_in.all():
                    event.interested_in.remove(user)
        elif tipo == "not_interested":
            print("hola")
            if user in event.not_interested_in.all():
                event.not_interested_in.remove(user)
                remove_add='removed'
            else:
                event.not_interested_in.add(user)
                remove_add='added'
                #si se deja de estar interesado se anula el resto de votos
                if user in event.interested_in.all():
                    event.interested_in.remove(user)
                if user in event.signed_up.all():
                    event.signed_up.remove(user)
        else:
            remove_add='nothing'
        data = {
            'remove_add' : remove_add
        }
    else:   
        data = {}
    return JsonResponse(data)

