import logging
# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException



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