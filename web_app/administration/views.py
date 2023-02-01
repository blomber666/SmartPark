from django.shortcuts import render
from django.shortcuts import redirect
from thingsboard_api_tools import TbApi
from parkings.models import Stop, Payment, Statistic, Price
from users.models import User
#, FilterModel
from django.contrib import messages

from push_telemetry import main as push_telemetry
from datetime import datetime
from datetime import timedelta
from datetime import time


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

def administration(request,):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
            context = {'override_entry': 'null', 'override_exit': 'null'}
            start_filter = None
            start_date_converted = None
            end_filter = None
            end_date_converted = None
            username = None
           
            if request.method == 'GET':
                print("\n\n", request, "\n\n" )
                #get all active stops
                active_stops = Stop.objects.filter(end_time=None)
                #get all completed stops
                completed_stops = Stop.objects.filter(end_time__isnull=False)

                stats = Statistic.objects.all()
                #convert stats.average_time to hour:minute:second format
                for stat in stats:
                    stat.average_time = str(stat.average_time).split('.')[0]

                prices = Price.objects.all()
                for price in prices:
                    if price.start_time == time(0,0,0):
                        price.start_time = '00:00:00'

                    if price.end_time == time(23, 59, 59):
                        price.end_time = '23:59:59'

                    price.day = week_days[str(price.day)]

            elif request.method == 'POST':
                print("\n\n", request.body , "\n\n" )
                print("\n\n")

                park_num = 1

                if 'start_filter' in request.POST and request.POST.get("start_filter")!='':
                    start_filter = request.POST.get("start_filter")
                    print('\n\n\n', request.POST, '\n\n\n')
                    #convert to yyyy-mm-dd
                    start_date_converted = datetime.strptime(start_filter, '%m/%d/%Y')
                    start_date_converted = start_date_converted.date()
                    print(start_date_converted)
                    context.update({'start_filter': start_filter})

                if 'end_filter' in request.POST and request.POST.get("end_filter")!='':
                    end_filter = request.POST.get("end_filter")
                    #convert to yyyy-mm-dd
                    end_date_converted = datetime.strptime(end_filter, '%m/%d/%Y')
                    end_date_converted = end_date_converted.date()
                    print(end_date_converted)
                    context.update({'end_filter': end_filter})
                else:
                    end_date_converted = datetime.today().date()
                
                if 'username' in request.POST and request.POST.get("username")!='':
                    username = request.POST.get("username")
                    print(username)
                    context.update({'username': username})

                
                active_stops = get_filtered_active_stops(username, start_date_converted, end_date_converted, park_num)
                #get all completed stops with start_time between start_filter and end_filter
                completed_stops = get_filtered_completed_stops(username, start_date_converted, end_date_converted, park_num)

                stats = get_filtered_stats(start_date_converted, end_date_converted, park_num)

                prices = Price.objects.all()




            #get override telemetry
            override_entry = tbapi.get_device_by_name(name='override_1_1')
            override_entry = tbapi.get_latest_telemetry(override_entry['id'], telemetry_keys=["value"])["value"][0]['value']
            override_exit = tbapi.get_device_by_name(name='override_1_2')
            override_exit = tbapi.get_latest_telemetry(override_exit['id'], telemetry_keys=["value"])["value"][0]['value']
                
            
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

def get_filtered_active_stops(user, start_date_converted, end_date_converted, park_num):
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
    
def get_filtered_completed_stops(user, start_date_converted, end_date_converted, park_num):
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

def get_filtered_stats(start_date_converted, end_date_converted, park_num):
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

def get_door_state(request, door):
    if request.method == 'GET' and request.user.is_superuser:
        
        device = tbapi.get_device_by_name(name=str(door))
        door_state = tbapi.get_latest_telemetry(device['id'], telemetry_keys=["open"])["open"][0]['value']

        return render(request,'override.html', {'door': door_state})


def filter(request):
    return render(request, 'filter.html')
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

                print("\n\n override:\n", request.POST, "\n\n")
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
                print("\n\npost request:\n\n")
                if 'add' in request.POST:
                    print("\n\n price:\n", request.POST, "\n\n")
                    args = {}

                    args['park'] = 'park_1'
                    
                    args['date'] = request.POST['date'] if  request.POST['date']!="" else None
                    args['day'] = request.POST['day'] if  request.POST['day']!="" else None
                    # start_time is of type models.TimeField()
                    args['start_time'] = request.POST['start_time'] if  request.POST['start_time']!="" else time(0, 0, 0)
                    args['end_time'] = request.POST['end_time'] if  request.POST['end_time']!="" else time(23, 59, 59)
                    args['price'] = request.POST['price'] if  request.POST['price']!="" else None
                    price = Price.objects.create(**args)
                    price.save()
                    
                    return redirect('/administration')
                else:
                    return redirect('/administration')
                # elif 'edit' in request.POST:
                #     print("\n\n price:\n", request.POST, "\n\n")
                #     pass

                # elif 'delete' in request.POST:
                #     print("\n\n price:\n", request.POST, "\n\n")
                #     pass
            else:
                return redirect('/administration')

        else:
            return redirect('/administration')

