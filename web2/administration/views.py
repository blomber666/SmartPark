from django.shortcuts import render
from django.shortcuts import redirect
from stops.models import Stop, Payment
from django.contrib import messages
from thingsboard_api_tools import TbApi
from push_telemetry import main as push_telemetry



def administration(request):
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized')
        return redirect('/')
    else:
        if request.user.is_superuser:
            # ThingsBoard REST API URL
            url = "http://192.168.1.197:8080"
            # Default Tenant Administrator credentials
            username = "tenant@thingsboard.org"
            password = "tenant"
            tbapi = TbApi(url, username, password)
            #get all active stops
            active_stops = Stop.objects.filter(end_time=None)
            #get all completed stops
            completed_stops = Stop.objects.filter(end_time__isnull=False)

            #get the latest telemetry of device named 'door_1_1'
            entry_door = tbapi.get_tenant_device(name='door_1_1')
            entry_door_telemetry = tbapi.get_latest_telemetry(entry_door['id'], telemetry_keys=["open"])
            print(entry_door_telemetry)

            #get the latest telemetry of device named 'door_1_2'
            exit_door = tbapi.get_tenant_device(name='door_1_2')
            exit_door_telemetry = tbapi.get_latest_telemetry(exit_door['id'], telemetry_keys=["open"])
            print(exit_door_telemetry)
            

            context = {
                'active_stops': active_stops,
                'completed_stops': completed_stops,
            }
            return render(request, 'administration.html', context)
        else:
            return redirect('/home')

def override(request):
    '''
    Override the gate:
    push teleemtry  value wiht 'open' or 'close' to the gate
    based on which button inside administration.html is pressed
    '''
    if not request.user.is_authenticated:
        messages.info(request,'HTTP ERROR: 401 - Unauthorized', status=401)
        return redirect('/home')
    else:
        if request.user.is_superuser:
            if request.method == 'POST':

                print(request.POST)
                if 'entry_open' in request.POST:
                    push_telemetry('override_1_1', 'value', 'open')
                elif 'entry_close' in request.POST:
                    push_telemetry('override_1_1', 'value', 'close')
                elif 'entry_normal' in request.POST:
                    push_telemetry('override_1_1', 'value', 'null')
                elif 'exit_open' in request.POST:
                    push_telemetry('override_1_2', 'value', 'open')
                elif 'exit_close' in request.POST:
                    push_telemetry('override_1_2', 'value', 'close')
                elif 'exit_normal' in request.POST:
                    push_telemetry('override_1_2', 'value', 'null')   
                else:
                    print('unknown button')

            else:
                print('not post')
            return redirect('/administration')
        else:
            return redirect('/home')


