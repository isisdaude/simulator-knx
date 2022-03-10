"""
Some class definitions for the simulated KNX actuators.
"""
from device_abstractions import Actuator
from abc import ABC, abstractclassmethod

class Light(Actuator, ABC):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "light")

    def turnOn(self):
        self.status = 1
    
    def turnOff(self):
        self.status = 0

    def lumentoLux(lm, area):
        ''' The conversion from Lumens to Lux given the surface area in squared meters '''
        return lm/area

    def luxtoLumen(lx, area):
        ''' The conversion from Lux to Lumen given the surface area in squared meters '''
        return area*lx

class LED(Light):
    lm = 800
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status)
