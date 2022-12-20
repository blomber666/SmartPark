import logging
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException
#get name from command line
import argparse
from thingsboard_api_tools import TbApi
import time


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

def control_gate(tbapi, gate_name, old_presence, camera_name, plate):
    #get the gate telemetry

        presence = get_car_presence(tbapi, gate_name)

        #print the gate name in green if the gate is open
        gate_string = "entry" if gate_name.split("_")[-1] == "1" else "exit"

        if presence and plate is None:
            #get plate from camera 1
            plate = get_plate(tbapi, camera_name)
            printc("CYAN",f"plate: {plate}")

        if not presence and plate is not None:
            #delete plate
            plate = None

        if presence:
            printc("GREEN",f"{gate_string}")
        else:
            printc("MAGENTA",f"{gate_string}")

        if presence != old_presence:
            if presence:
                printc('YELLOW',f"{gate_name} opened")
            else:
                printc('YELLOW',f"{gate_name} closed")
            return presence, plate

        else:
            return old_presence, plate

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

    #get the entry_gate of the park
    entry_gate_name = "gate_"+park_number+"_1"
    #get the exit_gate of the park
    exit_gate_name = "gate_"+park_number+"_2"

    #get the entry_camera of the park
    entry_camera_name = "camera_"+park_number+"_1"
    #get the exit_camera of the park
    exit_camera_name = "camera_"+park_number+"_2"

    print(f"entry_gate_name: {entry_gate_name}")
    print(f"entry_camera_name: {entry_camera_name}")
    print(f"exit_gate_name: {exit_gate_name}")
    print(f"exit_camera_name: {exit_camera_name}")


    entry_presence = False
    exit_presence = False
    plate = None

    while 1:

        time.sleep(1)

        entry_presence, plate = control_gate(tbapi, entry_gate_name, entry_presence, entry_camera_name, plate)

        #exit_presence = control_gate(tbapi, exit_gate_name, exit_presence, camera_name)

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