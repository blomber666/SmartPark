from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo
#get name from command line
import argparse


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="the sensor name like: sensor_1_1", type=str)
    parser.add_argument("--value", help="the value to send 0(occupied) or 1(free)", type=int)

    opt = parser.parse_args()
    return opt


def main( name, value):

    telemetry = { "free": value} 
    #token=0hLg4REX1YGPL2VPDK0Z
    #get token from device
    sensors = {
        "sensor_1_1": "WDxuJ3lulcmI2Kd2Ql33",
        "sensor_1_2": "4gG56x8GQ3Vlj3RPWq58",
        "sensor_1_3": "pDCSzYjmfqRFIxaQVeEx"
    }
    client=TBDeviceMqttClient("192.168.1.197", 1883,sensors[name])

    client.connect()
    result = client.send_telemetry(telemetry)

    success = result.get() == TBPublishInfo.TB_ERR_SUCCESS

    if success:
        print("Telemetry published", telemetry)
    else:
        print("Failed to publish telemetry")



    client.disconnect()

if __name__ == '__main__':

    ##MAIN CODE
    opt = parse_opt()
    main(**vars(opt))

