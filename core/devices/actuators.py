"""
Some class definitions for the simulated KNX actuators.
"""
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod
import sys
sys.path.append("core")

class LightActuator(Actuator, ABC):
    """Abstract class to represent light devices"""
    def __init__(self, name, refid, individual_addr, default_status, state, lumen):
        super().__init__(name, refid, individual_addr, default_status, "light", state)
        self.lumen = lumen

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

    def update_state(self, telegram):
        if telegram.control_field == True: # Control field bit
            if telegram.payload == 0 or telegram.payload == 1: # 0 is the encoding for push-button, 1 for switch #TODO implement a class payload with different fields
                self.state = not self.state
        # if the control field is not True, the telegram does nto concern the LED



class TemperatureActuator(Actuator, ABC):
    """Abstract class to represent temperature devices"""
    def __init__(self, name, refid, individual_addr, default_status, actuator_type, state, update_rule, max_power=0):
        super().__init__(name, refid, individual_addr, default_status, actuator_type, state)
        self.update_rule = update_rule
        self.max_power = max_power
        """Power of the device in Watts"""
        self.power = max_power
        """Power really used, max by default"""



class Heater(TemperatureActuator):
    """Concrete class to represent a heating device"""
    def __init__(self, name, refid, individual_addr, default_status, max_power, state=False, update_rule=1):
        # Verification of update_rule sign
        assert update_rule >= 0, "The Heater should have update_rule>=0."  #Syntax for an error message
        super().__init__(name , refid, individual_addr, default_status, "heater", state, update_rule, max_power)

    insulation_to_correction_factor = {"average":0, "good": -10/100, "bad": 15/100}
    """Situation of the insulation of the room associated to the correction factor for the heating"""

    def temp_to_watts(self, temp): # useful watts required to heat 1m3 to temp
        dist = 18 - temp
        return 70 - (dist * 7)/2

    def watts_to_temp(self, watts):
        return ((watts - 70)*2)/7 + 18

    def required_power(self, desired_temperature=20, volume=1, insulation_state="good"):
        assert desired_temperature >= 10 and desired_temperature <= 40
        desired_wattage = volume*self.temp_to_watts(desired_temperature)
        desired_wattage += desired_wattage*self.insulation_to_correction_factor[insulation_state]
        return desired_wattage

    def max_temperature_in_room(self, volume=1, insulation_state="good"):
        """Maximum reachable temperature for this heater in the specified room"""
        watts = self.power/((1+self.insulation_to_correction_factor[insulation_state])*volume)
        return self.watts_to_temp(watts)


    def update_state(self, telegram):
        if telegram.control_field == True: # Control field bit
            if telegram.payload == 0: # Encoding of Push-Button
                self.state = not self.state
            #TODO:
            # if telegram.payload == 10: #Encoding of temperature TemperatureController
            #     self.power = payload.power


class AC(TemperatureActuator):
    """Concrete class to represent a cooling device"""
    def __init__(self, name, refid, individual_addr, default_status, max_power, state=False, update_rule=-1):
        # Verification of update_rule sign
        assert update_rule <= 0, "[ERROR] The Cooler should have update_rule<=0."  #Syntax for an error message
        super().__init__(name, refid, individual_addr, default_status, "cooler", state, update_rule, max_power)

    def update_state(self, telegram):
        if telegram.control_field == True: # Control field bit
            if telegram.payload == 0: # Encoding of Push-Button
                self.state = not self.state
            #TODO:
            # if telegram.payload == 10: #Encoding of temperature TemperatureController
            #     self.power = payload.power
