import json
from abc import abstractmethod
from io import TextIOWrapper
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from mqtt_device.event_handler import EventArgs, EventHandler
from mqtt_device.local.device.device import LocalDevice, DeviceProperty
from mqtt_device.remote.device.device import RemoteDevice

if TYPE_CHECKING:
    from appli import T_Maze


class BottleEvent(EventArgs):
    pass


class DirectionEvent(EventArgs):

    def __init__(self,  direction: str, activate_bottle: bool, rfid: str = None):
        self.direction = direction
        self.activate_bottle = activate_bottle
        self.rfid = rfid


class StateConfirmationEvent(EventArgs):

    def __init__(self, state: str, rfid: str = None):
        self.state = state
        self.rfid = rfid


class LocalBottle(LocalDevice):

    DEVICE_TYPE = "bottles"

    def declare_properties(self):
        prop = DeviceProperty(property_name="state", datatype="str", settable=True)
        self.add_property(prop)

        prop.value_changed += self.on_state_changed

    def on_state_changed(self, sender: DeviceProperty, old_val: str, new_val: str):
        print(f"Received '{new_val}' DO SOMETHING ({self.device_id})")
        sleep(3)
        # sender._set_value(new_val)


class IT_Maze:

    @property
    @abstractmethod
    def direction_changed(self) -> EventHandler[DirectionEvent]:
        pass


class Remote_T_Maze(RemoteDevice, IT_Maze):

    DEVICE_TYPE = "t_maze"

    def __init__(self, device_id: str, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self._direction_changed: EventHandler[DirectionEvent] = EventHandler(self)
        # self.confirm_direction_changed: EventHandler[StateConfirmationEvent] = EventHandler(self)

    def on_direction_changed(self, sender: DeviceProperty, old_val: str, new_val: str):

        tab_json = json.loads(new_val)

        event = DirectionEvent(direction=tab_json['direction'], activate_bottle=tab_json['is_first'], rfid=tab_json['rfid'])
        self.direction_changed(event=event)

    # def on_confirmation_direction_changed(self, sender: DeviceProperty, old_val: str, new_val: str):
    #     tab_json = json.loads(new_val)
    #
    #     event = StateConfirmationEvent(state=tab_json['state'], rfid=tab_json['rfid'])
    #     self.confirm_direction_changed(event=event)

    def on_property_added(self, sender: RemoteDevice, prop: DeviceProperty):

        if prop.property_name == "direction":
            prop.value_changed += self.on_direction_changed
        # if prop.property_name == "state":
        #     prop.value_changed += self.on_confirmation_direction_changed

    @property
    def direction_changed(self) -> EventHandler[DirectionEvent]:
        return self._direction_changed


class Local_T_Maze(LocalDevice, IT_Maze):#local car c'est l'objet physique, celui qui envoie

    DEVICE_TYPE = "t_maze"

    def __init__(self, device_id: str, t_maze: IT_Maze, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)
        self.t_maze = t_maze
        self.t_maze.direction_changed.register(self.on_direction_changed)

    def on_direction_changed(self, sender: IT_Maze, event: DirectionEvent):
        print(event, sender)

        tab_json = {'direction': event.direction, 'rfid': event.rfid, 'is_first': event.activate_bottle}
        prop = self.get_property("direction")
        prop.set_str_value(json.dumps(tab_json))



    def declare_properties(self):
        prop = DeviceProperty(property_name="direction", datatype="json", settable=False)
        self.add_property(prop)

    @property
    def direction_changed(self) -> EventHandler[DirectionEvent]:
        return self.t_maze.direction_changed


class RemoteBottle(RemoteDevice):

    DEVICE_TYPE = "bottles"

    def __init__(self, device_id: str, device_type: str = None, location: str = None):
        super().__init__(device_id, device_type, location)

        self.bottle_changed: EventHandler[BottleEvent] = EventHandler(self)
        self._is_available = True # variable qui regarde l'état de la course du biberon (s'il avance ou pas)
        self._need_to_init = False


    def set_state(self, state: str) -> bool:
        print(f"state  ={state}")

        prop = self.get_property("state")
        old_val = prop.value

        print(f"FROM {old_val} TO {state}")

        if state == prop.value:
            return False

        if not self._is_available:
            if state == "0":
                self._need_to_init = True

            print("pas avalaible")
            return False

        prop.value = state
        self._is_available = False


        if old_val in ["1", None] and state == "0":
            return True
        else:
            return False

    def on_state_changed(self, sender: DeviceProperty, old_val: str, new_val: str):
        print(f"STATE CHANGED to '{new_val}'")
        self._is_available = True
        self.bottle_changed(BottleEvent())

        if self._need_to_init:
            self.set_state("1") #cette ligne etait commentée avec un 0
            self._need_to_init = False


    def on_property_added(self, sender: RemoteDevice, prop: DeviceProperty):

        # print(f"PROP = {prop.property_name}")
        if prop.property_name == "state":
            prop.value_changed += self.on_state_changed


class TrackingWriter():
    def __init__(self, dest_dir: Path):
        self._dest_dir = dest_dir
        self._file_handler: TextIOWrapper = None
        self._filename: str = None

    @property
    def fullpath(self) -> Path:
        return self._dest_dir/self._filename

    @property
    def filename(self) -> str:
        return self._filename

    def close(self):
        if self._file_handler:
            self._file_handler.close()

    @filename.setter
    def filename(self, value: str):
        # if self._file_handler:
        #     self._file_handler.close()
        self._filename = value

        self._file_handler = open(self.fullpath,
                                  'w')  # on ecrit le flux d'information provenant de la camera dans un fichier

    def write(self, text: str):
        self._file_handler.write(text + '\n')
        self._file_handler.flush()