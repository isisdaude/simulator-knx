"""
Some class definitions for the simulated KNX actuators.
"""

import logging
import sys
from system.telegrams import FloatPayload, Payload, Telegram, BinaryPayload, DimmerPayload
from system.system_tools import  IndividualAddress
from .device_abstractions import Actuator
from abc import ABC, abstractclassmethod, abstractmethod

sys.path.append("core")


class LightActuator(Actuator, ABC):
    """Abstract class to represent actuators acting on world's brightness"""
    def __init__(self, class_name: str, name: str, individual_addr: IndividualAddress, state: bool, lumen: float, beam_angle: float):
        """ Initialization of the light actuator devices object"""
        super().__init__(class_name, name, individual_addr, state)
        self.max_lumen = lumen # Luminous flux of device = quantity of visible light emitted from a source per unit of time
        self.beam_angle = beam_angle # angle at which the light is emitted (e.g. 180° for a LED bulb)


class LED(LightActuator):
    """Concrete class to represent LED actuators"""

    # state is ON/OFF=True/False
    def __init__(self, name: str, individual_addr: IndividualAddress, state: bool=False):
        super().__init__('LED', name, individual_addr, state, lumen=800, beam_angle=180)
        self.state_ratio = 100 # Percentage of 'amplitude'

    def update_state(self, telegram: Telegram):
        # if telegram.control_field == True: # Control field bit
        # print(f"telegram received: {telegram}")
        # print("receive telegram led")
        if isinstance(telegram.payload, DimmerPayload):
            # print("dimmer telegram")
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio

        elif isinstance(telegram.payload, BinaryPayload):
            # print("binary telegram")
            self.state = telegram.payload.content

        self.__str_state = 'ON' if self.state else 'OFF'
        logging.info(f"{self.name} has been turned {self.__str_state} by device '{telegram.source}'.")
    
    def effective_lumen(self):
        # Lumen quantity rationized with the state ratio (% of source's max lumens)
        return self.max_lumen*(self.state_ratio/100)

    def get_dev_info(self):
        dev_specific_dict = {"state":self.state, "max_lumen":self.max_lumen, "effective_lumen": self.effective_lumen(), "beam_angle":self.beam_angle, "state_ratio":self.state_ratio}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class TemperatureActuator(Actuator, ABC):
    """Abstract class to represent temperature devices"""
    def __init__(self, class_name: str, name: str, individual_addr: IndividualAddress, state: bool, update_rule: float, max_power: float=0):
        super().__init__(class_name, name, individual_addr, state)
        self.update_rule = update_rule
        self.max_power = max_power
        """Power of the device in Watts"""
        self.state_ratio = 100 # Percentage of 'amplitude'
        """Power really used, max by default"""
    
    def effective_power(self):
        return self.max_power * self.state_ratio/100
    
    def get_dev_info(self):
        self.__str_state = "ON" if self.state else "OFF"
        dev_specific_dict = {"state":self.state, "update_rule":self.update_rule, "max_power":self.max_power, "state_ratio":self.state_ratio, "effective_power":self.effective_power()}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict



class Heater(TemperatureActuator):
    """Concrete class to represent a heating device"""
    def __init__(self, name: str, individual_addr: IndividualAddress, max_power: float=400, state: bool=False, update_rule: float=1):
        # Verification of update_rule sign
        try:
            assert update_rule >= 0
        except AssertionError:
            logging.error("The Heater should have update_rule>=0")
            sys.exit()
        super().__init__('Heater', name, individual_addr, state, update_rule, max_power)
        

    def update_state(self, telegram: Telegram):
        #  if telegram.control_field == True:  # Control field bit
        # If simple binary telegram payload, we turn heater ON at max power
        if isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio



class AC(TemperatureActuator):
    """Concrete class to represent a cooling device"""

    def __init__(self, name: str, individual_addr: IndividualAddress, max_power: float=400, state: bool=False, update_rule: float=-1):
        # Verification of update_rule sign
        try:
            assert update_rule <= 0
        except AssertionError:
            logging.error("The Cooler should have update_rule<=0")
            sys.exit()
        super().__init__('AC', name, individual_addr, state, update_rule, max_power)

    def update_state(self, telegram: Telegram):
        # if telegram.control_field == True:  # Control field bit
        # If simple binary telegram payload, we turn heater ON at max power
        if isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio
    



class Switch(Actuator):
    """Concrete class to represent a swicth indicator, to be linked to a physical device to turn ON/OFF"""
    def __init__(self, name: str, individual_addr: IndividualAddress,  state: bool=False ):
        super().__init__('Switch', name, individual_addr, state)

    def update_state(self, telegram: Telegram):
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
    from svshi_interface.main import Interface
    def __init__(self, name: str, individual_addr: IndividualAddress, interface: Interface, state: bool=False):
        super().__init__('IPInterface', name, individual_addr, state)
        self.interface = interface

    def update_state(self, telegram: Telegram):
        # print(f"update state IP interface, telegram: {telegram}")
        if isinstance(telegram.payload, BinaryPayload):
            # print("Binary payload")
            self.interface.add_to_sending_queue([telegram])
        elif isinstance(telegram.payload, DimmerPayload):
            telegram.payload = BinaryPayload(telegram.payload.content) # create binary payload with state from dimmer payload
            self.interface.add_to_sending_queue([telegram])
        ### TODO float payload

    def get_dev_info(self):
        dev_specific_dict = {"state":self.state}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict
