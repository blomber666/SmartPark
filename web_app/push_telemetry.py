import argparse
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
import time

'''
send a telemetry to a device
usage:
python push_telemetry.py DEVICE_NAME VALUE
example:
python push_telemetry.py sensor_1_1 323
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
    parser.add_argument("name", help="the sensor name like: sensor_1_1", type=str, default="sensor_1_1")
    parser.add_argument("value", help="the value to send", type=str, default=1)

    # opt = parser.parse_args(args=['sensor_1_1', '111'])
    opt = parser.parse_args()
    return opt

def on_publish(client,userdata,result):             #create function for callback
    printc("OK", "data published \r")

def main(name, value):
    tokens = {  
        'sensor_1_1': '3bPMNFmgEXcQoZvSiN8T',
        'sensor_1_2': 'pVv5GRFwnFGTbCgTzIov',
        'sensor_1_3': 'RqJ6uZp9jG8yUSVeLTuZ',
        'sensor_1_4': '58pQDxOT9VColdN8kyXH',
        'sensor_1_5': 'h4u8ZfgKuL8t7mz3Ugx9',
        'sensor_1_6': 'C4u05P3caWhMkZir9UAL',
        'sensor_1_7': 'kUrgBYUk9iuWJAaynxEb',
        'sensor_1_8': 'T4A6doiYZDt3qlDl9PYK',
        'camera_1_1': 'HbyEW9wZcjBXOBiVfpYg',					
        'camera_1_2': 'rwmbIw7vjUCXy6iDMC1q',					
        'door_1_1': '4yr64n5rydgwfD75xEvE',					
        'door_1_2': 'wIEXGMhF5MGf0oXBREha',					
        'gate_1_1': 'N3SVjK5kG3VHe33lM1C5',					
        'gate_1_2': 'dZ66bXlpJjkx58DOqO2U',					
        'override_1_1':	'LYvfIgTdAD84yuAZrU5l',				
        'override_1_2': 'lpywCZFRo3Ym9NOc0Pft',
    }
    keys = {
        'sensor_1_1': 'distance',
        'sensor_1_2': 'distance',
        'sensor_1_3': 'distance',
        'sensor_1_4': 'distance',
        'sensor_1_5': 'distance',
        'sensor_1_6': 'distance',
        'sensor_1_7': 'distance',
        'sensor_1_8': 'distance',
        'camera_1_1': 'plate',
        'camera_1_2': 'plate',
        'door_1_1': 'open',
        'door_1_2': 'open',
        'gate_1_1': 'distance',
        'gate_1_2': 'distance',
        'override_1_1': 'value',
        'override_1_2': 'value',
    }

    try:
        token = tokens[name] #Token of the device
    except:
        printc("FAIL", "device name not found")

    key = keys[name] #Key of the telemetry
    telemetry = {key: value} #Telemetry to send
    client = TBDeviceMqttClient(host="192.168.1.197", username=token)
    # Connect to ThingsBoard
    client.connect()
    #wait until connection is established or timeout
    retries = 5
    while not client.is_connected() and retries > 0:
        time.sleep(0.5)
        retries -= 1
    # Sending telemetry and checking the delivery status (QoS = 1 by default)
    if client.is_connected():
        client.send_telemetry(telemetry)
        printc("OK", f'Sent {key} = {value} to {name}')
    else:
        printc("FAIL", "connection failed")
    # Disconnect from ThingsBoard
    client.disconnect()


if __name__ == '__main__':
    opt = parse_opt()
    main(**vars(opt))

# names  = [
#     'sensor_1_1',
#     'sensor_1_2',
#     'sensor_1_3',
#     'sensor_1_4',
#     'sensor_1_5',
#     'sensor_1_6',
#     'sensor_1_7',
#     'sensor_1_8',
#     'camera_1_1',
#     'camera_1_2',
#     'door_1_1',
#     'door_1_2',
#     'gate_1_1',
#     'gate_1_2',
#     'override_1_1',
#     'override_1_2',
# ]
# values = [
#     '1',    
#     '2',
#     '3',
#     '4',
#     '5',
#     '6',
#     '7',
#     '8',
#     'AA111AA',
#     'BB222BB',
#     '1',
#     '0',
#     '1',
#     '0',
#     'null',
#     'null',
# ]