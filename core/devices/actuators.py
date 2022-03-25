"""
Some class definitions for the simulated KNX actuators.
"""
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod

class LightActuator(Actuator, ABC):
    """Abstract class to represent light devices"""
    def __init__(self, name, refid, individual_addr, default_status, state, lumen):
        super().__init__(name, refid, individual_addr, default_status, "light", state)
        self.lumen = lumen

    # @property #getter in a pythonic way, but creates overhead!!! use only if usefull
    # def lumen(self):
    #     return self._lumen
    #
    # @lumen.setter
    # def lumen(self, lumen:int):
    #     # condition on rule value, e.g. raise error if rule ==0
    #     self._lumen = lumen

    def lumen_to_Lux(self, lumen, area):
        ''' The conversion from Lumens to Lux given the surface area in squared meters '''
        return lumen/area

    def lux_to_Lumen(self, lux, area):
        ''' The conversion from Lux to Lumen given the surface area in squared meters '''
        return area*lux

class LED(LightActuator):
    """Concrete class to represent LED lights"""
    def __init__(self, name, refid, individual_addr, default_status, state=False): #state is ON/OFF=True/False
        super().__init__(name, refid, individual_addr, default_status, state, lumen=800)


class TemperatureActuator(Actuator, ABC):
    """Abstract class to represent temperature devices"""
    def __init__(self, name, refid, individual_addr, default_status, actuator_type, state, update_rule, power=0):
        super().__init__(name, refid, individual_addr, default_status, actuator_type, state)
        self.update_rule = update_rule
        self.max_power = power
        """Power of the device in Watts"""


class Heater(TemperatureActuator):
    """Concrete class to represent a heating device"""
    def __init__(self, name, refid, individual_addr, default_status, max_power, state=False, update_rule=1):
        # Verification of update_rule sign
        assert update_rule >= 0, "The Heater should have update_rule>=0."  #Syntax for an error message
        super().__init__(name , refid, individual_addr, default_status, "heater", state, update_rule, max_power)


class Cooler(TemperatureActuator):
    """Concrete class to represent a cooling device"""
    def __init__(self, name, refid, individual_addr, default_status, state=False, update_rule=-1):
        # Verification of update_rule sign
        assert update_rule <= 0, "The Cooler should have update_rule<=0."  #Syntax for an error message
        super().__init__(name, refid, individual_addr, default_status, "cooler", state, update_rule)
    # def set_update_rule(self, rule: int):
    #     assert(rule < 0)
    #     super().set_update_rule(rule)
