"""
Some class definitions for the simulated KNX actuators.
"""
from system.telegrams import HeaterPayload, Payload, Telegram, TempControllerPayload, ButtonPayload, SwitchPayload
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod
import sys, logging
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

    # state is ON/OFF=True/False
    def __init__(self, name, refid, individual_addr, default_status, state=False):
        super().__init__(name, refid, individual_addr, default_status, state, lumen=800)

    def update_state(self, telegram):
        if telegram.control_field == True: # Control field bit

            if isinstance(telegram.payload, ButtonPayload):
                if telegram.payload.pushed:
                    # telegram.payload == 0 or telegram.payload == 1: # 0 is the encoding for push-button, 1 for switch #TODO implement a class payload with different fields
                    self.state = not self.state
            if isinstance(telegram.payload, SwitchPayload):
                if telegram.payload.switched:
                    self.state = not self.state
            str_state = 'ON' if self.state else 'OFF'
            logging.info(f"{self.name} has been turned {str_state}.")
        # if the control field is not True, the telegram does nto concern the LED, except for a read state



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
        try:
            assert update_rule >= 0
        except AssertionError:
            logging.error("The Heater should have update_rule>=0")
            sys.exit()
        super().__init__(name , refid, individual_addr, default_status, "heater", state, update_rule, max_power)


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
         if telegram.control_field == True:  # Control field bit

            if isinstance(telegram.payload, TempControllerPayload):

                if telegram.payload.set_heater_power is not Payload.EMPTY_FIELD:
                    wished_power = telegram.payload.set_heater_power
                    if wished_power < 0:
                        wished_power = 0
                    self.power = wished_power if wished_power <= self.max_power else self.max_power


class AC(TemperatureActuator):
    """Concrete class to represent a cooling device"""

    def __init__(self, name, refid, individual_addr, default_status, max_power, state=False, update_rule=-1):
        # Verification of update_rule sign
        try:
            assert update_rule <= 0
        except AssertionError:
            logging.error("The Cooler should have update_rule<=0")
            sys.exit()
        super().__init__(name, refid, individual_addr, default_status, "cooler", state, update_rule, max_power)

    def update_state(self, telegram):
        if telegram.control_field == True:  # Control field bit
            pass
            # TODO: Payload for AC
