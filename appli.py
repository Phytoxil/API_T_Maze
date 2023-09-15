import json
from datetime import datetime

from mqtt_device.event_handler import EventHandler
from transition_doors.events import TransitionEvent
from transition_doors.remote_transition_doors import ITransitionDoors

from datasouriscamera.devices import BottleEvent, DirectionEvent, RemoteBottle, TrackingWriter, IT_Maze
from datasouriscamera.motion_detector import IStateReader


class T_Maze(IT_Maze):

    def __init__(self, camera: IStateReader, bottle_left: RemoteBottle, bottle_right : RemoteBottle, gate: ITransitionDoors, writer: TrackingWriter): #permet de mettre des arguments quand je creer l'application
        self.camera = camera #on a defini ce qu'est l'argument camera. L'interert est de pouvoir tester avec de faux device
        self.bottle_left = bottle_left
        self.bottle_right = bottle_right
        self.gate = gate
        self.gate.mouse_moved.register(self.on_mouse_moved)
        self.bottle_right.bottle_changed.register(self.on_fin_de_course)
        #self._file_handler: TextIOWrapper = None
        self._is_into_maze = False
        self.current_status :str = None
        self.is_first = None
        self.current_mouse: str = None
        self.writer=writer

        self.current_direction = None #pour memoriser la direction
        self.confirm_dir = None #variable de confirmation du capteur
        self._direction_changed: EventHandler[DirectionEvent] = EventHandler(self)
        # self.confirm_direction_changed: EventHandler[StateConfirmationEvent] = EventHandler(self)



    def on_mouse_moved(self, sender: ITransitionDoors, event: TransitionEvent):
        if event.to_room != "T_MAZE":
            print("MOUSE EXIT") #la souris est sortie, on rend tous les biberons accessibles. Pour cela on envoie l'état "1" qui signifie faire avancer le biberon
            self.bottle_left.set_state("1")
            self.bottle_right.set_state("1")
            self.writer.close() # on écrit pas dans le fichier quand la souris est en dehors du T
            self._is_into_maze = False #la souris n'est pas dans le T
            self.current_status = None
            self.is_first = None
            self.current_mouse = None
        else:
            print("MOUSE ENTER") # la souris est dans le T
            current_datetime = datetime.now()
            filename = event.rfid + current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
            self.writer.filename = filename
            self._is_into_maze = True
            self.current_mouse = event.rfid



    def on_fin_de_course(self, sender: RemoteBottle, event: BottleEvent):
        print(f"bib {sender.device_id} en fin de course")

    def start(self):

        while True:
            state = self.camera.next_state()
            tab = json.loads(state)
            #print(tab)
            for i in tab:

                if self._is_into_maze:
                    self.writer.write(str(i) + '\n')
                    direction = i['movement_direction']
                    confirm_dir = i['beam']
                    #tableau =['Left', 'Right', 'None']
                    """ direction envoie 'Left', 'Right', 'Center'"""
                    """beam envoie =['Left', 'Right', None]"""

                    """ pour exclure la condition de direction "Centre" """
                    etat= None
                    if confirm_dir == 'None':
                        etat = direction
                    else :
                        etat = confirm_dir
                    if self.current_status == etat:
                        continue
                    self.current_status = etat

                    if direction == 'Right':
                        self.direction_changed(
                            DirectionEvent(direction="right", activate_bottle=False, rfid=self.current_mouse))
                    if direction == 'Left':
                        self.direction_changed(
                            DirectionEvent(direction="left", activate_bottle=False, rfid=self.current_mouse))

                    if confirm_dir == 'Right':
                        act_bottle = self.bottle_left.set_state("0")
                        self.direction_changed(DirectionEvent(direction="beam_right", activate_bottle=act_bottle, rfid=self.current_mouse))

                    if confirm_dir == 'Left':
                        act_bottle = self.bottle_right.set_state("0")
                        self.direction_changed(DirectionEvent(direction="beam_left", activate_bottle=act_bottle, rfid=self.current_mouse))

                    self.is_first = True if self.is_first is None else False

    @property
    def direction_changed(self) -> EventHandler[DirectionEvent]:
        return self._direction_changed


