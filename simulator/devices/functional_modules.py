"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""

import logging
from .device_abstractions import FunctionalModule
from system.telegrams import BinaryPayload, DimmerPayload, HeaterPayload, Payload, Telegram

class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__('Button', name, refid, location, default_status, "button")
        self.state = False
        self.__str_state = "OFF"

    def user_input(self, state=None, state_ratio=None): # state_ratio is only for command parser, to be able to call the function with this argument without errors
        self.state = not self.state
        if state is not None: # if user specifies the wanted state (ON/OFF)
            self.state = state
        self.__str_state = "ON" if self.state else "OFF" #switch the state of the button
        logging.info(f"The {self.name} has been turned {self.__str_state}")
        __binary_payload = BinaryPayload(binary_state=self.state)
        # Send Telegram to the knxbus
        self.send_telegram(__binary_payload, control_field = True)
    
    def get_dev_info(self):
        dev_specific_dict = {"state":self.state}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class Dimmer(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__('Dimmer', name, refid, location, default_status, "dimmer")
        self.state = False
        self.__str_state = "OFF"
        self.state_ratio = 100

    def user_input(self, state=None, state_ratio=100, switch_state=False, keep_on=False):
        if keep_on: # If switch state but we want the dimmer to be on anyway
            self.state = True
            self.__str_state = "ON"
        else: # if user turn ON/OFF dimmer, no need for switch_state flag
            self.state = not self.state
        if state is not None: # if user gives the wanted state (True/False)
            self.state = state
        self.__str_state = "ON" if self.state else "OFF" #switch the state of the button

        if self.state:
            self.state_ratio = state_ratio
            logging.info(f"The {self.name} has been turned {self.__str_state} at {self.state_ratio}%")
        else:
            logging.info(f"The {self.name} has been turned {self.__str_state}")

        dimmer_payload = DimmerPayload(binary_state=self.state, state_ratio=self.state_ratio)
        # Send Telegram to the knxbus
        self.send_telegram(dimmer_payload, control_field = True)
    
    def get_dev_info(self):
        dev_specific_dict = {"state":self.state, "state_ratio":self.state_ratio}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

