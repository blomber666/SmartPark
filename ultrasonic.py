#Libraries
import RPi.GPIO as GPIO
import time
import argparse
from thingsboard_api_tools import TbApi

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

sensor1 = Ultrasonic(18, 24)
sensor2 = Ultrasonic(20, 21)
door1 = Door(25, 8)
door2 = Door(16, 12)

# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"

tbapi = TbApi(url, username, password)
devices = tbapi.get_tenant_device()

#find the device using the name
for d in devices:
    if d['name'] == 'gate_1_1':
        gate_1_1 = d
        break
gate_1_1_token = tbapi.get_device_token(gate_1_1)

for d in devices:
    if d['name'] == 'gate_1_2':
        gate_1_2 = d
        break
gate_1_2_token = tbapi.get_device_token(gate_1_2)

for d in devices:
    if d['name'] == 'door_1_1':
        door_1_1 = d
        break

for d in devices:
    if d['name'] == 'door_1_2':
        door_1_2 = d
        break


if __name__ == '__main__':
    try:
        while True:
            dist1 = sensor1.get_distance()
            dist2 = sensor2.get_distance()
            print("Measured Distance 1 = %.1f cm" % dist1)
            print("Measured Distance 2 = %.1f cm" % dist2)

            telemetry_1 = { str('distance'): dist1} 
            result_1 = tbapi.send_telemetry(gate_1_1_token, telemetry_1)
            #check if result is an empty dict
            if not result_1:
                printc("OK", "Sent ", telemetry_1, "to device: ", gate_1_1['name'])

            #do the same for the second device
            telemetry_2 = { str('distance'): dist2}
            result_2 = tbapi.send_telemetry(gate_1_2_token, telemetry_2)
            #check if result is an empty dict
            if not result_2:
                printc("OK", "Sent ", telemetry_2, "to device: ", gate_1_2['name'])

            door_1_1_telemetry = tbapi.get_telemetry(door_1_1['id'], telemetry_keys=["open"])   
            door_1_2_telemetry = tbapi.get_telemetry(door_1_2['id'], telemetry_keys=["open"])

            if int(door_1_1_telemetry['open'][0]['value']) == 1:
                door1.open()
            else:
                door1.close()

            if int(door_1_2_telemetry['open'][0]['value']) == 1:
                door2.open()
            else:
                door2.close()
            print("\n\n")
            time.sleep(0.5)

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()