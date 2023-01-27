from django.shortcuts import render
from parkings.map_tools import generate_map
#from users import views as users_views
from parkings.models import Stop, Payment, TbApi
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse


# Create your views here.
def park_1(request, context=None):
    
    if request.user.is_authenticated:
        free_spaces, total_spaces = generate_map('parkings/static/park_1.json')
        #get the stop with the plate as foreign key
        stop = Stop.objects.filter(user=request.user).last()
        plate = request.user.username  if stop else None
        start = stop.start_time if stop and stop.start_time else None
        end = stop.end_time if stop and stop.end_time else None

        #last time is the last time the user was in the parking, if the user is in the parking now, the last time is the start time
        #if the user is not in the parking, the last time is the end time
        #if the user never was in the parking, the last time is Never
        last_time = end if end else start if start else 'Never'
        #convert to only date
        if last_time != 'Never':
            last_time = last_time.date()

        #get the price of the park from the device park_1
        # ThingsBoard REST API URL
        url = "http://192.168.1.197:8080"
        # Default Tenant Administrator credentials
        username = "tenant@thingsboard.org"
        password = "tenant"
        tbapi = TbApi(url, username, password)
        price_device = tbapi.get_device_by_name('price_1')
        price = tbapi.get_telemetry(price_device['id']['id'], telemetry_keys=["price"])['price'][0]['value']

        payment = Payment.objects.filter(stop_id=stop.stop_id).last() if stop else None
        if payment:
            amount = f'{payment.amount}€'
        elif stop:
            amount = f'{calculate_amount(start, timezone.now())}€'
        else:
            amount = '0€'
        payed = payment

        park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
        park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)

        context = {'plate': plate, 'start': start, 'end': end , 'last_time':last_time, 'amount': amount, 'payed': payed, \
            'free_spaces': free_spaces, 'park_status': park_status, 'park_percent': park_percent, 'total_spaces': total_spaces,}

        return render(request, 'park_1.html', context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')

def pay(request):
    if request.user.is_authenticated and request.method == 'GET':
        stop = Stop.objects.filter(plate=request.user.plate).last()
        #check if already payed
        payment = Payment.objects.filter(stop_id=stop.stop_id)
        if not payment:
            #calculate the amount in euors, every minute is 1 cent
            amount = calculate_amount(stop.start_time)['amount']
            payment = Payment(stop_id=stop, payment_time=0, amount=amount)
            payment.save()
        else:
            #already payed
            pass

        return redirect('/park_1')
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')


#API
def calculate_amount(start, end=timezone.now(), price=0.1):
    '''calculate the amount in euros, every minute is 'price' cents
    start and end are datetime.datetime objects'''
    #calculate the amount in euors, every minute is 1 cent
    amount = ((end - start).total_seconds()) / 60 * price
    #round to 2 decimal places
    amount = round(amount, 2)    
    print("\n\n", amount, "\n\n\n")
    context = {'amount': amount}
    return JsonResponse(context)

def get_parkings(request):
    if(request.user.is_authenticated):
        free_spaces, total_spaces = generate_map('parkings/static/park_1.json')
        park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
        park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)
        context = {'park_status': park_status, 'park_percent': park_percent}
        return JsonResponse(context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
