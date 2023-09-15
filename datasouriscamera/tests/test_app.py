import unittest
from threading import Thread
from time import sleep
from unittest.mock import Mock

from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.local.client import LocalClient
from mqtt_device.remote.client import ApplicationClient
from transition_doors.events import TransitionEvent

from appli import T_Maze
from datasouriscamera.tests.test_devices import FakeTransitionDoors
from datasouriscamera.devices import Local_T_Maze, Remote_T_Maze, DirectionEvent, RemoteBottle
from datasouriscamera.motion_detector import StateReader

SERIAL_PORT = 'COM5'  # Remplacez par le bon port série
BAUD_RATE = 9600

class TestApp(unittest.TestCase):

    def test_something(self): #lancer ce programme pour faire les tests

        mqtt_client = MQTTClient(broker_ip="192.168.24.120")
        writer = Mock()  # TrackingWriter(dest_dir=Path(r"C:\Users\steve\Documents\data_cam"))  #enleve le mock pour que ca fonctionne
        remote_client = ApplicationClient(client_id="app_client", environment_name="souris_city", id_env="01", mqtt_client=mqtt_client)

        remote_client.connect()

        bottle_right = remote_client.get_remote_device(device_id="bottle_right").as_type(RemoteBottle)
        #bottle_right = Mock()
        bottle_left = remote_client.get_remote_device(device_id="bottle_left").as_type(RemoteBottle)
        sr = StateReader(port_com=SERIAL_PORT, baud_rate=BAUD_RATE)

        # motion_detector = MotionDetector(state_reader=sr)
        fake_gate = FakeTransitionDoors()

        def run_fake(): #scenario de la porte, c'est ici pour simuler la porte
            sleep(2)
            fake_gate.mouse_moved(
                event=TransitionEvent(id_device="toto", timestamp=0, rfid="testrfid1", from_room="BLACK_BOX", to_room="T_MAZE"))
            sleep(2000)
            fake_gate.mouse_moved(
                event=TransitionEvent(id_device="toto", timestamp=0, rfid="testrfid1", from_room="T_MAZE", to_room="BLACK_BOX"))
            # sleep(10)
            # fake_gate.mouse_moved(
            #     event=TransitionEvent(id_device="toto", timestamp=0, rfid="testrfid2", from_room="BLACK_BOX", to_room="T_MAZE"))
            # sleep(30)
            # fake_gate.mouse_moved(
            #     event=TransitionEvent(id_device="toto", timestamp=0, rfid="testrfid2", from_room="T_MAZE", to_room="BLACK_BOX"))

        #gate = remote_client.get_remote_device(device_id="transition_doors").as_type(RemoteTransitionDoors)

        mqtt_client = MQTTClient(broker_ip="192.168.24.120")
        local_client = LocalClient(environment_name="souris_city", id_env="01", client_id="local_t_maze", mqtt_client=mqtt_client)

        app = T_Maze(camera=sr, bottle_left=bottle_left, bottle_right=bottle_right, gate=fake_gate, writer=writer) #fake_gate pour tester door, decommente gate pour avoir la vraie porte

        local_t_maze = Local_T_Maze(device_id="t_maze", t_maze=app)
        local_client.connect()
        local_client.add_local_device(local_t_maze)

        thread = Thread(target=run_fake)
        thread.start()

        #bottle.set_state("1")
        device = remote_client.get_remote_device("t_maze").as_type(Remote_T_Maze)

        def on_direction_changed(sender: Remote_T_Maze, event: DirectionEvent):
            print(f"{event.direction}, {event.rfid}, {event.activate_bottle}")

        # def on_direction_confirmed(sender: Remote_T_Maze, event: StateConfirmationEvent):
        #     print(f"{event.state}, {event.rfid}")

        device.direction_changed.register(on_direction_changed)
        #device.confirm_direction_changed.register(on_direction_confirmed)

        app.start()


if __name__ == '__main__':
    unittest.main()
