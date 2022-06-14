"""
Class definitions to implement the KNX Bus object representation and emulate the behaviour of a KNX system.
The GroupAddressBus class gather all devices assigned to a particular group address.
"""

import logging
import sys
import traceback
from typing import List, Dict, Union

from system.system_tools import GroupAddress
from system.telegrams import Telegram


class KNXBus:
    """
    Class to represent the KNX Bus.
    Manage the transmission of telegrams over the KNX Bus, between Devices.
    """

    def __init__(self) -> None:  # , svshi_mode: bool
        """
        Initialization of the KNX Bus object.

        group_addresses : list of group addresses defined in the system
        __ga_buses : list of GroupAddressBus objects, 
        containing list of devices assigned to a particular group address"""
        self.name = "KNX Bus"
        self.group_addresses = []
        self.__ga_buses: List[GroupAddressBus] = []

    def attach(
        self, device, group_address: GroupAddress
    ) -> None:  # device : Device, not InRoomDevice
        """
        Assign a device to a group address, and connect it to the bus.
        The KNX Bus object can then call the correct devices' method 
        when a telegram arrive with corresponding destination address:
        (e.g. actuator.update_state() in transmit_telegram())
        If it is a new group address, creation of a GroupAddressBus object,
        if it is a new device on existing group address, addition of the device to the GroupAddressBus object.

        device : Device, not InRoomDevice
        """
        if group_address in device.group_addresses:
            logging.info(
                f"{device.name} is already connected to the KNX Bus through {group_address.name}."
            )
        else:
            if group_address not in self.group_addresses:
                logging.info(
                    f"Creation of a ga_bus ({group_address.name}) for {device.name}."
                )
                self.group_addresses.append(group_address)
                ga_bus = GroupAddressBus(group_address)
                ga_bus.add_device(device)
                self.__ga_buses.append(ga_bus)
            else:
                for ga_bus in self.__ga_buses:
                    if ga_bus.group_address == group_address:
                        logging.info(
                            f"{device.name} is added to the ga_bus ({group_address.name})."
                        )
                        ga_bus.add_device(device)

    def detach(
        self, device, group_address: GroupAddress
    ) -> None:  # device : Device, not InRoomDevice
        """Remove devices from KNX Bus object, from GroupAddressBus objects, 
        and delete group adrress from device' group addresses list."""
        if group_address not in self.group_addresses:
            logging.warning(
                f"The group address '{group_address.name}' is not linked to any device, thus device {device.name} cannot be detached from it"
            )
        elif group_address not in device.group_addresses:
            logging.warning(
                f"The group address '{group_address.name}' is not linked to {device.name}, that thus cannot be detached from it."
            )
        else:
            for ga_bus in self.__ga_buses:
                if ga_bus.group_address == group_address:
                    if not ga_bus.detach_device(
                        device
                    ):  # return number of devices linked to this ga_bus after removal of device, if none, we delete the ga bus
                        self.__ga_buses.remove(ga_bus)
                        self.group_addresses.remove(group_address)
                        logging.info(
                            f"The ga_bus ({group_address.name}) is deleted as no devices are connected to it."
                        )

    def transmit_telegram(self, telegram: Telegram) -> None:
        """
        Transmit a telegram on the bus to other devicdes assigned to the destination address.
        Method called when Device.send_telegram() is called or when svshi interface receives a telegram from svshi.
        """
        for ga_bus in self.__ga_buses:
            if telegram.destination == ga_bus.group_address:
                # Only actuators for now, but sensors and functional module could also receive telegrams to read state fro instance.
                for actuator in ga_bus.actuators:
                    try:
                        actuator.update_state(telegram)
                    except AttributeError:
                        logging.warning(
                            f"The actuator {actuator.name} or the telegram created is missing an Attribute."
                        )
                    except:
                        exc = sys.exc_info()[0]
                        trace = traceback.format_exc()
                        logging.warning(
                            f"[KNXBus.transmit_telegram()] - Transmission of the telegram from source '{telegram.source}' failed: {exc} with trace \n{trace}."
                        )

    def get_info(self) -> Dict[str, Union[str, Dict[str, Dict[str, List[str]]]]]:
        """Return information about the KNX Bus configuration, 
        and the devices assigned to each group address, method called via CLI commmand 'getinfo'"""
        bus_dict = {"name": self.name, "group_addresses": {}}
        for ga_bus in self.__ga_buses:
            str_ga = ga_bus.group_address.name
            ga_dict = {str_ga: {}}
            sensor_names = []
            for sensor in ga_bus.sensors:
                sensor_names.append(sensor.name)
            if len(sensor_names):
                ga_dict[str_ga]["Sensors"] = sensor_names
            actuator_names = []
            for actuator in ga_bus.actuators:
                actuator_names.append(actuator.name)
            if len(actuator_names):
                ga_dict[str_ga]["Actuators"] = actuator_names
            functional_module_names = []
            for functional_module in ga_bus.functional_modules:
                functional_module_names.append(functional_module.name)
            if len(functional_module_names):
                ga_dict[str_ga]["Functional Modules"] = functional_module_names
            bus_dict["group_addresses"].update(ga_dict)
        return bus_dict


class GroupAddressBus:
    """Class to gather devices assigned to a particular group address."""

    def __init__(self, group_address: GroupAddress) -> None:
        """Initialization of a group address bus object"""
        from devices import Actuator, Sensor, FunctionalModule

        self.group_address = group_address
        self.sensors: List[Sensor] = []
        self.actuators: List[Actuator] = []
        self.functional_modules: List[FunctionalModule] = []

    def add_device(self, device) -> None:  # device : Device, not InRoomDevice
        """Add a device to the corresponding list (actuators, sensors or functional modules), 
        and add the group address to the device's list of ga"""
        from devices import Actuator, Sensor, FunctionalModule

        device.group_addresses.append(self.group_address)
        logging.info(
            f"{device.name} can receive telegrams from the bus, {self.group_address.name} added to device's group addresses list."
        )
        if isinstance(device, Actuator):
            self.actuators.append(device)
        if isinstance(device, FunctionalModule):
            self.functional_modules.append(device)
        if isinstance(device, Sensor):
            self.sensors.append(device)

    def detach_device(self, device) -> int:  # device : Device, not InRoomDevice
        """Remove a device to the corresponding list, and remove the group address from the device's list of ga."""
        from devices import Actuator, Sensor, FunctionalModule

        if isinstance(device, Actuator):
            try:
                self.actuators.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}."
                )
        if isinstance(device, FunctionalModule):
            try:
                self.functional_modules.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}."
                )
        if isinstance(device, Sensor):
            try:
                self.sensors.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}."
                )
        device.group_addresses.remove(self.group_address)
        logging.info(
            f"{self.group_address.name} removed from {device.name}'s group addresses."
        )
        return len(self.sensors) + len(self.actuators) + len(self.functional_modules)
