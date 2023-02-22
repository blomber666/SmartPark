from django.shortcuts import render
from django.shortcuts import redirect
from thingsboard_api_tools import TbApi
from parkings.models import Stop, Payment, Statistic, Price
from users.models import User
#, FilterModel
from django.contrib import messages
# from django.urls import reverse

from push_telemetry import main as push_telemetry
from datetime import datetime
from datetime import timedelta
from datetime import time
from parkings.views import time_intersect


# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
username = "tenant@thingsboard.org"
password = "tenant"
tbapi = TbApi(url, username, password)

def administration(request, context={}):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
            context.update({'override_entry': 'null', 'override_exit': 'null'})
            print('\n\n\n', context, '\n\n\n')
            start_filter = None
            start_filter = None
            end_filter = None
            end_filter = None
            user_filter = None
            park_num = 1
           
            if request.method == 'GET':
                pass
      
            elif request.method == 'POST':

                if 'sensor_get' in request.POST or 'sensor_send' in request.POST:
                    new_context = sensor_control(request)
                    context.update(new_context)

                if 'start_filter' in request.POST and request.POST.get("start_filter")!='':
                    start_filter = request.POST.get("start_filter")
                    context.update({'start_filter': start_filter})

                if 'end_filter' in request.POST and request.POST.get("end_filter")!='':
                    end_filter = request.POST.get("end_filter")
                    context.update({'end_filter': end_filter})
                
                if 'user_filter' in request.POST and request.POST.get("user_filter")!='':
                    user_filter = request.POST.get("user_filter")
                    context.update({'user_filter': user_filter})

            #get override telemetry
            override_entry = tbapi.get_device_by_name(name='override_1_1')
            override_entry = tbapi.get_latest_telemetry(override_entry['id'], telemetry_keys=["value"])["value"][0]['value']
            override_exit = tbapi.get_device_by_name(name='override_1_2')
            override_exit = tbapi.get_latest_telemetry(override_exit['id'], telemetry_keys=["value"])["value"][0]['value']

            active_stops = get_active_stops(user_filter, start_filter, end_filter, park_num)
            completed_stops = get_completed_stops(user_filter, start_filter, end_filter, park_num)

            stats = get_stats(start_filter, end_filter, park_num)
            prices = get_prices(park_num='1')
            
            context.update({
                'active_stops': active_stops,
                'completed_stops': completed_stops,
                'stats': stats,
                'prices': prices,
                'override_entry': str(override_entry),
                'override_exit': str(override_exit),
                }
            ) 
            return render(request, 'administration.html', context)
        else:
            return redirect('/home')

def get_active_stops(user, start_date, end_date, park_num):
    '''
    Get all active stops with the given filters, based on which is not None
    '''
    #active stops filters by start_time that is between start_date_converted and end_date_converted
    if start_date:
        start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
    else:
        end_date = datetime.today().date()
    args = {}
    if user:
        args['user__username__icontains'] = user
    if start_date and end_date:
        args['start_time__range'] = [start_date, end_date+timedelta(days=1)]
    args['end_time__isnull'] = True 
    if park_num:
        args['park'] = park_num
    active_stops = Stop.objects.filter(**args)

    return active_stops
    
def get_completed_stops(user, start_date, end_date, park_num):
    '''
    Get all completed stops with the given filters, based on which is not None
    '''
    #completed_stops_1 filters by start_time that is between start_date and end_date
    #completed_stops_2 filters by end_time that is between start_date and end_date
    #then we combine the two querysets
    if start_date:
        start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
    args = {}
    if user:
        args['user__username__icontains'] = user

    if start_date and end_date:
        args['start_time__range'] = [start_date, end_date+timedelta(days=1)]
    args['end_time__isnull'] = False
    if park_num:
        args['park'] = park_num
    completed_stops_1 = Stop.objects.filter(**args)

    args = {}
    if user:
        args['user__username__icontains'] = user
    if start_date and end_date:
        args['end_time__range'] = [start_date, end_date+timedelta(days=1)]
    args['end_time__isnull'] = False
    if park_num:
        args['park'] = park_num
    completed_stops_2 = Stop.objects.filter(**args)

    completed_stops = completed_stops_1 | completed_stops_2
    return completed_stops

def get_stats(start_date, end_date, park_num):
    '''
    Get all stats with the given filters, based on which is not None
    '''
    if start_date:
        start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
    #stats filters by start_time that is between start_date and end_date
    args = {}
    if start_date and end_date:
        args['date__range'] = [start_date, end_date]
    if park_num:
        args['park'] = park_num
    stats = Statistic.objects.filter(**args)
    #convert stats.average_time to hour:minute:second format
    for stat in stats:
        stat.average_time = str(stat.average_time).split('.')[0]
    
    return stats

def get_prices(park_num):
    '''
    Get all prices with the given filters, based on which is not None
    '''
    #prices filters by park
    args = {}
    if park_num:
        args['park'] = park_num
    prices = Price.objects.filter(**args)

    #convert every None value to ""
    for price in prices:
        if price.date == None:
            price.date = ''
        if price.day == None:
            price.day = ''
        if price.start_time == None:
            print(type(price.start_time))
            print(price.start_time, str(price.start_time))
            price.start_time = ''
        if price.end_time == None:
            price.end_time = ''

    return prices

def get_door_state(request, door):
    if request.method == 'GET' and request.user.is_superuser:
        
        device = tbapi.get_device_by_name(name=str(door))
        door_state = tbapi.get_latest_telemetry(device['id'], telemetry_keys=["open"])["open"][0]['value']

        return render(request,'override.html', {'door': door_state})

def override(request):
    '''
    Override the gate:
    push teleemtry  value wiht 'open' or 'close' to the gate
    based on which button inside administration.html is pressed
    '''

    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/home')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':

                if 'entry_open' in request.POST:
                    push_telemetry('override_1_1', 'open')
                elif 'entry_close' in request.POST:
                    push_telemetry('override_1_1', 'close')
                elif 'entry_default' in request.POST:
                    push_telemetry('override_1_1', 'null')
                elif 'exit_open' in request.POST:
                    push_telemetry('override_1_2', 'open')
                elif 'exit_close' in request.POST:
                    push_telemetry('override_1_2', 'close')
                elif 'exit_default' in request.POST:
                    push_telemetry('override_1_2', 'null')
                else:
                    print('unknown button')

                return redirect('/administration')
        else:
            return redirect('/home')

def price(request):
    print('price request',request)
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                args = {}
                if 'delete' in request.POST:
                    id = request.POST['price_id']
                    price = Price.objects.get(id = id)
                    price.delete()
                    return redirect('/administration')

                args = price_control(request)

                if args == None:
                    return redirect('/administration')

                else:                  
                    if 'add' in request.POST:         
                        price = Price.objects.create(**args)
                        price.save()
                        
                    elif 'edit' in request.POST:
                        price = Price.objects.filter(id = args['id'])
                        print('\n\n\n\nprice', price, '\n\n\n\n')
                        price.update(**args)

        return redirect('/administration')        

def price_control(request):
    args = {}
    args['park'] = '1'
    if 'price_id' in request.POST and request.POST['price_id']!="":
        args['id'] = request.POST['price_id']
    else:
        if 'edit' in request.POST:
            messages.error(request,'Price id is missing')
            return None

    if 'price_date' in request.POST and request.POST['price_date']!="":
        print('date: ', request.POST['price_date'])
        if(datetime. strptime(request.POST['price_date'], '%d/%m/%Y') > datetime.now()):
            converted = datetime.strptime(request.POST['price_date'], '%d/%m/%Y').date()
            print('converted: ', converted)
            args['date'] = converted
        else:
            messages.error(request,'Date must be in the future')
            return redirect('/administration')

    if 'price_day' in request.POST and request.POST['price_day']!="" and request.POST['price_day']!='None':
        args['day'] = request.POST['price_day']

    if 'price_start_time' in request.POST and request.POST['price_start_time']!="":
        start_time = request.POST['price_start_time']
        if len(request.POST['price_start_time']) == 5:
            start_time = start_time + ':00'
        args['start_time'] = str(start_time)
    else:
        messages.warning(request, 'start time automatically set to 00:00:00')
        args['start_time'] = str(time(0, 0, 0))

    if 'price_end_time' in request.POST and request.POST['price_end_time']!="":
        end_time = request.POST['price_end_time']
        if len(request.POST['price_end_time']) == 5:
            end_time = end_time + ':00'
        args['end_time'] = str(end_time)   
    else:
        messages.warning(request, 'end time automatically set to 23:59:59')
        args['end_time'] = str(time(23, 59, 59))

    if 'price_price' in request.POST and request.POST['price_price']!="":
        if float(request.POST['price_price']) >=0:
            args['price'] = request.POST['price_price']
        else:
            messages.error(request, 'Price must be positive')
            redirect('/administration')

    if check_price(request, args):
        return args
    else:
        return None


