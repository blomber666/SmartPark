from django.shortcuts import render
from django.shortcuts import redirect
from thingsboard_api_tools import TbApi
from parkings.models import Stop, Payment, Statistic, Price
from users.models import User
#, FilterModel
from django.contrib import messages
from django.urls import reverse

from push_telemetry import main as push_telemetry
from datetime import datetime
from datetime import timedelta
from datetime import time
from push_telemetry import main as push_telemetry


# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
username = "tenant@thingsboard.org"
password = "tenant"
tbapi = TbApi(url, username, password)

week_days = {
    '0' : 'Monday',
    '1' : 'Tuesday',
    '2' : 'Wednesday',
    '3' : 'Thursday',
    '4' : 'Friday',
    '5' : 'Saturday',
    '6' : 'Sunday',
    'None' : '',
}

def administration(request, context={}):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
            context.update({'override_entry': 'null', 'override_exit': 'null'})
            print('\n\n\n', context, '\n\n\n')
            start_filter = None
            start_date_converted = None
            end_filter = None
            end_date_converted = None
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
                
                if 'user_filter' in request.POST and request.POST.get("user_filter")!='':
                    user_filter = request.POST.get("user_filter")
                    context.update({'user_filter': user_filter})

            


            #get override telemetry
            override_entry = tbapi.get_device_by_name(name='override_1_1')
            override_entry = tbapi.get_latest_telemetry(override_entry['id'], telemetry_keys=["value"])["value"][0]['value']
            override_exit = tbapi.get_device_by_name(name='override_1_2')
            override_exit = tbapi.get_latest_telemetry(override_exit['id'], telemetry_keys=["value"])["value"][0]['value']

            active_stops = get_active_stops(user_filter, start_date_converted, end_date_converted, park_num)
            completed_stops = get_completed_stops(user_filter, start_date_converted, end_date_converted, park_num)

            stats = get_stats(start_date_converted, end_date_converted, park_num)
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

def get_active_stops(user, start_date_converted, end_date_converted, park_num):
    '''
    Get all active stops with the given filters, based on which is not None
    '''
    #active stops filters by start_time that is between start_date_converted and end_date_converted
    args = {}
    if user:
        args['user__username__icontains'] = user
    if start_date_converted and end_date_converted:
        args['start_time__range'] = [start_date_converted, end_date_converted+timedelta(days=1)]
    args['end_time__isnull'] = True 
    if park_num:
        args['park'] = park_num
    active_stops = Stop.objects.filter(**args)

    return active_stops
    
def get_completed_stops(user, start_date_converted, end_date_converted, park_num):
    '''
    Get all completed stops with the given filters, based on which is not None
    '''
    #completed_stops_1 filters by start_time that is between start_date_converted and end_date_converted
    #completed_stops_2 filters by end_time that is between start_date_converted and end_date_converted
    #then we combine the two querysets
    args = {}
    if user:
        args['user__username__icontains'] = user

    if start_date_converted and end_date_converted:
        args['start_time__range'] = [start_date_converted, end_date_converted+timedelta(days=1)]
    args['end_time__isnull'] = False
    if park_num:
        args['park'] = park_num
    completed_stops_1 = Stop.objects.filter(**args)

    args = {}
    if user:
        args['user__username__icontains'] = user
    if start_date_converted and end_date_converted:
        args['end_time__range'] = [start_date_converted, end_date_converted+timedelta(days=1)]
    args['end_time__isnull'] = False
    if park_num:
        args['park'] = park_num
    completed_stops_2 = Stop.objects.filter(**args)

    completed_stops = completed_stops_1 | completed_stops_2
    return completed_stops

def get_stats(start_date_converted, end_date_converted, park_num):
    '''
    Get all stats with the given filters, based on which is not None
    '''
    #stats filters by start_time that is between start_date_converted and end_date_converted
    args = {}
    if start_date_converted and end_date_converted:
        args['date__range'] = [start_date_converted, end_date_converted]
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

    # for price in prices:
    #     if price.start_time == time(0,0,0):
    #         price.start_time = '00:00:00'

    #     if price.end_time == time(23, 59, 59):
    #         price.end_time = '23:59:59'
    #     price.day = week_days[str(price.day)]

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
                    push_telemetry('override_1_1', 'value', 'open')
                    #push_telemetry('door_1_1', 'value', '1')
                elif 'entry_close' in request.POST:
                    push_telemetry('override_1_1', 'value', 'close')
                    push_telemetry('door_1_1', 'value', '0')
                elif 'entry_default' in request.POST:
                    push_telemetry('override_1_1', 'value', 'null')
                    #push_telemetry('door_1_1', 'value', '0')
                elif 'exit_open' in request.POST:
                    push_telemetry('override_1_2', 'value', 'open')
                    #push_telemetry('door_1_2', 'value', '1')
                elif 'exit_close' in request.POST:
                    push_telemetry('override_1_2', 'value', 'close')
                    #push_telemetry('door_1_2', 'value', '0')
                elif 'exit_default' in request.POST:
                    push_telemetry('override_1_2', 'value', 'null')
                    #push_telemetry('door_1_1', 'value', '0')  
                else:
                    print('unknown button')
                #wait 2 seconds
                # time.sleep(2)
                return redirect('/administration')
        else:
            return redirect('/home')

def price(request):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                args = {}

                if 'add' in request.POST:
                    args['park'] = '1'
                    if 'date' in request.POST and request.POST['date']!="":
                        converted = datetime.strptime(request.POST['date'], '%m/%d/%Y').date()
                        args['date'] = converted

                    if 'day' in request.POST and request.POST['day']!="":
                        args['day'] = request.POST['day']

                    if 'start_time' in request.POST and request.POST['start_time']!="":
                        print('\n\n\n\n', request.POST['start_time'], '\n\n\n\n')
                        args['start_time'] = request.POST['start_time']
                    else:
                        args['start_time'] = time(0, 0, 0)

                    if 'end_time' in request.POST and request.POST['end_time']!="":
                        args['end_time'] = request.POST['end_time']
                    else:
                        args['end_time'] = time(23, 59, 59)
                    
                    if 'price' in request.POST and request.POST['price']!="":
                        args['price'] = request.POST['price']
                    else:
                        args['price'] = 0
                        
                    price = Price.objects.create(**args)
                    price.save()
                    

                elif 'edit' in request.POST:
                    args['id'] = request.POST['price_id']
                    price = Price.objects.filter(**args)
                    
                    args['park'] = 'park_1'
                    args['date'] = request.POST['date']
                    args['day'] = request.POST['day']
                    args['start_time'] = request.POST['start_time']
                    args['end_time'] = request.POST['end_time']
                    args['price'] = request.POST['price']
                    
                    price.update(**args)

                elif 'delete' in request.POST:

                    args = {}
                    args['price__id'] = request.POST['price_id']
                    price = Price.objects.filter(**args)
                    price.delete()

        return redirect('/administration')        

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
                push_telemetry(sensor_name, sensor_field, sensor_value)
                #add message sent
                messages.info(request,f'Telemetry sent to {sensor_name}')


            context = {
                'sensor_name': sensor_name,
                'sensor_field': sensor_field,
                'sensor_value': sensor_value
            }
        print("\n\n context:\n", context, "\n\n")
        return context
