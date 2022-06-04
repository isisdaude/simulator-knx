"""
Some class definitions for the simulated KNX actuators.
"""

from system.telegrams import HeaterPayload, Payload, Telegram, BinaryPayload, DimmerPayload
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod
import sys, logging
sys.path.append("core")


class LightActuator(Actuator, ABC):
    """Abstract class to represent light devices"""

    def __init__(self, class_name, name, refid, individual_addr, default_status, state, lumen, beam_angle):
        super().__init__(class_name, name, refid, individual_addr, default_status, "light", state)
        self.max_lumen = lumen # Luminous flux of device = quantity of visible light emitted from a source per unit of time
        self.beam_angle = beam_angle # angle at which the light is emitted (e.g. 180° for a LED bulb)


class LED(LightActuator):
    """Concrete class to represent LED lights"""

    # state is ON/OFF=True/False
    def __init__(self, name, refid, individual_addr, default_status, state=False):
        super().__init__('LED', name, refid, individual_addr, default_status, state, lumen=800, beam_angle=180)
        self.state_ratio = 100 # Percentage of 'amplitude'

    def update_state(self, telegram):
        if telegram.control_field == True: # Control field bit

            if isinstance(telegram.payload, BinaryPayload):
                self.state = telegram.payload.content

            elif isinstance(telegram.payload, DimmerPayload):
                self.state = telegram.payload.content
                if self.state:
                    self.state_ratio = telegram.payload.state_ratio

            self.__str_state = 'ON' if self.state else 'OFF'
            logging.info(f"{self.name} has been turned {self.__str_state} by device '{telegram.source}'.")
    
    def effective_lumen(self):
        # Lumen quantity rationized with the state ratio (% of source's max lumens)
        return self.max_lumen*(self.state_ratio/100)

    def get_dev_info(self):
        dev_specific_dict = {"state":self.state, "max_lumen":self.max_lumen, "beam_angle":self.beam_angle, "state_ratio":self.state_ratio}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class TemperatureActuator(Actuator, ABC):
    """Abstract class to represent temperature devices"""

    def __init__(self, class_name, name, refid, individual_addr, default_status, actuator_type, state, update_rule, max_power=0):
        super().__init__(class_name, name, refid, individual_addr, default_status, actuator_type, state)
        self.update_rule = update_rule
        self.max_power = max_power
        """Power of the device in Watts"""
        self.state_ratio = 100 # Percentage of 'amplitude'
        self.effective_power = self.max_power * self.state_ratio/100
        """Power really used, max by default"""
    
    def get_dev_info(self):
        self.__str_state = "ON" if self.state else "OFF"
        dev_specific_dict = {"state":self.state, "update_rule":self.update_rule, "max_power":self.max_power, "state_ratio":self.state_ratio, "power":self.effective_power}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict



class Heater(TemperatureActuator):
    """Concrete class to represent a heating device"""

    def __init__(self, name, refid, individual_addr, default_status, max_power=400, state=False, update_rule=1):
        # Verification of update_rule sign
        try:
            assert update_rule >= 0
        except AssertionError:
            logging.error("The Heater should have update_rule>=0")
            sys.exit()
        super().__init__('Heater', name, refid, individual_addr, default_status, "heater", state, update_rule, max_power)
        

    def watts_to_temp(self, watts):
        return ((watts - 70)*2)/7 + 18

    def required_power(self, desired_temperature=20, volume=1, insulation_state="good"):
        from system import INSULATION_TO_CORRECTION_FACTOR
        assert desired_temperature >= 10 and desired_temperature <= 40
        desired_wattage = volume*self.temp_to_watts(desired_temperature)
        desired_wattage += desired_wattage*INSULATION_TO_CORRECTION_FACTOR[insulation_state]
        return desired_wattage

    def max_temperature_in_room(self, volume=1, insulation_state="good"):
        """Maximum reachable temperature for this heater in the specified room"""
        from system import INSULATION_TO_CORRECTION_FACTOR
        watts = self.power/((1+INSULATION_TO_CORRECTION_FACTOR[insulation_state])*volume)
        return self.watts_to_temp(watts)


    def update_state(self, telegram):
         if telegram.control_field == True:  # Control field bit
            # If simple binary telegram payload, we turn heater ON at max power
            if isinstance(telegram.payload, BinaryPayload):
                self.state = telegram.payload.content
                self.effective_power = self.max_power
            if isinstance(telegram.payload, DimmerPayload):
                self.state = telegram.payload.content
                if self.state:
                    self.state_ratio = telegram.payload.state_ratio
                    self.effective_power = self.max_power * self.state_ratio/100



class AC(TemperatureActuator):
    """Concrete class to represent a cooling device"""

    def __init__(self, name, refid, individual_addr, default_status, max_power=400, state=False, update_rule=-1):
        # Verification of update_rule sign
        try:
            assert update_rule <= 0
        except AssertionError:
            logging.error("The Cooler should have update_rule<=0")
            sys.exit()
        super().__init__('AC', name, refid, individual_addr, default_status, "ac", state, update_rule, max_power)

    def update_state(self, telegram):
        if telegram.control_field == True:  # Control field bit
            # If simple binary telegram payload, we turn heater ON at max power
            if isinstance(telegram.payload, BinaryPayload):
                self.state = telegram.payload.content
                self.effective_power = self.max_power
            if isinstance(telegram.payload, DimmerPayload):
                self.state = telegram.payload.content
                if self.state:
                    self.state_ratio = telegram.payload.state_ratio
                    self.effective_power = self.max_power * self.state_ratio/100
    



class Switch(Actuator):
    """Concrete class to represent a swicth indicator, to be linked to a physical device to turn ON/OFF"""
    def __init__(self, name, refid, individual_addr, default_status, state=False ):
        super().__init__('Switch', name, refid, individual_addr, default_status, 'switch', state)

    def update_state(self, telegram):
        if isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content # do not consider the state_ratio

    def get_dev_info(self):
        dev_specific_dict = {"state":self.state}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

class IPInterface(Actuator):
    """Concrete class to represent an IP interface to communicate with external interfaces"""
    from interface.main import Interface
    def __init__(self, name, refid, individual_addr, default_status, interface: Interface, state=False):
        super().__init__('IPInterface', name, refid, individual_addr, default_status, 'ip_interface', state)
        self.interface = interface

    def update_state(self, telegram):
        # TODO: For the moment, retransmit only Binary Telegrams!
        if isinstance(telegram.payload, BinaryPayload):
            self.interface.add_to_sending_queue([telegram])

    def get_dev_info(self):
        dev_specific_dict = {"state":self.state}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

    

            
