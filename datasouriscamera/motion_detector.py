from abc import abstractmethod
from multiprocessing import Queue
from threading import Thread
from typing import Callable

import serial


class IStateReader:

    @abstractmethod
    def next_state(self) -> str:
        pass


class StateReader(IStateReader):

    def __init__(self, port_com: str, baud_rate: int):
        self._serial = serial.Serial(port_com, baud_rate)

    def next_state(self) -> str:
        res = self._serial.readline()

        return res.strip().decode('utf-8')


class FakeStateReader(IStateReader):

    def __init__(self, fake_run: Callable) -> None:
        self._messages: Queue[str] = Queue()

        self._fake_run = fake_run
        self._is_running = False

    # def _run_fake(self):
    #     while self._nb_alt > 0:
    #         self.add_message("ON")
    #         sleep(0.1)
    #         self.add_message("OFF")
    #         self._nb_alt -= 1
    #
    #     self.add_message("END")

    def add_message(self, message: str):
        self._messages.put(message)

    def next_state(self) -> str:

        if not self._is_running:
            thread = Thread(target=self._fake_run)
            thread.start()
            self._is_running = True

        return self._messages.get()


class MotionDetector:

    def __init__(self, state_reader: IStateReader) -> None:
        self._ask_to_stop: bool = False
        self._state_reader: IStateReader = state_reader
        # pass


    def start(self):
        thread = Thread(name="MotionDetector", target=self._main_loop)
        thread.start()

    def _main_loop(self):

        while not self._ask_to_stop:
            res = self._state_reader.next_state()
            print(res)