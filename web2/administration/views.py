from django.shortcuts import render
from django.http import HttpResponseRedirect
from stops.models import Stop, Payment
# Create your views here.

def administration(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            #get all active stops
            active_stops = Stop.objects.filter(end_time=None)
            context = {'active_stops': active_stops}
            completed_stops = Stop.objects.filter(end_time__isnull=False)
            context['completed_stops'] = completed_stops
            return render(request, 'administration.html', context)
        else:
            return HttpResponseRedirect('/home')
