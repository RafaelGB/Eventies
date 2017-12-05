from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render , reverse
from django.views.generic import ListView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Event, Tag, Category
from .forms import EventForm

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

@login_required
def NewEvent(request):

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect('eventDetails', pk=event.pk)
    else:
        form = EventForm()
        event = Event()
    return render(request, 'new_event.html', { 'event':event , 'form': form})
