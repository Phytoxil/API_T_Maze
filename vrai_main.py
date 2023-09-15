from pathlib import Path
from unittest.mock import Mock

from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.local.client import LocalClient
from mqtt_device.remote.client import ApplicationClient
from transition_doors.remote_transition_doors import RemoteTransitionDoors

from appli import T_Maze
from datasouriscamera.devices import Local_T_Maze, RemoteBottle, TrackingWriter
from datasouriscamera.motion_detector import StateReader

SERIAL_PORT = 'COM5'  # Remplacez par le bon port série
BAUD_RATE = 9600


def main():
    broker_ip = "192.168.24.120"
    remote_client = ApplicationClient(client_id="app_client", environment_name="souris_city", id_env="01", mqtt_client=MQTTClient(broker_ip=broker_ip))
    local_client = LocalClient(environment_name="souris_city",id_env="01",client_id="T_Maze", mqtt_client=MQTTClient(broker_ip=broker_ip))
    remote_client.connect()
    #writer = TrackingWriter(r"C:\Users\SocialCage\Documents\data_cam")
    writer = Mock()
    #writer = r"C:\Users\SocialCage\Documents\data_cam"
    #bottle_right = Mock()
    bottle_right = remote_client.get_remote_device(device_id="bottle_right").as_type(RemoteBottle)
    bottle_left = remote_client.get_remote_device(device_id="bottle_left").as_type(RemoteBottle)
    #bottle_left = Mock()

    #door = Mock()
    door = remote_client.get_remote_device(device_id="transition_door_t").as_type(RemoteTransitionDoors)
    sr = StateReader(port_com=SERIAL_PORT, baud_rate=BAUD_RATE)

    # motion_detector = MotionDetector(state_reader=sr)

    app = T_Maze(camera=sr, bottle_left=bottle_left, bottle_right=bottle_right, gate=door, writer=writer)
    local_t_maze = Local_T_Maze(device_id="T_Maze", t_maze=app)
    local_client.connect()
    local_client.add_local_device(local_t_maze)

    app.start()

if __name__ == '__main__':
    main()
