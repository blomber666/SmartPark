#Libraries
import sys
import RPi.GPIO as GPIO
import time
import argparse
from thingsboard_api_tools import TbApi
from tb_device_mqtt import TBDeviceMqttClient
if __name__ == '__main__':
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


        BG_PURPLE = '\033[48;5;57m'      #That is, \033[48;5;<BG COLOR>m
        RAINBOW = '\033[48;5;57m'      #That is, \033[48;5;<BG COLOR>m
        PURPLE = '\033[38;5;206m'     #That is, \033[38;5;<FG COLOR>m
        BOLD = '\033[1m'
        RED_BOLD = '\033[1;31m'
        GREEN_BOLD = '\033[1;32m'
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

    def printc_inline(strings):
        #delete all characters in line
        print('\033[2K', end='\r')
        for i, arg in enumerate(strings):
            color = arg[0]
            texts = arg[1::]
            c = getattr(bcolors,color)
            text = ' '.join(map(str, texts))
            #if last argument
            if i != len(strings)-1:
                print(c + text + bcolors.END, end='')
            else:
                print(c + text + bcolors.END, end='\r')
            #flush stdout
            sys.stdout.flush()


    def print_results(dist_gate, dist_park, door_telemetry):
        gate_name = 'GATE_1_1'
        park_name = 'PARK_1_4'
        string = []
        DISTANCE_THRESHOLD = 10

        #door telemetry
        if door_telemetry == 0:
            string.append(['RED_BOLD', 'DOOR'])
        else:
            string.append(['GREEN_BOLD', 'DOOR'])

        #tab
        string.append(['WHITE', '     '])

        #gate distance
        if dist_gate < DISTANCE_THRESHOLD:
            string.append(['RED_BOLD', gate_name, '=', dist_gate, ' cm'])
        else:
            string.append(['GREEN_BOLD', gate_name, '=', dist_gate, ' cm'])

        #tab
        string.append(['WHITE', '     '])

        #park telemetry
        if dist_park < DISTANCE_THRESHOLD:
            string.append(['RED_BOLD', park_name, '=', dist_park, ' cm'])
        else:
            string.append(['GREEN_BOLD', park_name, '=', dist_park, ' cm'])
    
        printc_inline(string)
        #flush stdout
        sys.stdout.flush()

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

    printc('RAINBOW', 'Starting control of gate_1_1 and park_1_4')
    gate_1_1 = Ultrasonic(3, 2)
    park_1_4 = Ultrasonic(18, 17)
    park_light_1_4 = Led(15)
    door_1_1 = Door(4, 14)

    # ThingsBoard REST API URL
    url = "http://192.168.1.197:8080"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "tenant"

    tbapi = TbApi(url, username, password)
    devices = tbapi.get_tenant_devices()

    for d in devices:
        if d['name'] == 'door_1_1':
            door_1_1.id = d['id']
            break

    for d in devices:
        if d['name'] == 'sensor_1_4':
            park_1_4.id = d['id']
            break

    gate_1_1.token = 'N3SVjK5kG3VHe33lM1C5'
    gate_1_1.key = 'distance'
    gate_client = TBDeviceMqttClient(host="192.168.1.197", username=gate_1_1.token)
    gate_client.connect()
    park_1_4.token = '58pQDxOT9VColdN8kyXH'
    park_1_4.key = 'distance'
    park_client = TBDeviceMqttClient(host="192.168.1.197", username=park_1_4.token)
    park_client.connect()


    try:
        while True:
            dist_gate = gate_1_1.get_distance()
            dist_park = park_1_4.get_distance()
            
            gate_client.send_telemetry({gate_1_1.key: dist_gate})
            park_client.send_telemetry({park_1_4.key: dist_park})

            door_telemetry = tbapi.get_telemetry(door_1_1.id, telemetry_keys=["open"]) 
            door_telemetry = int(door_telemetry['open'][0]['value'])
            if door_telemetry == 1:
                door_1_1.open()
            else:
                door_1_1.close()

            park_telemetry = tbapi.get_telemetry(park_1_4.id, telemetry_keys=["distance"])
            park_telemetry = float(park_telemetry['distance'][0]['value'])
            if park_telemetry < 10:
                park_light_1_4.occupied()
            else:
                park_light_1_4.free()

            print_results(dist_gate, dist_park, door_telemetry)
            #flush stdout
            sys.stdout.flush()
            
            time.sleep(0.5)

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")


    finally:
        printc("WARNING", "Terminating...")
        gate_client.disconnect()
        park_client.disconnect()
        GPIO.cleanup()