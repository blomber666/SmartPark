from django.shortcuts import render
from parkings.map_tools import generate_map
from users import views as users_views
from stops.models import Stop

def park_1(request):
    print(request.user.is_authenticated)
    print(request.user)
    #get the stop with the plate of the user
    stop = Stop.objects.filter(plate=request.user.plate).last()
    plate = request.user.plate
    start = stop.start_time
    context = {'plate': plate, 'start': start}
    
    if request.user.is_authenticated:
        generate_map('parkings/static/park_1.json')

        return render(request, 'park_1.html', context)
    else :
        users_views.home
# Create your views here.
