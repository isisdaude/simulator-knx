"""
Class definitions for the simulated KNX actuators: 
LED, Heater, AC, Switch and IPInterface.
"""

import logging
import sys
from abc import ABC
from typing import Dict, Union, Tuple

from system.telegrams import Telegram, BinaryPayload, DimmerPayload, FloatPayload
from system.system_tools import IndividualAddress
from .device_abstractions import Actuator


class LightActuator(Actuator, ABC):
    """Abstract class to represent actuators acting on world's brightness"""

    def __init__(
        self,
        name: str,
        individual_addr: IndividualAddress,
        state: bool,
        lumen: float,
        beam_angle: float,
    ) -> None:
        """
        Initialization of the light actuator object

        lumen : Luminous flux of light source = quantity of visible light emitted from a source per unit of time
        beam_angle : Angle at which the light is emitted (e.g. 180° for a LED bulb)"""
        super().__init__(name, individual_addr, state)
        self.max_lumen = lumen
        self.beam_angle = beam_angle


class LED(LightActuator):
    """Concrete class to represent LED actuators"""

    def __init__(
        self, name: str, individual_addr: IndividualAddress, state: bool = False
    ) -> None:
        """Initialization of a LED device object"""
        super().__init__(name, individual_addr, state, lumen=800, beam_angle=180)
        self.state_ratio = 100  # in %

    def update_state(self, telegram: Telegram) -> None:
        """
        Update the state and/or state_ratio of the LED actuator

        telegram : packet with new devices states
        """
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio

        elif isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content

        self.__str_state = "ON" if self.state else "OFF"
        logging.info(
            f"{self.name} has been turned {self.__str_state} by device '{telegram.source}'."
        )

    def effective_lumen(self) -> float:
        """Lumen quantity adjusted with the state ratio (% of source's max lumens)"""
        return self.max_lumen * (self.state_ratio / 100)

    def get_dev_info(
        self,
    ) -> Dict[str, Union[str, bool, float, Tuple[float, float, float]]]:
        """Return information about the LED device's states and configuration, method called via CLI commmand 'getinfo'"""
        dev_specific_dict = {
            "state": self.state,
            "max_lumen": self.max_lumen,
            "effective_lumen": self.effective_lumen(),
            "beam_angle": self.beam_angle,
            "state_ratio": self.state_ratio,
        }
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class TemperatureActuator(Actuator, ABC):
    """Abstract class to represent actuators acting on world's temperature"""

    def __init__(
        self,
        name: str,
        individual_addr: IndividualAddress,
        state: bool,
        update_rule: float,
        max_power: float = 0,
    ) -> None:
        """
        Initialization of the temperature actuator device object

        update_rule : +/- 1 for now, indicate whether the temperature actuator can heat up or cool down room's temperature
        max_power : power in Watts of the temperature actuator"""
        super().__init__(name, individual_addr, state)
        self.update_rule = update_rule
        self.max_power = max_power
        self.state_ratio = 100  # in %

    def effective_power(self) -> float:
        """Power value adjusted with the state ratio (% of source's max power)"""
        return self.max_power * self.state_ratio / 100

    def get_dev_info(
        self,
    ) -> Dict[str, Union[str, bool, float, Tuple[float, float, float]]]:
        """Return information about the Temperature actuator device's states and configuration, method called via CLI commmand 'getinfo'"""
        dev_specific_dict = {
            "state": self.state,
            "update_rule": self.update_rule,
            "max_power": self.max_power,
            "state_ratio": self.state_ratio,
            "effective_power": self.effective_power(),
        }
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class Heater(TemperatureActuator):
    """Concrete class to represent a heating device"""

    def __init__(
        self,
        name: str,
        individual_addr: IndividualAddress,
        max_power: float = 400,
        state: bool = False,
        update_rule: float = 1,
    ) -> None:
        """
        Initialization of a heater device object

        update_rule : should be > 0
        """
        try:
            assert update_rule > 0
        except AssertionError:
            logging.error(
                f"The Heater should have update_rule > 0, but {update_rule} was given."
            )
            sys.exit()
        super().__init__(name, individual_addr, state, update_rule, max_power)

    def update_state(self, telegram: Telegram) -> None:
        """
        Update the state and/or state_ratio of the heater actuator

        telegram : packet with new devices states
        """
        if isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio


class AC(TemperatureActuator):
    """Concrete class to represent a cooling device"""

    def __init__(
        self,
        name: str,
        individual_addr: IndividualAddress,
        max_power: float = 400,
        state: bool = False,
        update_rule: float = -1,
    ) -> None:
        """
        Initialization of an AC device object

        update_rule : should be < 0
        """
        try:
            assert update_rule < 0
        except AssertionError:
            logging.error(
                f"The AC should have update_rule < 0, but {update_rule} was given."
            )
            sys.exit()
        super().__init__(name, individual_addr, state, update_rule, max_power)

    def update_state(self, telegram: Telegram) -> None:
        """
        Update the state and/or state_ratio of the AC actuator

        telegram : packet with new devices states
        """
        if isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio


class Switch(Actuator):
    """Concrete class to represent a swicth indicator, can be linked to any real actuator device to indicate its state in GUI"""

    def __init__(
        self, name: str, individual_addr: IndividualAddress, state: bool = False
    ) -> None:
        """Initialization of an Switch device object"""
        super().__init__(name, individual_addr, state)
        self.state_ratio = 100  # in %

    def update_state(self, telegram: Telegram) -> None:
        """
        Update the state and/or state_ratio of the Switch actuator

        telegram : packet with new devices states
        """
        if isinstance(telegram.payload, BinaryPayload):
            self.state = telegram.payload.content
        if isinstance(telegram.payload, DimmerPayload):
            self.state = telegram.payload.content
            if self.state:
                self.state_ratio = telegram.payload.state_ratio

    def get_dev_info(
        self,
    ) -> Dict[str, Union[str, bool, float, Tuple[float, float, float]]]:
        """Return information about the Switch actuator device's states and configuration, method called via CLI commmand 'getinfo'"""
        dev_specific_dict = {"state": self.state}
        dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict


class IPInterface(Actuator):
    """
    Concrete class to represent an IP interface to communicate with external interfaces
    Considered as an actuator as it subscribes to the bus, receives telegrams and 'act' on the physical world (send network packets to external SVSHI program
    """

    from svshi_interface.main import Interface

    def __init__(
        self,
        name: str,
        individual_addr: IndividualAddress,
        interface: Interface,
        state: bool = False,
    ) -> None:
        """Initialization of an Switch device object"""
        super().__init__(name, individual_addr, state)
        self.interface = interface

    def update_state(self, telegram: Telegram) -> None:
        """
        Update the state and/or state_ratio of the Switch actuator

        telegram : packet with new devices states
        """
        if isinstance(telegram.payload, BinaryPayload):
            self.interface.add_to_sending_queue([telegram])
        elif isinstance(telegram.payload, DimmerPayload):
            # SVSHI does not support Dimmer payload for actuators, only binary (corresponds to svshi 'switch' type)
            telegram.payload = BinaryPayload(telegram.payload.content)
            self.interface.add_to_sending_queue([telegram])
        elif isinstance(
            telegram.payload, FloatPayload
        ):  # Sensors values sent regularly on bus
            self.interface.add_to_sending_queue([telegram])

    def get_dev_info(self) -> None:
        """IP Interface is not considered as a real device and has no specific attributes/characteristics, method implemented to respect the definition of abstract class Actuators"""
        return None
