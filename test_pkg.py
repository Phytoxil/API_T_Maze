import mqtt_device.common as md
from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.remote.client import ApplicationClient

if __name__ == "__main__":
    mqtt_client = MQTTClient(broker_ip="192.168.24.8", broker_port=1883)
    client = ApplicationClient(environment_name="souris_city", id_env="01", client_id="my_client", mqtt_client=mqtt_client)

    client.connect()

    client.wait_until_ended()
    # init(*sys.argv[1:])  # type: ignore
