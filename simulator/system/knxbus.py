"""
Module that implement the KNX Bus object representation to emulate the real behaviour of a KNX system.
"""

import logging
import sys
import traceback
from typing import List

from system.system_tools import GroupAddress


class KNXBus:
    '''Class that implements the transmission over the KNX Bus, between Actuators and FuntionalModules'''

    def __init__(self, svshi_mode: bool):
        self.name = "KNX Bus"
        self.__svshi_mode = svshi_mode
        self.group_addresses = []  # list of group addresses
        # list of group address buses
        self.__ga_buses: List[GroupAddressBus] = []
        self.__group_address_to_payload_type = {}

    # If not in list, add the observer to the list
    def attach(self, device, group_address: GroupAddress):
        '''Adds a device to the knx bus'''
        # from devices import FunctionalModule
        if group_address in device.group_addresses:
            logging.info(
                f"{device.name} is already connected to the KNX Bus through {group_address.name}.")
            return
        else:
        #     if isinstance(device, FunctionalModule):
        #         self.__update_group_address_to_payload(device, group_address)
  
            if group_address not in self.group_addresses:  # if ga not in group_addresses of KNXBus
                logging.info(
                    f"Creation of a ga_bus ({group_address.name}) for {device.name}.")
                self.group_addresses.append(group_address)
                # Creation of the instance that link all devices connected to this group address
                ga_bus = GroupAddressBus(group_address)
                ga_bus.add_device(device) # add ga to devices ga list
                # we add the new object to the list
                self.__ga_buses.append(ga_bus)
            else:  # if the group address already exists, we just add the device to the corresponding class GroupAddressBus
                for ga_bus in self.__ga_buses:
                    if ga_bus.group_address == group_address:
                        logging.info(
                            f"{device.name} is added to the ga_bus ({group_address.name}).")
                        ga_bus.add_device(device) # add ga to devices ga list

    # Remove the device from the group address
    def detach(self, device, group_address: GroupAddress):
        '''Removes a device from the knx bus'''
        if group_address not in self.group_addresses:
            logging.warning(
                f"The group address '{group_address.name}' is not linked to any device, thus device {device.name} cannot be detached.")
            return
        elif group_address not in device.group_addresses:
            logging.warning(
                f"The group address '{group_address.name}' is not linked to {device.name}, that thus cannot be detached.")
        else:
            for ga_bus in self.__ga_buses:
                if ga_bus.group_address == group_address:
                    if not ga_bus.detach_device(device): # return number of devices linked to this ga_bus, if none, we delete the ga bus
                        self.__ga_buses.remove(ga_bus)
                        self.group_addresses.remove(group_address)
                        logging.info(
                            f"The ga_bus ({group_address.name}) is deleted as no devices are connected to it.")
 
    # notifier is a functional module (e.g. button)
    def transmit_telegram(self, telegram):
        '''Transmits a telegram through the bus'''
        for ga_bus in self.__ga_buses:
            if telegram.destination == ga_bus.group_address:
                # Sending to external applications
                # TODO: send telegrams to all devices connected to this group address (not only actuators), and let them manage and interpret it
                for actuator in ga_bus.actuators:  # loop on actuator linked to this group address
                    # print(f"actuator: {actuator.name}")
                    try:
                        actuator.update_state(telegram)
                    except AttributeError:
                        logging.warning(f"The actuator {actuator.name} or the telegram created is missing an Attribute.")
                    except:
                        exc = sys.exc_info()[0]
                        trace = traceback.format_exc()
                        logging.warning(f"[KNXBus.transmit_telegram()] - Transmission of the telegram from source '{telegram.source}' failed: {exc} with trace \n{trace}.")
                # NOTE: for further implementation with functional_modules and sensors receiving telegrams
                # for functional_module in ga_bus.functional_modules:
                #     functional_module.function_to_call(telegram)
                # for functional in ga_bus.functional_modules:
                #     functional.function_to_call(telegram)


    # def __update_group_address_to_payload(self, device: FunctionalModule, group_address: GroupAddress):
    #     from system.telegrams import BinaryPayload
    #     pass
    #     # TODO: which else need to be handled?
    #     # print((str(group_address), BinaryPayload)
    #     # self.__group_address_to_payload_type.update((str(group_address), BinaryPayload))
    #     # TODO: to be added when async things handled correctly
    #     # self.communication_interface.group_address_to_payload = self.__group_address_to_payload_type
    
    def get_info(self):
        bus_dict = {"name": self.name, "group_addresses":{}}
        for ga_bus in self.__ga_buses:
            str_ga = ga_bus.group_address.name
            ga_dict = {str_ga: {}}
            sensor_names = []
            for sensor in ga_bus.sensors:
                sensor_names.append(sensor.name)
            if len(sensor_names):
                ga_dict[str_ga]['Sensors'] = sensor_names
            actuator_names = []
            for actuator in ga_bus.actuators:
                actuator_names.append(actuator.name)
            if len(actuator_names):
                ga_dict[str_ga]['Actuators'] = actuator_names
            functional_module_names = []
            for functional_module in ga_bus.functional_modules:
                functional_module_names.append(functional_module.name)
            if len(functional_module_names):
                ga_dict[str_ga]['Functional Modules'] = functional_module_names

            bus_dict["group_addresses"].update(ga_dict)
        return bus_dict




class GroupAddressBus:
    def __init__(self, group_address: GroupAddress):
        from devices import Actuator, Sensor, FunctionalModule
        self.group_address = group_address
        self.sensors: List[Sensor] = []
        self.actuators: List[Actuator] = []
        self.functional_modules: List[FunctionalModule] = []

    def add_device(self, device):
        from devices import Actuator, Sensor, FunctionalModule
        device.group_addresses.append(self.group_address)
        logging.info(
            f"{self.group_address.name} added to {device.name}'s connections.")
        if isinstance(device, Actuator):
            self.actuators.append(device)
        if isinstance(device, FunctionalModule):
            self.functional_modules.append(device)
        if isinstance(device, Sensor):
            self.sensors.append(device)

    def detach_device(self, device):
        from devices import Actuator, Sensor, FunctionalModule
        if isinstance(device, Actuator):
            try:
                self.actuators.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}.")
        if isinstance(device, FunctionalModule):
            try:
                self.functional_modules.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}.")
        if isinstance(device, Sensor):
            try:
                self.sensors.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}.")
        device.group_addresses.remove(self.group_address)
        logging.info(
            f"{self.group_address.name} removed from {device.name}'s connections.")
        return (len(self.sensors) + len(self.actuators) + len(self.functional_modules))
