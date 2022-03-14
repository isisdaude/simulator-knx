"""
Some class definitions for the simulated KNX sensors.
"""
from .device_abstractions import Sensor
from abc import ABC, abstractclassmethod

class Button(Sensor):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        self.state = False

    def press(self):
        if(self.state == True):
            self.state = False
        else:
            self.state = True

class Brightness(Sensor):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "brightness")


class Thermometer(Sensor):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "temperature")
