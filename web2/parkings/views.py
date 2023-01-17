from django.shortcuts import render
from parkings.map_tools import generate_map
from users import views as users_views
from stops.models import Stop, Payment
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages



# Create your views here.
def park_1(request, context=None):
    
    if request.user.is_authenticated:
        free_spaces, total_spaces = generate_map('parkings/static/park_1.json')
        #get the stop with the plate of the user
        stop = Stop.objects.filter(plate=request.user.plate).last()
        plate = request.user.plate 
        start = stop.start_time if stop and stop.start_time else None
        end = stop.end_time if stop and stop.end_time else None

        payment = Payment.objects.filter(stop_id=stop.stop_id).last() if stop else None
        if payment:
            amount = payment.amount
        elif stop:
            amount = calculate_amount(start, timezone.now())
        else:
            amount = 0
        payed = payment
        print('pagamento', payment)
        print('spazi liberi', free_spaces)
        context = {'plate': plate, 'start': start, 'end': end , 'amount': amount , 'free_spaces': free_spaces, 'payed': payed}

        return render(request, 'park_1.html', context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')

def pay(request):
    if request.user.is_authenticated and request.method == 'GET':
        print("\n\n\n user is authenticated")
        stop = Stop.objects.filter(plate=request.user.plate).last()
        print('\n\n\n\nstop', stop)
        #check if already payed
        payment = Payment.objects.filter(stop_id=stop.stop_id)
        print('\n\n\n\npayment', payment)
        if not payment:
            #calculate the amount in euors, every minute is 1 cent
            end = timezone.now()
            amount = (end - stop.start_time).seconds / 60 * 0.01
            payment = Payment(stop_id=stop, payment_time=0, amount=amount)
            payment.save()
            print('\n\n\n\npagamento effettuato')
        else:
            #already payed
            pass

        return redirect('/park_1')
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')

def calculate_amount(start, end):
    '''calculate the amount in euros, every minute is 1 cent.
    start and end are datetime.datetime objects'''
    print('\n\n\nsecondi', (end - start).total_seconds())
    
    #calculate the amount in euors, every minute is 1 cent
    amount = ((end - start).total_seconds()) / 60 * 0.1
    #round to 2 decimal places
    amount = round(amount, 2)
    return amount