def check_price(request, args):
    '''
    check if the new/edited price is valid, 
    and if it doesn't overlaps with an existing one
    '''

    if 'price' not in args:
        messages.error(request,'Price must be filled')
        return False

    #check if price_date and price_day are in args
    if not 'date' in args and not 'day' in args:
        print('date and day are empty')
        messages.error(request,'Date or day must be filled')
        return False
    
    if 'date' in args and 'day' in args:
        print('date and day are filled')
        messages.error(request,'Date and day cannot be filled at the same time')
        return False

    if str(args['start_time']) > str(args['end_time']):
        messages.error(request,'Start time must be before end time')
        return False

    if 'date' in args:
        #get all prices with the same date as input
        prices = Price.objects.filter(date = args['date'])
        #remove the price being edited
        if 'id' in args:
            prices = prices.exclude(id = args['id'])
            print('filtered prices: ', prices)
        print('date prices: ', prices)
        if new_time_overlap(request, prices, args):
            messages.error(request,'Price overlaps with existing price')
            return False

    elif 'day' in args:
        #get all prices with the same day as input
        prices = Price.objects.filter(day = args['day'])
        #remove the price being edited
        if 'id' in args:
            prices = prices.exclude(id = args['id'])
            print('filtered prices: ', prices)
        print('day prices: ', prices)
        if new_time_overlap(request, prices, args):
            messages.error(request,'Price overlaps with existing price')
            return False
        
    return True

def new_time_overlap(request, prices, args):
    '''
    check if the new/edited price overlaps with any existing one
    '''
    #convert to datetime.time
    new_start_time = datetime.strptime(args['start_time'], '%H:%M:%S').time()
    new_end_time = datetime.strptime(args['end_time'], '%H:%M:%S').time()
    for price in prices:
        if time_intersect(new_start_time, new_end_time, price.start_time, price.end_time):
            return True
    return False

def sensor_control(request):
        context = {}
        if request.method == 'POST':
            sensor_name = None
            sensor_field = None
            sensor_telemetry = None
            args = {}

            if 'sensor_name' in request.POST and request.POST['sensor_name']!="":
                sensor_name = request.POST['sensor_name']
                sensor = tbapi.get_device_by_name(name=str(sensor_name))
                args['device'] = sensor['id']
            
            if 'sensor_field' in request.POST and request.POST['sensor_field']!="":
                sensor_field = request.POST['sensor_field']
                args['telemetry_keys'] = str(request.POST['sensor_field'])

            if 'sensor_value' in request.POST and request.POST['sensor_value']!="":
                sensor_value = request.POST['sensor_value']
                args['telemetry_value'] = str(request.POST['sensor_value'])

            #get latest telemetry
            if 'sensor_get' in request.POST:
                #delete args['telemetry_value'] if it exists
                if 'telemetry_value' in args:
                    del args['telemetry_value']

                sensor_telemetry = tbapi.get_latest_telemetry(**args)[f"{args['telemetry_keys']}"]
                print("\n\n sensor_telemetry:\n", sensor_telemetry, "\n\n")

                if len(sensor_telemetry) == 0:
                    sensor_value = "No data"
                elif len(sensor_telemetry) == 1:
                    sensor_value = sensor_telemetry[0]['value']
                    if sensor_value == None:
                        sensor_value = "No data"
                else:
                    raise Exception("sensor_telemetry has more than one value")
                
            #send telemetry
            elif 'sensor_send' in request.POST:
                push_telemetry(sensor_name, sensor_value)
                #add message sent
                messages.info(request,f'Telemetry sent to {sensor_name}')


            context = {
                'sensor_name': sensor_name,
                'sensor_field': sensor_field,
                'sensor_value': sensor_value
            }
        print("\n\n context:\n", context, "\n\n")
        return context
