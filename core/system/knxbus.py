
import logging
from .tools import GroupAddress, Telegram, IndividualAddress
from devices import Actuator, Sensor, FunctionalModule


class KNXBus:
    '''Class that implements the transmission over the KNX Bus, between Actuators and FuntionalModules'''
    def __init__(self):
        self.name = "KNX Bus"
        self.group_addresses = [] # list of group addresses
        self.ga_buses = [] # list of group address buses
        self.temp_actuaors = []
        self.temp_functional = []

    def attach(self, device, group_address : GroupAddress): #If not in list, add the observer to the list
        if isinstance(device, Sensor):
            if device.group_address == group_address:
                logging.info(f"The sensor {device.name} is already connected to the KNX Bus through this group address")
                return
            else:
                device.group_address == group_address
        if isinstance(device, Actuator):
            if group_address in device.group_addresses:
                logging.info(f"The actuator {device.name} is already connected to the KNX Bus through this group address")
                return
            else:
                #TODO: loop in temp_functional to sedn power values
                device.group_addresses.append(group_address) # we add the group address in the local list of group addresses to which the device is connected to
        if isinstance(device, FunctionalModule):
            if group_address in device.group_addresses:
                logging.info(f"The functional module {device.name} is already connected to the KNX Bus through this group address")
                return
            else:
                logging.info(f"{device.name} is added to the bus")
                device.connect_to(self) # store KNX Bus object in functional module class
                device.group_addresses.append(group_address) # we add the group address in the local list of group addresses to which the device is connected to

        if group_address not in self.group_addresses: # if ga not in group_addresses of KNXBus
            logging.info(f"Creation of a ga_bus for {device.name}")
            self.group_addresses.append(group_address)
            ga_bus = GroupAddressBus(group_address) # Creation of the instance that link all devices connected to this group address
            ga_bus.add_device(device)
            self.ga_buses.append(ga_bus) # we add the new object to the list
        else: # if the group address already exists, we just add the device to the corresponding class GroupAddressBus
            for ga_bus in self.ga_buses:
                if ga_bus.group_address == group_address:
                    logging.info(f"{device.name} is added to the ga_bus")
                    ga_bus.add_device(device)


    def detach(self, device, group_address:GroupAddress): # Remove the device from the group address
        if group_address not in self.group_addresses:
            logging.warning(f"The device {device.name} cannot be detached from the bus: the group address '{group_address}' is not assigned")
            return
        for ga_bus in self.ga_buses:
            if ga_bus.group_address == group_address:
                ga_bus.detach_device(device)

    # def remove_device(self, device):



    def transmit_telegram(self, telegram): # notifier is a functional module (e.g. button)
        #print("telegram in transmission")
        print(telegram)
        for ga_bus in self.ga_buses:
            if telegram.destination == ga_bus.group_address:
                for actuator in ga_bus.actuators: # loop on actuator linked to this group address
                    actuator.update_state(telegram)
                # for functional_module in ga_bus.functional_modules:
                #     functional_module.update_state(telegram)


class GroupAddressBus:
    def __init__(self, group_address:GroupAddress):
        self.group_address = group_address
        self.sensors = []
        self.actuators = []
        self.functional_modules = []


    def add_device(self, device):
        if isinstance(device, Actuator):
            self.actuators.append(device)
        if isinstance(device, FunctionalModule):
            self.functional_modules.append(device)
        if isinstance(device, Sensor):
            self.sensors.append(device)

    def detach_device(self, device):
        if isinstance(device, Actuator):
            self.actuators.remove(device)
        if isinstance(device, FunctionalModule):
            self.functional_modules.remove(device)
        if isinstance(device, Sensor):
            self.sensors.remove(device)
