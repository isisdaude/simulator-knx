"""
Some class definitions for the simulated KNX actuators.
"""
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod

class LightActuators(Actuator, ABC):
    def __init__(self, name, refid, individual_addr, default_status, state):
        super().__init__(name, refid, individual_addr, default_status, "light", state)

    def lumen_to_Lux(self, lumen, area):
        ''' The conversion from Lumens to Lux given the surface area in squared meters '''
        return lumen/area

    def lux_to_Lumen(self, lux, area):
        ''' The conversion from Lux to Lumen given the surface area in squared meters '''
        return area*lux

    def update(self, functional_module): # states is a list of button states with respecting index
        if (functional_module.state):
            self.state = True
        else:
            self.state = False



class LED(LightActuators):
    def __init__(self, name, refid, individual_addr, default_status, state=False): #state is ON/OFF=True/False
        super().__init__(name, refid, individual_addr, default_status, state)
        self.lumen = 800 #800 lumens at 1 meter



class TemperatureActuators(Actuator, ABC):
    def __init__(self, name, refid, individual_addr, default_status, actuator_type, state):
        super().__init__(name, refid, individual_addr, default_status, actuator_type, state)
    update_rule = 0

    @abstractmethod
    def set_update_rule(self, rule:int):
        self.update_rule = rule

    def get_update_rule(self):
        return self.update_rule

class Heater(TemperatureActuators):
    def __init__(self, name, refid, individual_addr, default_status, state=False):
        super().__init__(name, refid, individual_addr, default_status, "heater", state)

    def set_update_rule(self, rule: int):
        assert(rule >= 0)
        super().set_update_rule(rule)

class Cooler(TemperatureActuators):
    def __init__(self, name, refid, individual_addr, default_status, state=False):
        super().__init__(name, refid, individual_addr, default_status, "cooler", state)

    def set_update_rule(self, rule: int):
        assert(rule <= 0)
        super().set_update_rule(rule)
