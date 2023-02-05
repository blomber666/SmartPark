from django.shortcuts import render
from parkings.map_tools import generate_map
#from users import views as users_views
from parkings.models import Stop, Payment, TbApi, Price
from users.models import User
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta


# Create your views here.
def park_1(request, context={}):
    
    if request.user.is_authenticated:
        start_filter = None
        start_date_converted = None
        end_filter = None
        end_date_converted = None
        park_num = 1

        #read free_spaces and total_spaces from file park_1.txt inside media folder
        with open('media/park_1.txt', 'r') as f:
            free_spaces = int(f.readline())
            total_spaces = int(f.readline())

        stop = Stop.objects.filter(user=request.user).last()
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

        payment = Payment.objects.filter(stop=stop).last() if stop else None
        if payment:
            amount = f'{payment.amount}€'
        elif stop:
            amount = f'{ calculate_amount(start, timezone.now())["amount"] }€'
        else:
            amount = '0€'
        payed = payment

        park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
        park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)

        if request.method == 'POST':
            print('\n\n\npost request\n\n\n')

            if 'start_filter' in request.POST and request.POST.get("start_filter")!='':
                start_filter = request.POST.get("start_filter")
                #convert to yyyy-mm-dd
                start_date_converted = datetime.strptime(start_filter, '%m/%d/%Y').date()
                context.update({'start_filter': start_filter})

            if 'end_filter' in request.POST and request.POST.get("end_filter")!='':
                end_filter = request.POST.get("end_filter")
                #convert to yyyy-mm-dd
                end_date_converted = datetime.strptime(end_filter, '%m/%d/%Y')
                end_date_converted = end_date_converted.date()
                context.update({'end_filter': end_filter})
            else:
                end_date_converted = datetime.today().date()

        stops = get_stops(request.user, start_date_converted, end_date_converted, park_num)

        context = {'username': username, 'start': start, 'end': end , 'last_time':last_time, 'amount': amount, 'payed': payed, \
            'free_spaces': free_spaces, 'park_status': park_status, 'park_percent': park_percent, 'total_spaces': total_spaces,\
                'stops': stops}
        return render(request, 'park_1.html', context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')

def get_stops(user, start_date, end_date, park_num):
    '''
    Get all stops with the given filters, bu always filter by user
    '''
    #completed_stops_1 filters by start_time that is between start_date and end_date
    #completed_stops_2 filters by end_time that is between start_date and end_date
    #then we combine the two querysets
    print('get_stops')
    assert(user), 'user is required'

    args = {}
    args['user'] = user
    if start_date and end_date:
        args['start_time__range'] = [start_date, end_date+timedelta(days=1)]
    if park_num:
        args['park'] = park_num
    stops_1 = Stop.objects.filter(**args)

    args = {}
    args['user'] = user
    if start_date and end_date:
        args['end_time__range'] = [start_date, end_date+timedelta(days=1)]
    if park_num:
        args['park'] = park_num
    stops_2 = Stop.objects.filter(**args)

    stops = stops_1 | stops_2

    for stop in stops:
        payment = Payment.objects.filter(stop=stop).last()
        if payment:
            stop.amount = f'{payment.amount}€'
        elif stop.start_time:
            stop.amount = f'{ calculate_amount(stop.start_time, timezone.now())["amount"] }€ (not payed)'
        else:
            stop.amount = '0€'
    
    return stops

def pay(request):
    if request.user.is_authenticated and request.method == 'GET':
        stop = Stop.objects.filter(user=request.user).last()
        print(stop)
        #check if already payed
        payment = Payment.objects.filter(stop=stop)
        if not payment:
            #calculate the amount in euors, every minute is 1 cent
            amount = calculate_amount(stop.start_time)['amount']
            payment = Payment(stop=stop, payment_time=0, amount=amount)
            payment.save()
        else:
            #already payed
            pass

        return redirect('/park_1')
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')


#API
def calculate_amount(start, end=timezone.now()):
    '''calculate the amount in euros,
    start and end are datetime.datetime objects.
    Get the prices from the db'''
    
    price = get_price_from_db()
    print('\n\n\n\n')
    print('price: ', price)
    #calculate the amount in euors, every minute is 1 cent
    amount = ((end - start).total_seconds()) / 60 * price
    #round to 2 decimal places
    amount = round(amount, 2)
    #add a zero at the end if the cents are a multiple of 10 or if there are no cents
    # if amount % 0.1 == 0 or amount % 1 == 0:
    #     amount = str(amount) + '0'
    #da fare altrove, qui amount deve essere un numero

    assert amount >= 0, 'amount is negative'

    context = {'amount': amount}
    return context

def get_parkings(request):
    if(request.user.is_authenticated):
        with open('media/park_1.txt', 'r') as f:
            free_spaces = int(f.readline())
            total_spaces = int(f.readline())
        print('\n\nfree_spaces: ', free_spaces)
        print('total_spaces: ', total_spaces, "\n\n")
        park_status = str((total_spaces-free_spaces)) + '/' + str(total_spaces)
        park_percent = int(((total_spaces-free_spaces)/total_spaces)*100)
        context = {'park_status': park_status, 'park_percent': park_percent}
        return JsonResponse(context)
    else:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')

def get_price_from_db():
    '''Get the prices from the db'''
    prices = Price.objects.all()
    price = 0.01 #default price
    if prices:
        today = datetime.today().date()
        now = datetime.now().time()
        #check in order of priority: date, weekday, every day, default price
        #date is in price.date
        #weekday is in price.day as "Every day", "Every Monday", "Every Tuesday", ...
        #every day is in price.day as "Every day"
        #consider only if the time is between start_time and end_time

        found_day = None
        found_date = None
        found_every_day = None

        for p in prices:
            if p.date and p.date == today:
                if p.start_time <= now and p.end_time >= now:
                    found_date = p
                    break
            elif p.day and p.day == 'Every ' + today.strftime("%A"):
                if p.start_time <= now and p.end_time >= now:
                    found_day = p
            elif p.day and p.day == 'Every Day':
                if p.start_time <= now and p.end_time >= now:
                    found_every_day = p


        for p in [found_date, found_day, found_every_day]:
            if p:
                price = float(p.price)
                break

        print('price: ', price)

    return price
    
        
        