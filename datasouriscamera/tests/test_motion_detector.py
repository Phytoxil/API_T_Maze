import json
import unittest
from threading import Thread
from time import sleep
from typing import List

from datasouriscamera.motion_detector import StateReader, FakeStateReader, MotionDetector

SERIAL_PORT = 'COM5'  # Remplacez par le bon port série
BAUD_RATE = 9600


# class StateReader:
#
#     def __init__(self, port: str, baud_rate: int):
#         self._serial = serial.Serial(port, baud_rate)
#         self._state_changed = Event()

        # self._current_state: str = None

    # def start(self):
    #     # self._serial = serial.Serial(self._port, self._baud_rate)
    #     self._serial.open()
    #
    #     thread = Thread(name="StateReader", target=self._listen)
    #     thread.start()

    # def _listen(self):
    #     pass

    # def next(self) -> str:
    #
    #     is_finished = False
    #
    #     while not is_finished:
    #         data = self._serial.readline()
    #
    #     return "TOTO"


class TestMotionDetector(unittest.TestCase):


    def test_motion_detector(self):

        sr = StateReader(port_com=SERIAL_PORT, baud_rate=BAUD_RATE)
        md = MotionDetector(state_reader=sr)

        md.start()

        print("END")


    def test_something(self):
        state_listener = FakeStateReader(SERIAL_PORT, BAUD_RATE)
        state_listener.start()
        # self.assertEqual(True, False)  # add assertion here

    def test_tmp_serial(self):

        reader = StateReader(port_com=SERIAL_PORT, baud_rate=BAUD_RATE)

        while True:
            res = reader.next_state()
            res = res.replace("\'", "\"")
            print(f"NEXT = {res}")
            tab = json.loads(res)
            print(tab)
    def test_tmp_json(self):

        msg = dict()
        msg['centroid'] = (87, 46)
        msg['movement_direction'] = "In Zone"

        top_msg = list()
        top_msg.append(msg)
        top_msg.append(msg)

        res_json = json.dumps(top_msg)

        res_des = json.loads(res_json)

        print("OK")
        # json_str = """{'movement_direction': 'Left'}"""
        #
        # res = json.loads(json_str)
        #
        # print(res)

    def test_motion_detector_fake(self):

        def toto(list_msg: List[str]): #manque list_msg en argument ?


            for elem in list_msg:
                sr.add_message(elem)

        res: List[str] = list()

        res.append(r"{'centroid': (85, 48), 'status': '1', 'movement_direction': 'In Zone'} 1")
        res.append(r"{'centroid': (85, 152), 'status': '1', 'movement_direction': 'In Zone'} 1")

        sr = FakeStateReader(fake_run=toto)

        md = MotionDetector(state_reader=sr)

        md.start()


        sleep(10)

    def test_tmp_state(self):
        sr = FakeStateReader(nb_alt=3)

        def run():
            while True:
                status = sr.next_state()
                print(status)
                if status == "END":
                    break
            #
            # tutu = sr.next_state()
            # print(tutu)

        thread = Thread(target=run)
        thread.start()

        # sr.add_message("KIKOO")
        sleep(10)
    def test_json(self):
        chr = '[{"movement_direction": "In Zone", "centroid": "(85, 45)"}]'
        chr_des = json.loads(chr)
        print(chr_des)

if __name__ == '__main__':
    unittest.main()
