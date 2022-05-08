
import logging
from typing import List

from .tools import GroupAddress
from devices import Actuator, Sensor, FunctionalModule
from .telegrams import Telegram
from interface.communication_interface import CommunicationInterface

# TODO: add an async function that checks whether there are telegrams to be transmitted from svshi, maybe in the callback function of the interface!

class KNXBus:
    '''Class that implements the transmission over the KNX Bus, between Actuators and FuntionalModules'''

    def __init__(self):
        self.name = "KNX Bus"
        self.group_addresses = []  # list of group addresses
        # list of group address buses
        self.ga_buses: List[GroupAddressBus] = []
        self.temp_actuaors = []
        self.temp_functional = []
        self.group_address_to_payload_type = {}
        # TODO: add this to the bus with proper variables
        self.communication_interface = CommunicationInterface('localhost', '???', self.group_address_to_payload_type)
        self.communication_interface.start_communication()

    # If not in list, add the observer to the list
    def attach(self, device, group_address: GroupAddress):
        '''Adds a device to the knx bus'''
        if group_address in device.group_addresses:
            logging.info(
                f"{device.name} is already connected to the KNX Bus through {group_address.name}")
            return
        else:
            if isinstance(device, FunctionalModule):
                try:
                    device.knxbus == self
                    self.__update_group_address_to_payload(device, group_address)
                except AttributeError:  # if bus is not connected yet
                    # store KNX Bus object in functional module class
                    device.connect_to(self)
                    logging.info(
                        f"Functional Module {device.name} establish connection to the bus (KNXBus object stored in device's class)")

            if group_address not in self.group_addresses:  # if ga not in group_addresses of KNXBus
                logging.info(
                    f"Creation of a ga_bus ({group_address.name}) for {device.name}")
                self.group_addresses.append(group_address)
                # Creation of the instance that link all devices connected to this group address
                ga_bus = GroupAddressBus(group_address)
                ga_bus.add_device(device)
                # we add the new object to the list
                self.ga_buses.append(ga_bus)
            else:  # if the group address already exists, we just add the device to the corresponding class GroupAddressBus
                for ga_bus in self.ga_buses:
                    if ga_bus.group_address == group_address:
                        logging.info(
                            f"{device.name} is added to the ga_bus ({group_address.name})")
                        ga_bus.add_device(device)

    # Remove the device from the group address
    def detach(self, device, group_address: GroupAddress):
        '''Removes a device from the knx bus'''
        if group_address not in self.group_addresses:
            logging.warning(
                f"The group address '{group_address.name}' is not linked to any device.")
            return
        elif group_address not in device.group_addresses:
            logging.warning(
                f"The group address '{group_address.name}' is not linked to {device.name}.")
        else:
            for ga_bus in self.ga_buses:
                if ga_bus.group_address == group_address:
                    if not ga_bus.detach_device(device):
                        self.ga_buses.remove(ga_bus)
                        self.group_addresses.remove(group_address)
                        logging.info(
                            f"The ga_bus ({group_address.name}) is deleted as no devices are connected to it.")
 
    # notifier is a functional module (e.g. button)
    def transmit_telegram(self, telegram):
        '''Transmits a telegram through the bus'''
        #print("telegram in transmission")
        print(telegram)
        for ga_bus in self.ga_buses:
            if telegram.destination == ga_bus.group_address:
                # Sending to external applications
                self.communication_interface.add_telegram_to_send(telegram)
                # TODO: send telegrams to all devices connected to this group address (not only actuators), and let them manage and interpret it
                for actuator in ga_bus.actuators:  # loop on actuator linked to this group address
                    actuator.update_state(telegram)
                # for functional_module in ga_bus.functional_modules:
                #     functional_module.update_state(telegram)
                # for functional in ga_bus.functional_modules:
                #     functional.receive_telegram(telegram)

    def __update_group_address_to_payload(self, device: FunctionalModule, group_address: GroupAddress):
        # TODO: Heater does not send telegrams for the moment
        from simulator.devices.functional_modules import Switch, TemperatureController
        from simulator.system.telegrams import SwitchPayload, TempControllerPayload

        # TODO: can add other devices here
        if isinstance(device, Switch):
            self.group_address_to_payload_type.update(
                (str(group_address), SwitchPayload))
        elif isinstance(device, TemperatureController):
            self.group_address_to_payload_type.update(
                (str(group_address), TempControllerPayload))

        # TODO: to be added when async things handled correctly
        # self.communication_interface.group_address_to_payload = self.group_address_to_payload_type


class GroupAddressBus:
    def __init__(self, group_address: GroupAddress):
        self.group_address = group_address
        self.sensors: List[Sensor] = []
        self.actuators: List[Actuator] = []
        self.functional_modules: List[FunctionalModule] = []

    def add_device(self, device):
        device.group_addresses.append(self.group_address)
        logging.info(
            f"{self.group_address.name} added to {device.name}'s connections")
        if isinstance(device, Actuator):
            self.actuators.append(device)
        if isinstance(device, FunctionalModule):
            self.functional_modules.append(device)
        if isinstance(device, Sensor):
            self.sensors.append(device)

    def detach_device(self, device):
        if isinstance(device, Actuator):
            try:
                self.actuators.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}")
        if isinstance(device, FunctionalModule):
            try:
                self.functional_modules.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}")
        if isinstance(device, Sensor):
            try:
                self.sensors.remove(device)
            except ValueError:
                logging.warning(
                    f"{device.name} is not stored in ga_bus {self.group_address.name}")
        device.group_addresses.remove(self.group_address)
        logging.info(
            f"{self.group_address.name} removed from {device.name}'s connections")
        return (len(self.sensors) + len(self.actuators) + len(self.functional_modules))
