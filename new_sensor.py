import logging
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException
#get name from command line
import argparse
from thingsboard_api_tools import TbApi

'''
create a new sensor and add the relation 'CONTAINS' to the park
-make sure the park exists and the sensor does not exist
-make sure the name is in the format: name_PARKID_SENSORID
usage:
python new_sensor.py SENSOR_NAME DEVICE_TYPE
example:
python new_sensor.py sensor_1_1 default
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
    parser.add_argument("name", help="the sensor name like: sensor_1_1", type=str, default="defaultname_1_1")
    parser.add_argument("device_type", help="the value to send 0(occupied) or 1(free)", type=str, default="default")

    opt = parser.parse_args()
    return opt




def main( name, device_type):
    # ThingsBoard REST API URL
    url = "http://192.168.1.197:8080"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "tenant"
    tbapi = TbApi(url, username, password)
    #get the park number from the name (sensor_1_6 -> 1)
    park_number = name.split("_")[-2]

    #get selected profile
    profile = tbapi.get_device_profiles(name=device_type)
    # creating a Device
    device = tbapi.add_device(name, device_type)
    #get the device name
    name = tbapi.get_device_by_id(device['id']['id'])['name']
    printc("GREEN", "\nDevice created:")
    print(name)


    #get park assets
    park = tbapi.get_tenant_asset(name="park_"+park_number)
    #get the park name
    park_name = park['name']


    # Creating relations from device to asset

    relation = tbapi.add_relation(park['id'], device['id'], "Contains")
    printc("GREEN", "\nRelation created:")
    print(park_name, " contains ", name)



if __name__ == '__main__':

    ##MAIN CODE
    opt = parse_opt()
    main(**vars(opt))

