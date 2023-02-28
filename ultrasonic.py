#Libraries
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


    def print_results(dist_gate, dist_park, door_telemetry, park_telemetry):
        gate_name = 'GATE_1_1'
        park_name = 'PARK_1_4'
        string = []
        DISTANCE_THRESHOLD = 10

        #door telemetry
        if door_telemetry < DISTANCE_THRESHOLD:
            string.append(['RED_BOLD', gate_name, ' = '])
        else:
            string.append(['GREEN_BOLD', gate_name, ' = '])

        #gate distance
        if dist_gate < DISTANCE_THRESHOLD:
            string.append(['RED_BOLD', dist_gate, ' cm'])
        else:
            string.append(['GREEN_BOLD', dist_gate, ' cm'])

        #tab
        string.append(['WHITE', '\t'])

        #park telemetry
        if park_telemetry < DISTANCE_THRESHOLD:
            string.append(['RED_BOLD', park_name, ' = '])
        else:
            string.append(['GREEN_BOLD', park_name, ' = '])

        #park distance
        if dist_park < DISTANCE_THRESHOLD:
            string.append(['RED_BOLD', dist_park, ' cm'])
        else:
            string.append(['GREEN_BOLD', dist_park, ' cm'])
    
        printc_inline(string)
        
for a in range(0, 100):
    for b in range(100, 0, -1):
        print_results(a, b, a, b)
        time.sleep(0)