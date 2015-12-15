__author__ = 'teddycool'
#State-switching and handling of general rendering
#from Inputs import Inputs
#from Board import Board
from Vision import Vision
import time
from  StateLoops import CamCalibrateLoop, CamMoutningLoop, PlayStateLoop
from Inputs import IoInputs
#Global GPIO used by all...
import RPi.GPIO as GPIO


class MainLoop(object):
    def __init__(self):
        #TODO: fix logging to file readable from web
        #self._inputs=Inputs.Inputs(self)
        #self._board = Board.Board()
        self._vision= Vision.Vision()
        self._calibrateState = CamCalibrateLoop.CamCalibrateLoop()
        self._mountingState = CamMoutningLoop.CamMountingLoop()
        self._playState = PlayStateLoop.PlayStateLoop()
        self._state = {"MountState": self._mountingState, "CalState": self._calibrateState, "PlayState": self._playState}
        #Start -> MountState ->[button]-> CalState ->[auto when done]-> PlayState ---> End...
        self._currentStateLoop = self._state["MountState"]
        self._calButton = IoInputs.PushButton(GPIO,23)
        self._gameButton = IoInputs.PushButton(GPIO,24)


    def initialize(self):
        print "Main init..."
        #self._inputs.initialize()
        self.time=time.time()
        frame = self._vision.initialize()
        self._lastframetime = time.time()
        #Init all states
        for key in self._state.keys():
            self._state[key].initialize()
        self._calButton.initialize()
        self._gameButton.initialize()
        print "Game started at ", self.time
        return frame

    def update(self):
        start = time.time()
        frame = self._vision.update()
        self._currentStateLoop.update(frame)
        cal = self._calButton.update()
        game = self._gameButton.update()
        #TODO: fix better state-machine, move to state-loops
        if cal  == "Pressed":
            self.changeState("CalState") #Mounting ready
        if cal == "LongPressed":
            self.changeState("MountState")  #Reset to playstate
        if game == "Pressed":
            self.changeState("PlayState")  #Reset to playstate
        print "Main update time: " + str(time.time()-start)
        return frame

    def draw(self, frame):
        start = time.time()
        frame = self._currentStateLoop.draw(frame)
        self._calButton.draw(frame,"Cal", 5,80)
        self._gameButton.draw(frame,"Game", 5,100)

        framerate = 1/(time.time()-self._lastframetime)
        self._lastframetime= time.time()
        self._vision.draw(frame, framerate) #Actually draw frame to mjpeg streamer...
        print "Main draw time: " + str(time.time()-start)


    def changeState(self, newstate):
        self._currentStateLoop = self._state[newstate]
        self._currentStateLoop.initialize()