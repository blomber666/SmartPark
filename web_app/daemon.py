from datetime import date, datetime, timedelta
from decimal import Decimal
import logging
import re
from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
from tb_rest_client.rest_client_ce import *
from tb_rest_client.rest import ApiException
#get name from command line
import argparse
from thingsboard_api_tools import TbApi
from push_telemetry import main as push_telemetry
import time

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_park.settings')
import django
django.setup()

from parkings.models import Stop, Payment, Statistic
from users.models import User
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
    parser.add_argument("--stats_freq", help="the frequency of the stats in hh:mm", type=str, default="00:01")
    # parser.add_argument("key", help="the key of the value", type=str, default="free")
    # parser.add_argument("value", help="the value to send", type=str, default=1)

    opt = parser.parse_args()
    return opt

def get_car_presence(tbapi, gate_name):
    gate = tbapi.get_device_by_name(name=gate_name)
    telemetry = tbapi.get_telemetry(gate['id'], telemetry_keys=["distance"])
    #get the latest telemetry (the first one)
    distances = telemetry['distance']
    #distances is a list of dictionaries
    #get the ones with the grater value for key "ts"
    distances.sort(key=lambda x: x['ts'])
    distance = float(distances[-1]['value'])
    
    if distance < 20:
        return True
    else:
        return False

def control_entry_gate(tbapi, park_number, old_presence, plate):
    #get the entry_gate of the park
    gate_name = "gate_"+park_number+"_1"
    #get the entry_camera of the park
    camera_name = "camera_"+park_number+"_1"
    #get the gate override name
    override_entry_name = "override_"+park_number+"_1"

    door_name = "door_"+park_number+"_1"

    #get the override telemetry
    override_gate = tbapi.get_device_by_name(name=override_entry_name)
    override = tbapi.get_telemetry(override_gate['id'], telemetry_keys=["value"])
    override_value = override['value'][0]['value']

    if override_value != 'null':
        if override_value == 'open':
            push_telemetry(door_name, 1)
            printc('GREEN',"entry(override)")
            return None, None

        elif override_value == 'close':
            push_telemetry(door_name, 0)
            printc('MAGENTA',"entry(override)")
            return None, None
        
        else:
            printc('RED',"unknown override value, entry gate not active")
            return None, None

    else:
        #get the gate telemetry
        presence = get_car_presence(tbapi, gate_name)
        door = tbapi.get_device_by_name(name=door_name)

        if presence != old_presence:
            if presence and plate is None:
                #get plate from camera 1
                plate = get_plate(tbapi, camera_name)
                if plate is None:
                    printc("RED","plate not found")
                    presence = False

                else:
                    printc("CYAN",f"plate: {plate}")
                    #check if user exists
                    try:
                        user = User.objects.get(username=plate)
                        #save to db without end time
                        #check if the user has already a stop
                        stop = Stop.objects.filter(user=user, end_time=None)
                        if stop:
                            printc('RED',"user already in the park")
                            presence = False
                            plate = None
                        else:
                            stop = Stop.objects.create(user=user, start_time=timezone.now(), end_time=None, park=park_number)

                    #print any exception
                    except User.DoesNotExist:
                        printc("RED", "user does not exist")
                        presence = False
                        plate = None


            door_telemetry = tbapi.get_telemetry(door['id'], telemetry_keys=["open"])
            door_open = True if door_telemetry['open'][0]['value'] == '1' else False

            if not presence and plate is not None:
                #delete plate
                plate = None

            if plate:
                printc('YELLOW',"entry opened")
                push_telemetry(door_name, 1)

            elif door_open:
                printc('YELLOW',"entry closed")
                push_telemetry(door_name, 0)
            #control the gate

        #get door telemetry
        
        door_telemetry = tbapi.get_telemetry(door['id'], telemetry_keys=["open"])
        if door_telemetry['open'][0]['value'] == '1':
            printc('GREEN',"entry")
        else:
            printc('MAGENTA',"entry")

        return presence, plate

