"""
Some class definitions for the simulated KNX actuators.
"""
from system.telegrams import HeaterPayload, Payload, Telegram, TempControllerPayload, ButtonPayload
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

    # state is ON/OFF=True/False
    def __init__(self, name, refid, individual_addr, default_status, state=False):
        super().__init__(name, refid, individual_addr, default_status, state, lumen=800)

    def update_state(self, telegram):
        if telegram.control_field == True:  # Control field bit
            if ButtonPayload(telegram.payload).pushed:
                self.state = not self.state


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
        # Syntax for an error message
        assert update_rule >= 0, "The Heater should have update_rule>=0."
        super().__init__(name, refid, individual_addr,
                         default_status, "heater", state, update_rule, max_power)

    def update_state(self, telegram: Telegram):
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
        # Syntax for an error message
        assert update_rule <= 0, "[ERROR] The Cooler should have update_rule<=0."
        super().__init__(name, refid, individual_addr,
                         default_status, "cooler", state, update_rule, max_power)

    def update_state(self, telegram):
        if telegram.control_field == True:  # Control field bit
            pass
            # TODO: Payload for AC
