"""
Some class definitions for the simulated KNX actuators.
"""
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod

class Light(Actuator, ABC):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "light")

    def lumentoLux(self, lm, area):
        ''' The conversion from Lumens to Lux given the surface area in squared meters '''
        return lm/area

    def luxtoLumen(self, lx, area):
        ''' The conversion from Lux to Lumen given the surface area in squared meters '''
        return area*lx

class LED(Light):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status)
        self.lm = 800 #800 lumens at 1 meter

class TemperatureVariators(Actuator, ABC):
    update_rule = 0

    @abstractmethod
    def set_update_rule(self, rule:int):
        self.update_rule = rule

    def get_update_rule(self):
        return self.update_rule

class Heater(TemperatureVariators):
    def __init__(self, name, refid, line):
        super().__init__(name, refid, line, 0, "heater")

    def set_update_rule(self, rule: int):
        assert(rule >= 0)
        super().set_update_rule(rule)

class AC(TemperatureVariators):
    def __init__(self, name, refid, line, default_status):
        super().__init__(name, refid, line, default_status, "ac")

    def set_update_rule(self, rule: int):
        assert(rule <= 0)
        super().set_update_rule(rule)
