from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render , reverse
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Event, Tag, Category

def itsOK(request):
    return HttpResponse("OK")

def HomeView(request):
    return render(request, 'home.html')

class EventObjectView(DetailView):
    model = Event
    context_object_name = 'event'
    template_name = 'eventDetails.html'

    def get_context_data(self, **kwargs):
        context = super(EventObjectView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context