"""
Class definitions for the simulated KNX Functional Modules:
Button and Dimmer.
"""

import logging
from typing import Dict, Union, Tuple

from .device_abstractions import FunctionalModule
from system.telegrams import BinaryPayload, DimmerPayload
from system.system_tools import IndividualAddress


class Button(FunctionalModule):
    """Concrete class to represent a Button"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of Button device object"""
        super().__init__(name, individual_addr)
        self.state = False
        self.__str_state = "OFF"

    def user_input(self, state: bool = None, state_ratio=None) -> None:
        """
        Update its state and send a telegram with ButtonPayload on the bus.

        state_ratio=None is simply to have the same function structure for all functional modules, and avoid error in user command parser
        """
        self.state = not self.state
        if state is not None:
            self.state = state
        self.__str_state = "ON" if self.state else "OFF"
        logging.info(f"The {self.name} has been turned {self.__str_state}.")
        __binary_payload = BinaryPayload(binary_state=self.state)
        self.send_telegram(__binary_payload)

    def get_dev_info(
        self,
    ) -> Dict[str, Union[str, bool, float, Tuple[float, float, float]]]:
        """Return information about the Button device's states and configuration, method called via CLI commmand 'getinfo'"""
        dev_specific_dict = {"state": self.state}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class Dimmer(FunctionalModule):
    """Concrete class to represent a Dimmer Button"""

    def __init__(self, name, individual_addr: IndividualAddress) -> None:
        """Initialization of Dimmer device object"""
        super().__init__(name, individual_addr)
        self.state = False
        self.__str_state = "OFF"
        self.state_ratio = 100

    def user_input(self, state: bool = None, state_ratio: float = 100):
        """
        Update its state and send a telegram with DimmerPayload on the bus.

        state_ratio : fraction of the dimmer state, percentage in (0-100)
        """
        self.state = not self.state
        if state is not None:
            self.state = state
        self.__str_state = "ON" if self.state else "OFF"

        if self.state:
            self.state_ratio = state_ratio
            logging.info(
                f"The {self.name} has been turned {self.__str_state} at {self.state_ratio}%."
            )
        else:
            logging.info(f"The {self.name} has been turned {self.__str_state}.")

        dimmer_payload = DimmerPayload(
            binary_state=self.state, state_ratio=self.state_ratio
        )
        if hasattr(dimmer_payload, "state_ratio"):
            self.send_telegram(dimmer_payload)
        else:
            logging.error(
                f"The Dimmer payload was not correctly created, the telegram cannot be sent."
            )

    def get_dev_info(
        self,
    ) -> Dict[str, Union[str, bool, float, Tuple[float, float, float]]]:
        """Return information about the Dimmer device's states and configuration, method called via CLI commmand 'getinfo'"""
        dev_specific_dict = {"state": self.state, "state_ratio": self.state_ratio}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict
