from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

telemetry = { "free": 1} 
#token=0hLg4REX1YGPL2VPDK0Z
#get token from device

client=TBDeviceMqttClient("192.168.1.197", 1883, "WDxuJ3lulcmI2Kd2Ql33")

client.connect()
result = client.send_telemetry(telemetry)

success = result.get() == TBPublishInfo.TB_ERR_SUCCESS

if success:
    print("Telemetry published")
else:
    print("Failed to publish telemetry")



client.disconnect()