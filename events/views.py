from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render , reverse
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Event, Tag, Category
from .forms import NewEventForm

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
        queryset = super(EventFilterView, self).get_queryset()
        if 'search' in self.request.GET:
            queryset = queryset.filter(title__icontains=self.request.GET['search'])
        return queryset


@login_required
def new_event(request):
    event = get_object_or_404(Event)
    if request.method == 'POST':
        form = NewEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect('eventDetails', pk=event.pk)
    else:
        form = NewEventForm()
    return render(request, 'new_event.html', {'event': event, 'form': form})