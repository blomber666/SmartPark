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

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="the sensor name like: sensor_1_1", type=str, default="sensor_1_1")
    parser.add_argument("key", help="the key of the value", type=str, default="free")
    parser.add_argument("value", help="the value to send", type=str, default=1)

    # opt = parser.parse_args(args=['sensor_1_1', 'free', '1'])
    opt = parser.parse_args()
    return opt


def main(name, key, value):
    # ThingsBoard REST API URL
    url = "http://192.168.1.197:8080"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "tenant"
    tbapi = TbApi(url, username, password)
    devices = tbapi.get_tenant_device()

    #find the device using the name
    for d in devices:
        if d['name'] == name:
            device = d
            break

    token = tbapi.get_device_token(device)

    telemetry = { str(key): value} 

    result = tbapi.send_telemetry(token, telemetry)
    #check if result is an empty dict
    if not result:
        printc("OK", "Sent ", telemetry, "to device: ", name)


if __name__ == '__main__':

    ##MAIN CODE
    opt = parse_opt()
    main(**vars(opt))

