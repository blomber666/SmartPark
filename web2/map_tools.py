import logging
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException
import cv2 #pip install opencv-python
import matplotlib.pyplot as plt #pip install matplotlib
from matplotlib import patches #pip install matplotlib
import numpy as np #pip install numpy
import math #pip install math



logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# ThingsBoard REST API URL
url = "http://192.168.1.197:8080"
# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"
import logging
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException


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
        cv2.polylines(map, np.array([vertices]), True, (255,255,255), 1)
        width = max([vertex[0] for vertex in vertices]) - min([vertex[0] for vertex in vertices])
        x = rectangle[0][0] + width/3
        #draw the text at middle x and y
        cv2.putText(map, key, (int(x),int((rectangle[0][1]+rectangle[-1][1])/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 1, cv2.LINE_AA)
        
    

    # Creating the REST client object with context manager to get auto token refresh
    with RestClientCE(base_url=url) as rest_client:
        try:
            # Auth with credentials
            rest_client.login(username=username, password=password)

            # retrieve telemetry for sensor_1_1
            telemetry = rest_client.get_latest_timeseries(EntityId("69482ca0-7d65-11ed-b021-03cf31a5a03e","DEVICE" ))
            print(telemetry)
            
            #get park assets
            parks = []
            parks_retrieved = rest_client.get_tenant_assets(page_size=100, page=0, type="park").data
            for park in parks_retrieved:
                contained_devices = rest_client.find_info_by_from(park.id.id, park.id.entity_type, "CONTAINS" )
                parks.append({"name": park.name, "id": park.id.id, "devices": [
                    {"name": device.to_name, "id": device.to.id} for device in contained_devices
                ]})

            #get the park_1 devices attributes
            for device in parks[0]['devices']:

                telemetry = rest_client.get_latest_timeseries(EntityId(device['id'],"DEVICE" ))
                #get the position of the device using id from positions
                positions[device['name'][-1]]

                print(device['name'],telemetry['free'])

                #if the device is free, fill a polygon with green
                if int(telemetry['free'][0]['value']):
                    overlay = map.copy()
                    cv2.fillPoly(overlay, [np.array(positions[device['name'][-1]])], (93, 252, 136))
                    alpha = 0.5
                    map = cv2.addWeighted(overlay, alpha, map, 1-alpha, 0)
            #save the map as png
            cv2.imwrite("web2/parkings/static/park_1.png", map)
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
        except ApiException as e:
            logging.exception(e)