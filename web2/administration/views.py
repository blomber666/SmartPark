from django.shortcuts import render
from django.shortcuts import redirect
from stops.models import Stop, Payment
from django.contrib import messages



def administration(request):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized', status=401)
        return redirect('')
    else:
        if request.user.is_superuser:
            #get all active stops
            active_stops = Stop.objects.filter(end_time=None)
            context = {'active_stops': active_stops}
            completed_stops = Stop.objects.filter(end_time__isnull=False)
            context['completed_stops'] = completed_stops
            return render(request, 'administration.html', context)
        else:
            return redirect('/home')
