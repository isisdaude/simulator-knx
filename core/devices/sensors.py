"""
Some class definitions for the simulated KNX sensors.
"""
from device_abstractions import Sensor
from abc import ABC, abstractclassmethod

class Button(Sensor):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
    
    def press(self):
        if(self.status == True):
            self.status = False
        else:
            self.status = True