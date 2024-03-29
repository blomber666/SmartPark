import logging
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from thingsboard_api_tools import TbApi
import cv2 #pip install opencv-python
# import matplotlib.pyplot as plt #pip install matplotlib
# from matplotlib import patches #pip install matplotlib
import numpy as np #pip install numpy
import math #pip install math


# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"

DISTANCE_THRESHOLD = 0.5 #in centimeters

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def generate_map(filename):
    '''generate a png map from a json file
    and  the telemetry of the devices
    filename: the json file
    each element of the json file is a rectangle
    the rectangle is defined by the 4 vertices'''
    import json
    with open(filename) as f:
        positions = json.load(f)

    #multiply the coordinates by SCALE_POSITONS to have a better resolution
    SCALE_POSITONS = 100
    for rectangle in positions.values():
        for vertex in rectangle:
            vertex[0] *= SCALE_POSITONS
            vertex[1] *= SCALE_POSITONS




    #rectangles is a dictionar where the key is the name of the rectangle
    #and the value is a list of 4 vertices
    #each vertex is a list of 2 values: x and y
    #find the min and max values of x and y
    min_x = min([min([vertex[0] for vertex in rectangle]) for rectangle in positions.values()])
    max_x = max([max([vertex[0] for vertex in rectangle]) for rectangle in positions.values()])
    min_y = min([min([vertex[1] for vertex in rectangle]) for rectangle in positions.values()])
    max_y = max([max([vertex[1] for vertex in rectangle]) for rectangle in positions.values()])

    #add a margin of 10%, at least 1 pixel
    margin_x = max(1,(max_x-min_x)//10)
    margin_y = max(1,(max_y-min_y)//10)

        #sort the vertices in a clockwise order
    for rectangle in positions.values():
        #find the center of the rectangle
        center = [sum([vertex[0] for vertex in rectangle])/4,sum([vertex[1] for vertex in rectangle])/4]
        #sort the vertices in a clockwise order
        rectangle.sort(key=lambda vertex: math.atan2(vertex[1]-center[1],vertex[0]-center[0]))
        #translate the vertices given the margin
        for vertex in rectangle:
            vertex[0] += margin_x
            vertex[1] += margin_y


    #create a numpy array of the size of the map
    map = np.zeros((int(max_y-min_y+2*margin_y),int(max_x-min_x+2*margin_x),3), np.uint8)

    #fill the map with grey
    map[:,:] = (128,128,128)

    #draw the rectangles with their key as text
    for key, rectangle in positions.items():
        #get the vertices of the rectangle
        vertices = [(vertex[0]-min_x,vertex[1]-min_y) for vertex in rectangle]
        #draw the rectangle border
        cv2.polylines(map, np.array([vertices]), True, (255,255,255), 3)
        width = max([vertex[0] for vertex in vertices]) - min([vertex[0] for vertex in vertices])
        x = rectangle[0][0] + width/3
        #draw the text at middle x and y
        cv2.putText(map, key, (int(x),int((rectangle[0][1]+rectangle[-1][1])/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3, cv2.LINE_AA)


    # ThingsBoard REST API URL
    url = "http://192.168.1.197:8080"
    # Default Tenant Administrator credentials
    username = "tenant@thingsboard.org"
    password = "tenant"
    tbapi = TbApi(url, username, password)


    #get park assets
    park_name = filename.split("/")[-1].split(".")[0]
    park = tbapi.get_tenant_asset(name=park_name)

    related_devices = tbapi.get_tenant_devices('sensor_1')

    sensor_counter = 0
    free_counter = 0
    for device in related_devices:
        device_type = device['type']
        
        if device_type == "park_sensor":
            name = device['name']
            sensor_counter += 1
            telemetry = tbapi.get_telemetry(device['id'], telemetry_keys=["distance"])
            #get the latest free attribute
            distance = telemetry['distance'][0]['value']

            print(name,distance)

            free = float(distance) > DISTANCE_THRESHOLD
            #if the device is free, fill a polygon with green
            if int(free):
                free_counter += 1
                overlay = map.copy()
                cv2.fillPoly(overlay, [np.array(positions[name[-1]])], (93, 252, 136))
                alpha = 0.5
                map = cv2.addWeighted(overlay, alpha, map, 1-alpha, 0)
    #save the map as png
    cv2.imwrite("media/park_1.png", map)
    #save free sensors and total sensors in a file, one per line
    with open("media/park_1.txt", "w") as f:
        f.write(f'{free_counter}\n')
        f.write(f'{sensor_counter}')
        
        

            #attributes = rest_client.get_attributes(EntityId("69482ca0-7d65-11ed-b021-03cf31a5a03e","DEVICE" ))
            
            # Creating an Asset
            # asset = Asset(name="Building 1", type="building")
            # asset = rest_client.save_asset(asset)

            # logging.info("Asset was created:\n%r\n", asset)

            # # creating a Device
            # device = Device(name="Thermometer 1", type="thermometer")
            # device = rest_client.save_device(device)

            # logging.info(" Device was created:\n%r\n", device)

            # # Creating relations from device to asset
            # relation = EntityRelation(_from=asset.id, to=device.id, type="Contains")
            # relation = rest_client.save_relation(relation)

            #logging.info(" Relation was created:\n%r\n", relation)
    return free_counter, sensor_counter

if __name__ == "__main__":
    generate_map('web2/parkings/static/park_1.json')


