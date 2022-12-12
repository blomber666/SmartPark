from tb_device_mqtt import TBDeviceMqttClient, TBPublishInfo

telemetry = { "ID_park": '001' , "free": False} 
#token=0hLg4REX1YGPL2VPDK0Z
client=TBDeviceMqttClient("10.1.22.45", 1883, "xeS2FCOc5A6K54LalAp9")

client.connect()
result = client.send_telemetry(telemetry)

success = result.get() == TBPublishInfo.TB_ERR_SUCCESS

if success:
    print("Telemetry published")
else:
    print("Failed to publish telemetry")



client.disconnect()