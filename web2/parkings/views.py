from django.shortcuts import render
from parkings.map_tools import generate_map
from users import views as users_views
from stops.models import Stop, Payment
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages



# Create your views here.
def park_1(request, context=None):
    #print(request.user.is_authenticated)
    #print(request.user)
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized', status=401)
        return redirect('')

    #get the stop with the plate of the user
    stop = Stop.objects.filter(plate=request.user.plate).last()
    plate = request.user.plate 
    start = stop.start_time if stop else None
    end = stop.end_time if stop else None
    payment = Payment.objects.filter(stop_id=stop.stop_id).last()
    amount = payment.amount if payment else None

    context = {'plate': plate, 'start': start, 'end': end , 'amount': amount}
    
    if request.user.is_authenticated:
        generate_map('parkings/static/park_1.json')
        return render(request, 'park_1.html', context)
    else:
        return users_views.home(request)

def pay(request):

    if request.user.is_authenticated:
        stop = Stop.objects.filter(plate=request.user.plate).last()
        #check if already payed
        payment = Payment.objects.filter(stop_id=stop.stop_id)

        if not payment:
            #calculate the amount in euors, every minute is 1 cent
            amount = (timezone.now() - stop.start_time).seconds / 60 * 0.01
            payment = Payment(stop_id=stop, payment_time=0, amount=amount)
            payment.save()
            context={'plate': request.user.plate, 'start': stop.start_time, 'payed': True}
        else:
            context={'plate': request.user.plate, 'start': stop.start_time, 'payed': False}

        return redirect('/park_1')
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized', status=401)
        return redirect('')