def control_exit_gate(tbapi, park_number, old_presence, plate):
    #get the entry_gate of the park
    gate_name = "gate_"+park_number+"_2"
    #get the entry_camera of the park
    camera_name = "camera_"+park_number+"_2"
    #get the gate override name
    override_exit_name = "override_"+park_number+"_2"

    door_name = "door_"+park_number+"_2"

    #get the override telemetry
    override_gate = tbapi.get_device_by_name(name=override_exit_name)
    override = tbapi.get_telemetry(override_gate['id'], telemetry_keys=["value"])
    override_value = override['value'][0]['value']

    if  override_value != 'null':
        if override_value == 'open':
            push_telemetry(door_name, 1)
            printc('GREEN',"exit(override)")
            return True, None

        elif override_value == 'close':
            push_telemetry(door_name, 0)
            printc('MAGENTA',"exit(override)")
            return False, None

        else:
            printc('RED',"unknown override value, exit gate not active")
            return False, None

    else:
        #get the gate telemetry
        presence = get_car_presence(tbapi, gate_name)
        door = tbapi.get_device_by_name(name=door_name)

        #if presence changed or there is someone waiting to exit
        if presence != old_presence:
            if presence and plate is None:
                #get plate from camera 2
                plate = get_plate(tbapi, camera_name)
                if plate is None:
                    printc("RED","plate not found")
                    presence = False
                else:
                    printc("CYAN",f"plate: {plate}")

                    #check if user exists
                    try:
                        user = User.objects.get(username=plate)
                        #check if payed

                        last_stop = Stop.objects.filter(user=user, end_time=None)

                        if len(last_stop) != 1:
                            printc("RED","user entered zero or more than one time")
                            presence = False
                            plate = None
                        else:
                            last_stop = last_stop[0]
                            #find the payment with the same stop id
                            payment = Payment.objects.filter(stop=last_stop)
                            #TODO check if the payment_time is less than 15 minutes ago
                            if payment :
                                printc("GREEN",f"payed{payment}")
                                if payment[0].payment_time < (timezone.now() - timedelta(minutes=15)):
                                    printc("RED","trying to exit after 15 minutes, for this time we don't charge")
                                #update the stop
                                last_stop.end_time = timezone.now()
                                last_stop.save()
                            else:
                                printc("RED","not payed")
                                plate = None
                                presence = False
                    #print any exception
                    except User.DoesNotExist:
                        printc("RED", "user does not exist")
                        presence = False
                        plate = None

                    
            door_telemetry = tbapi.get_telemetry(door['id'], telemetry_keys=["open"])
            door_open = True if door_telemetry['open'][0]['value'] == '1' else False

            if not presence and plate is not None:
                #delete plate
                plate = None
            if plate:
                printc('YELLOW',"exit opened")
                push_telemetry(door_name,1)
            elif door_open:
                printc('YELLOW',"exit closed")
                push_telemetry(door_name, 0)

        #get door telemetry
        door_telemetry = tbapi.get_telemetry(door['id'], telemetry_keys=["open"])
        if door_telemetry['open'][0]['value'] == '1':
            printc('GREEN',"exit")
        else:
            printc('MAGENTA',"exit")

        return presence, plate

def get_plate(tbapi, camera_name):
    i = 0
    #try to get the plate for 10 seconds
    while i < 5:
        camera = tbapi.get_device_by_name(name=camera_name)
        telemetry = tbapi.get_telemetry(camera['id'], telemetry_keys=["plate"])
        #get the latest telemetry (the first one)
        plates = telemetry['plate']
        #plates is a list of dictionaries
        #get the ones with the grater value for key "ts"
        plates.sort(key=lambda x: x['ts'])
        #if the time is less than 5 seconds ago
        if time.time() - plates[-1]['ts']/1000 < 5:
            plate = plates[-1]['value']
            return plate
        #wait 1 second
        time.sleep(1)
        i+=1
    return None

