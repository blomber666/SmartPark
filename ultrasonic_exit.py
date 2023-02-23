#Libraries
import RPi.GPIO as GPIO
import time
import argparse
from thingsboard_api_tools import TbApi
from push_telemetry import main as push_telemetry

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


#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
class Ultrasonic:
    def __init__(self, trigger, echo):
        self.trigger = trigger
        self.echo = echo
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

gate_1_2 = Ultrasonic(3, 2)
park_1_2 = Ultrasonic(18, 17)
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
        door_1_2 = d
        break

if __name__ == '__main__':
    try:
        while True:
            try:
                dist_gate = gate_1_2.get_distance()
                dist_park = park_1_2.get_distance()
                print("Measured Distance GATE = %.1f cm" % dist_gate)
                print("Measured Distance PARK = %.1f cm" % dist_park)
                push_telemetry('gate_1_2', dist_gate)
                push_telemetry('sensor_1_4', dist_park)

                door_1_2_telemetry = tbapi.get_telemetry(door_1_2['id'], telemetry_keys=["open"])   

                if int(door_1_2_telemetry['open'][0]['value']) == 1:
                    door_1_2.open()
                else:
                    door_1_2.close()
                print("\n\n")
                time.sleep(0.5)
            except OSError as e:
                #continue the while loop
                printc("RED", "OSError: ", e)
                continue
            


        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()