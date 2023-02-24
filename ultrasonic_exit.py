#Libraries
import RPi.GPIO as GPIO
import time
import argparse
from thingsboard_api_tools import TbApi
from tb_device_mqtt import TBDeviceMqttClient

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


#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
class Ultrasonic:
    def __init__(self, trigger, echo):
        self.trigger = trigger
        self.echo = echo
        self.id = None
        self.key = 'distance'
        self.token = None
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, False)
        time.sleep(2)
    def get_distance(self):
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)
        StartTime = time.time()
        StopTime = time.time()
        while GPIO.input(self.echo) == 0:
            StartTime = time.time()
        while GPIO.input(self.echo) == 1:
            StopTime = time.time()
        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed * 34300) / 2
        return distance
    def __del__(self):
        GPIO.cleanup()

class Door:
    def __init__(self, green, red):
        self.green = green
        self.red = red
        self.id = None
        GPIO.setup(self.green, GPIO.OUT)
        GPIO.setup(self.red, GPIO.OUT)
        GPIO.output(self.green, False)
        GPIO.output(self.red, False)
    def open(self):
        GPIO.output(self.green, True)
        GPIO.output(self.red, False)
    def close(self):
        GPIO.output(self.green, False)
        GPIO.output(self.red, True)
    def __del__(self):
        GPIO.cleanup()

class Led:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)
    def free(self):
        GPIO.output(self.pin, True)
    def occupied(self):
        GPIO.output(self.pin, False)
    def __del__(self):
        GPIO.cleanup()

gate_1_2 = Ultrasonic(3, 2)
park_1_2 = Ultrasonic(18, 17)
park_light_1_2 = Led(15)
door_1_2 = Door(4, 14)


# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"

tbapi = TbApi(url, username, password)
devices = tbapi.get_tenant_devices()

for d in devices:
    if d['name'] == 'door_1_2':
        door_1_2.id = d['id']
        break

for d in devices:
    if d['name'] == 'sensor_1_2':
        park_1_2.id = d['id']
        break

gate_1_2.token = 'dZ66bXlpJjkx58DOqO2U'
gate_1_2.key = 'distance'
gate_client = TBDeviceMqttClient(host="192.168.1.197", username=gate_1_2.token)
gate_client.connect()
park_1_2.token = 'pVv5GRFwnFGTbCgTzIov'
park_1_2.key = 'distance'
park_client = TBDeviceMqttClient(host="192.168.1.197", username=park_1_2.token)
park_client.connect()


if __name__ == '__main__':
    try:
        while True:
            dist_gate = gate_1_2.get_distance()
            dist_park = park_1_2.get_distance()
            print("Distance GATE_1_2 = %.1f cm" % dist_gate)
            print("Distance PARK_1_2 = %.1f cm" % dist_park)
            gate_client.send_telemetry({gate_1_2.key: dist_gate})
            park_client.send_telemetry({park_1_2.key: dist_park})

            door_telemetry = tbapi.get_telemetry(door_1_2.id, telemetry_keys=["open"])   
            if int(door_telemetry['open'][0]['value']) == 1:
                door_1_2.open()
            else:
                door_1_2.close()

            park_light_telemetry = tbapi.get_telemetry(park_1_2.id, telemetry_keys=["distance"])
            if float(park_light_telemetry['distance'][0]['value']) < 10:
                park_light_1_2.occupied()
            else:
                park_light_1_2.free()

            print("\n\n")
            time.sleep(2)

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        gate_client.disconnect()
        park_client.disconnect()
        GPIO.cleanup()