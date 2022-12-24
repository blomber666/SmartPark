import logging
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException
#get name from command line
import argparse
from thingsboard_api_tools import TbApi
import time
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_django.settings')

import django
django.setup()
from stops.models import Stop, Payment

from django.utils import timezone



'''
send a telemetry to a device
usage:
python push_telemetry.py DEVICE_NAME KEY VALUE
example:
python push_telemetry.py sensor_1_1 1
'''
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    END = '\033[0m' #RESET COLOR
    CYAN = '\033[36m'
    GREEN = '\033[32m' # Dark Green
    YELLOW = '\033[33m' # Dark Yellow
    RED = '\033[31m' # Dark Red
    BLUE = '\033[34m' # Dark Blue
    MAGENTA = '\033[35m' # Dark Magenta
    WHITE = '\033[37m' # Dark White
    BLACK = '\033[30m' # Dark Black
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    INVISIBLE = '\033[08m'
    REVERSE = '\033[07m'


def printc(*args):
    color = args[0]
    strings = args[1::]
    c = getattr(bcolors,color)
    string=' '.join(map(str, strings))
    print(c + string + bcolors.END)

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--park_name", help="the park name like: park_1", type=str, default="park_1")
    # parser.add_argument("key", help="the key of the value", type=str, default="free")
    # parser.add_argument("value", help="the value to send", type=str, default=1)

    opt = parser.parse_args()
    return opt

def get_car_presence(tbapi, gate_name):
    gate = tbapi.get_tenant_device(name=gate_name)
    telemetry = tbapi.get_telemetry(gate['id'], telemetry_keys=["distance"])
    #get the latest telemetry (the first one)
    distances = telemetry['distance']
    #distances is a list of dictionaries
    #get the ones with the grater value for key "ts"
    distances.sort(key=lambda x: x['ts'])
    distance = float(distances[-1]['value'])
    
    if distance < 1:
        return True
    else:
        return False

def control_entry_gate(tbapi, park_number, old_presence, plate):
    #get the entry_gate of the park
    gate_name = "gate_"+park_number+"_1"
    #get the entry_camera of the park
    camera_name = "camera_"+park_number+"_1"

    #get the gate telemetry
    presence = get_car_presence(tbapi, gate_name)

    if presence != old_presence:
        if presence and plate is None:
            #get plate from camera 1
            plate = get_plate(tbapi, camera_name)
            printc("CYAN",f"plate: {plate}")
            #save to db withou end time
            stop = Stop(plate=plate, start_time=0, end_time=None)
            stop.save()

        if not presence and plate is not None:
            #delete plate
            plate = None

        if plate:
            printc('YELLOW',"entry opened")
        else:
            printc('YELLOW',"entry closed")
        #control the gate

    if plate:
        printc("GREEN", "entry")
    else:
        printc("MAGENTA","entry")

    return presence, plate

def control_exit_gate(tbapi, park_number, old_presence, plate):

    #get the entry_gate of the park
    gate_name = "gate_"+park_number+"_2"
    #get the entry_camera of the park
    camera_name = "camera_"+park_number+"_2"

    #get the gate telemetry
    presence = get_car_presence(tbapi, gate_name)

    if presence != old_presence:
        if presence and plate is None:
            #get plate from camera 2
            plate = get_plate(tbapi, camera_name)
            printc("CYAN",f"plate: {plate}")

            #check if payed
            last_stop = Stop.objects.filter(plate=plate).order_by('-start_time')
            assert len(last_stop) > 0 , 'someone is trying to exit without entering'
            last_stop = last_stop[0]

            #find the payment with the same stop id
            payment = Payment.objects.filter(stop_id=last_stop.stop_id)
            #TODO check if the payment_time is less than 15 minutes ago
            if payment:
                printc("GREEN",f"payed{payment}")
                #update the stop
                last_stop.end_time = timezone.now()
                last_stop.save()
            else:
                printc("RED","not payed")
                plate = None
                
        if not presence and plate is not None:
            #delete plate
            plate = None
        if plate:
            printc('YELLOW',"exit opened")
        else:
            printc('YELLOW',"exit closed")

    if plate:
        printc("GREEN","exit")
    else:
        printc("MAGENTA","exit")

    return presence, plate
     

def get_plate(tbapi, camera_name):
    camera = tbapi.get_tenant_device(name=camera_name)
    telemetry = tbapi.get_telemetry(camera['id'], telemetry_keys=["plate"])
    #get the latest telemetry (the first one)
    plates = telemetry['plate']
    #plates is a list of dictionaries
    #get the ones with the grater value for key "ts"
    plates.sort(key=lambda x: x['ts'])
    plate = plates[-1]['value']
    return plate

def main(park_name):
    printc("GREEN","starting daemon for park:",park_name)
    #get park assets
    park = tbapi.get_tenant_asset(name=park_name)
    #get park number
    park_number = park['name'].split("_")[1]

    entry_presence = False
    exit_presence = False
    entry_plate = None
    exit_plate = None

    while 1:

        time.sleep(1)

        entry_presence, entry_plate = control_entry_gate(tbapi, park_number, entry_presence, entry_plate)

        exit_presence, exit_plate = control_exit_gate(tbapi, park_number, exit_presence, exit_plate)

        print("\n")






if __name__ == '__main__':
 
    # ThingsBoard REST API URL
    url = "http://192.168.1.197:8080"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "tenant"
    tbapi = TbApi(url, username, password)

    opt = parse_opt()
    main(**vars(opt))