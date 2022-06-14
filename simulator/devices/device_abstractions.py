"""
Abstract class and method definitions for simulated KNX devices:
Device, FunctionalModule, Sensor and Actuator.
"""

import logging
import sys
import traceback

from abc import ABC, abstractmethod
from typing import List


class Device(ABC):
    """Abstract root class to represent simulated KNX Devices"""

    from system.system_tools import IndividualAddress
    from system.telegrams import Payload
    from system.knxbus import KNXBus

    def __init__(
        self, name: str, individual_addr: IndividualAddress
    ) -> None:  # The constructor is also a good place for imposing various checks on attribute values
        """
        Initializaion of a simulated device instance

        class_name : name of the device's class (e.g. LED, Button,...), only used to check the davice's name
        name : should include its class name
        individual_addr : Individual Address of the device = position on the KNX bus (Area, Line, Device)
        """
        from tools import check_device_config
        from system.system_tools import GroupAddress

        class_name = type(self).__name__
        self.name, self.individual_addr = check_device_config(
            class_name, name, individual_addr
        )
        self._dev_basic_dict = {
            "class_name": class_name,
            "individual_address": self.individual_addr.ia_str,
        }  # Prepare dict for CLI 'getinfo' command
        self.group_addresses: List[GroupAddress] = []

    def __repr__(self):
        return f"Device({self.name!r}, {self.individual_addr!r})"

    def __str__(self):  # when called with print()
        return f"Device : {self.name}  {self.individual_addr} "

    def send_telegram(self, payload: Payload) -> None:
        """
        Construct a telegram with the given payload and send it on the bus.
        'knxbus' attribute is added to the device object with 'connect_to()' method,
        'connect_to()' method is called when added to the room with 'room.add_device()' method.
        'knxbus.transmit_telegram()' sends telegrams to all devices assigned to the same group addresses.
        """
        from system import Telegram

        for group_address in self.group_addresses:
            telegram = Telegram(self.individual_addr, group_address, payload)
            try:
                assert hasattr(self, "knxbus")
            except AssertionError:
                logging.warning(
                    f"The device '{self.name}' is not connected to the bus, and thus cannot send telegrams."
                )
            try:
                self.knxbus.transmit_telegram(telegram)
            except:
                exc = sys.exc_info()[0]
                trace = traceback.format_exc()
                logging.warning(
                    f"[Device.send_telegram()] - Transmission of the telegram from source '{telegram.source}' failed:{exc} with trace \n{trace}."
                )

    def connect_to(self, knxbus: KNXBus) -> None:
        """Add the knxbus object to device's attributes to send telegrams by calling 'knxbus.transmit_telegram()' method"""
        logging.info(
            f"{self.name} can send telegrams on the KNX Bus, knxbus object is added to device's class attributes."
        )
        self.knxbus = knxbus

    @abstractmethod
    def get_dev_info(self):
        """Abstract method that returns device's info in response to CLI command 'getinfo' from users"""


class FunctionalModule(Device, ABC):
    """
    Abstract class to represent Functional Module devices (actionable devices by user):
    Button and Dimmer.
    """

    from system.system_tools import IndividualAddress

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of a Functional Module instance"""
        super().__init__(name, individual_addr)

    @abstractmethod
    def user_input(self):
        """
        Interpret the user input/action (set button ON/OFF, ...) and send telegram on the bus
        Specific implementation for each functional module.
        Method called when user activated the device in the GUI (e.g. press a Button),
        or if he used CLI command 'set' to change a functional module state.
        """


class Sensor(Device, ABC):
    """
    Abstract class to represent Sensor devices (that read world states):
    Brightness, Thermometer, HumiditySoil, HumidityAir, CO2Sensor, AirSensor and PresenceSensor
    """

    from system.system_tools import IndividualAddress

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of a Sensor instance"""
        super().__init__(name, individual_addr)
        self.interface = None

    @abstractmethod
    def send_state(self):
        """
        Send periodically its state on the bus,
        only in svshi mode to run app with sensor value.
        Method called by its corresponding Ambient object (e.f. AmbientTemperature for Thermometer) at each world update.
        """


class Actuator(Device, ABC):
    """
    Abstract class to represent Actuator devices (that acto on world states):
    LED, Heater, AC, Switch and IPInterface
    """

    from system.system_tools import IndividualAddress
    from system.telegrams import Telegram

    def __init__(
        self, name: str, individual_addr: IndividualAddress, default_state: bool = False
    ) -> None:
        """
        Initialization of a Actuator instance.

        state : True/False if device is respectively turned ON/OF
        """
        super().__init__(name, individual_addr)
        self.state = default_state

    @abstractmethod
    def update_state(self, telegram: Telegram):
        """
        Update the state and/or state_ratio of device,
        Specific implementation for each actuator.
        Method called by the KNXBus object when receiving a telegram for one of actuators' group addresses.
        """
