import logging
import socket
import unittest
from pathlib import Path
from threading import Thread
from typing import TYPE_CHECKING

from mqtt_device.common.mqtt_client import MQTTClient
from mqtt_device.event_handler import EventHandler
from mqtt_device.local.client import LocalClient
from mqtt_device.remote.client import ApplicationClient

from mqtt_device.tests.convenient_classes.fake_mosquitto_server import FakeMosquittoServer

# from transition_door import ITransitionDoors, TransitionEvent
from transition_doors.events import TransitionEvent
from transition_doors.remote_transition_doors import ITransitionDoors

from datasouriscamera.devices import LocalBottle, RemoteBottle

if TYPE_CHECKING:
    pass

mosquitto: FakeMosquittoServer = None
local_ip: str = None


# def __init__(self, direction: str , occurence: int):
    #     self.direction = direction
    #     self.occurence = occurence


def run_fake_devices():

    def _run():
        conf = Path("resources/mosquitto.conf")

        mosquitto = FakeMosquittoServer(ip=local_ip, kill_if_exists=False, verbose=True, mosquitto_conf=conf)
        mosquitto.start()

        mqtt_client = MQTTClient(broker_ip=local_ip)

        local_client = LocalClient(client_id="local", environment_name="souris_city", id_env="01", mqtt_client=mqtt_client)
        local_client.connect()

        device = LocalBottle(device_id="bottle_left", location="T_MAZE")
        local_client.add_local_device(device)

        device = LocalBottle(device_id="bottle_right", location="T_MAZE")
        local_client.add_local_device(device)

        mqtt_client.wait_until_ended()

    thread = Thread(target=_run)
    thread.start()



class TestDevices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        global local_ip

        logging.root.setLevel(logging.INFO)
        # get the host ip
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)

    def test_run_fake_devices(self):

        #run_fake_devices()

        mqtt_client = MQTTClient(broker_ip="192.168.24.120")
        remote_client = ApplicationClient(client_id="app_client", environment_name="souris_city", id_env="01", mqtt_client=mqtt_client)

        remote_client.connect()

        bottle = remote_client.get_remote_device(device_id="bottle_right").as_type(RemoteBottle)
        bottle.set_state("1")
       # bottle.set_state("0")



        # bottle._is_available = False


        # bottle2 = remote_client.get_remote_device(device_id="bottle_right").as_type(RemoteBottle)
        # bottle2.set_state("ABC")
        # def on_bottle_changed(sender: RemoteBottle, event: BottleEvent):
        #     print("BOTTLE CHANGED!")

        #bottle.bottle_changed.register(on_bottle_changed)

        mqtt_client.wait_until_ended()
        # sleep(5)


class FakeTransitionDoors(ITransitionDoors):

    def __init__(self):
        self._mouse_moved: EventHandler[TransitionEvent] = EventHandler(self)

    @property
    def mouse_moved(self) -> EventHandler[TransitionEvent]:
        return self._mouse_moved

    @property
    def limited_room(self) -> str:
        pass

    @property
    def other_side_room(self) -> str:
        pass

    @property
    def max_number(self) -> int:
        pass

    def add_authorized_rfid(self, rfid_list: str):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def update_rules(self):
        pass