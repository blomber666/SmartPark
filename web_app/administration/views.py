from django.shortcuts import render
from django.shortcuts import redirect
from .models import Stop, TbApi
#, FilterModel
from django.contrib import messages

from push_telemetry import main as push_telemetry


# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
username = "tenant@thingsboard.org"
password = "tenant"
tbapi = TbApi(url, username, password)


def administration(request,context={'override_entry': 'null', 'override_exit':'null'}):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
           
            if request.method == 'GET':
                print("\n\n", request, "\n\n" )
                #get all active stops
                active_stops = Stop.objects.filter(end_time=None)
                #get all completed stops
                completed_stops = Stop.objects.filter(end_time__isnull=False)

                #get the latest telemetry of device named 'door_1_1'
                #entry_door_telemetry, exit_door_telemetry = get_entry_exit()
                # print("exit"+exit_door_telemetry)

            elif request.method == 'POST':
                print("\n\n", request.body , "\n\n" )
                print("\n\n")
                smartparks = request.POST.get("smartparks")
                print(smartparks)
                start_time = request.POST.get("start_time")
                print(start_time)
                end_time = request.POST.get("end_time")
                print(end_time)
                username = request.POST.get("username")
                print(username)
                plate = request.POST.get("plate")
                print(plate)
                print("\n\n")

                if smartparks is None:
                    active_stops = []
                    completed_stops = [] 
                    messages.error(request,"You must choose at least one SmartPark.")
                    pass
                else:
                    #get all active stops
                    active_stops = Stop.objects.filter(plate=plate, end_time=None, start_time=start_time)
                    #get all completed stops
                    completed_stops = Stop.objects.filter(plate=plate, end_time__lt=end_time, start_time=start_time)

            #get override telemetry
            override_entry = tbapi.get_device_by_name(name='override_1_1')
            override_entry = tbapi.get_latest_telemetry(override_entry['id'], telemetry_keys=["value"])["value"][0]['value']
            override_exit = tbapi.get_device_by_name(name='override_1_2')
            override_exit = tbapi.get_latest_telemetry(override_exit['id'], telemetry_keys=["value"])["value"][0]['value']
                
            
            context.update({
                'active_stops': active_stops,
                'completed_stops': completed_stops,
                'override_entry': str(override_entry),
                'override_exit': str(override_exit),
                }
            ) 
            return render(request, 'administration.html', context)
        else:
            return redirect('/home')

    
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