def send_stats(stats, park_number):
    '''
    send stats to the server.
    Create a new statistic model and save it to the database
    '''
    #get all stops for the park that has the start_time today
    all_stops = Stop.objects.filter(park=park_number, start_time__date=datetime.today().date())
    #get the completed stops for the park that has the start_time today
    completed_stops = Stop.objects.filter(park=park_number, start_time__date=datetime.today().date(), end_time__isnull=False)
    if len(all_stops) > 0:

        if len(completed_stops) > 0:
            #calculate the total income by summing the amount of all completed stops,
            #payment has a foreign key to the stop
            total_income = sum([payment.amount for payment in Payment.objects.filter(stop__in=completed_stops)])

            #calculate the average time of the completed stops
            completed_time_list = [stop.end_time - stop.start_time for stop in completed_stops] #type: [timedelta]
            #create a timedelta object with the value of 0
            timedelta_zero = datetime.now().replace(hour=0, minute=0, second=0) - datetime.now().replace(hour=0, minute=0, second=0)
            completed_total_time = sum(completed_time_list, timedelta_zero)

            #calculate the average time of the completed stops 
            average_time = (completed_total_time / completed_stops.count())

            #calculate the average price of the completed stops
            average_price = total_income / completed_stops.count()
            #calculate the average income per hour
            average_income_per_hour = total_income / (datetime.now() - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).seconds * 3600
        else:
            total_income = 0
            #average time mjust be a timedelta object
            average_time = datetime.now() - datetime.now()
            average_price = 0
            average_income_per_hour = 0

        #calculate the average stops per hour
        average_stops_per_hour = len(all_stops) / (datetime.now() - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).seconds * 3600
        
        #check the types of the values
        #assert total_income is a int, float or decimal.Decimal
        assert isinstance(total_income, (int, float, Decimal)), f"total_income is not a number, it is {type(total_income)}"
        assert isinstance(len(all_stops), int), f"total_stops is not an integer, it is {type(len(all_stops))}"
        assert isinstance(len(completed_stops), int), f"completed_stops is not an integer, it is {type(len(completed_stops))}"
        assert isinstance(average_time, timedelta), f"average_time is not a timedelta, it is {type(average_time)}"
        assert isinstance(average_price, (int, float, Decimal)), f"average_price is not a number, it is {type(average_price)}"
        assert isinstance(average_income_per_hour, (int, float, Decimal)), f"average_income_per_hour is not a number, it is {type(average_income_per_hour)}"
        assert isinstance(average_stops_per_hour, (int, float, Decimal)), f"average_stops_per_hour is not a number, it is {type(average_stops_per_hour)}"

        
        #update the stats model
        stats.total_income = total_income
        stats.total_stops = len(all_stops)
        stats.completed_stops = len(completed_stops)
        stats.active_stops = len(all_stops) - len(completed_stops)
        stats.average_time = average_time
        stats.average_price = average_price
        stats.average_income_per_hour = average_income_per_hour
        stats.average_stops_per_hour = average_stops_per_hour
        #change the date to now
        stats.date = datetime.now().date()
        #save the stats
        stats.save()
        printc("GREEN","stats sent")


def main(park_name, stats_freq):
    printc("GREEN","starting daemon for park:",park_name)
    #get park assets
    park = tbapi.get_tenant_asset(name=park_name)
    #get park number
    park_number = park['name'].split("_")[1]

    #check that stats_freq is in the correct format
    assert re.match(r"^\d{2}:\d{2}$", stats_freq), "stats_freq must be in the format hh:mm"
    #convert to datetime
    stats_freq = datetime.strptime(stats_freq, "%H:%M").time()
    printc('CYAN',f"stats_freq: {stats_freq}")
    #get the time of the last stats sent
    stats_time = datetime.now().time()

    entry_presence = False
    exit_presence = False
    entry_plate = None
    exit_plate = None
    #get the statistics for the park for today
    stats = Statistic.objects.filter(park=park_number, date=datetime.today().date())
    assert len(stats) <= 1, "there are more than one stats for today, NO BUONO"
    if len(stats) == 0:
        #create a new statistic
        #set average_time to 0 but as timedelta
        average_time = datetime.now() - datetime.now()
        stats = Statistic(park=park_number, date=datetime.today().date(), total_income=0,\
                total_stops=0, completed_stops=0, active_stops=0, average_time=average_time,\
                average_price=0, average_income_per_hour=0, average_stops_per_hour=0)
        stats.save()
        printc('GREEN',"created new stats for today")
    else:
        stats = stats[0]
        printc('GREEN',"found stats for today") 

    while 1:
        #create new stats if it is a new day
        #remove the time from the stats_date
        # stats_date = stats.date.date()
        if datetime.today().date() != stats.date:
            #send last stats for the previous day
            send_stats(stats, park_number)
            printc('GREEN',"sent last stats for the previous day")
            #create a new statistic for today
            #set average_time to 0 but as timedelta
            average_time = datetime.now() - datetime.now()
            stats = Statistic(park=park_number, date=datetime.today().date(), total_income=0,\
                total_stops=0, completed_stops=0, active_stops=0, average_time=average_time,\
                average_price=0, average_income_per_hour=0, average_stops_per_hour=0)
            stats.save()
            printc('GREEN',"created new stats for today")

        #every stats_freq send stats to the server
        if datetime.now().time() >= stats_time:
            send_stats(stats, park_number)
            #update the stats_time by adding stats_freq to it
            stats_time = (datetime.combine(date.today(), stats_time) + timedelta(hours=stats_freq.hour, minutes=stats_freq.minute)).time()
            printc('CYAN',f"next_stats_update: {stats_time}")

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