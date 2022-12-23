from django.shortcuts import render
from parkings.map_tools import generate_map
from users import views as users_views
from stops.models import Stop, Payment
# Create your views here.
def park_1(request, context=None):
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

def pay(request):
    if request.user.is_authenticated:
        stop = Stop.objects.filter(plate=request.user.plate).last()
        #check if already payed
        payment = Payment.objects.filter(stop_id=stop.stop_id)
        if not payment:
            payment = Payment(stop_id=stop, payment_time=0, amount=0)
            payment.save()
            context={'plate': request.user.plate, 'start': stop.start_time, 'payed': True}
            park_1(request, context)
        else:
            context={'plate': request.user.plate, 'start': stop.start_time, 'payed': False}
            park_1(request, context)
    else:
        users_views.home