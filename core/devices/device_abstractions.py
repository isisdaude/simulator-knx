"""
Gather the abstract class definitions for the simulated KNX devices.
"""

from abc import ABC, abstractmethod


class Device(ABC):
    """ Root Class module for KNX Devices (Sensors, Actuators and System devices)
    """
    def __init__(self, name, refid, individual_addr, default_status, dev_type): #The constructor is also a good place for imposing various checks on attribute values
        self.name = name
        self.refid = refid
        self.status: bool = default_status  # enable/disable status determine if sensor is activated or not, kind of power switch

        # Init addresses
        self.group_addr = 'ga not set'
        self.individual_addr = individual_addr

        #TODO: not necessary because already included in device types:
        if dev_type in ["actuator", "sensor", "sysdevice"]: #TODO: maybe create a config file, with the list of different types?
            self.dev_type = dev_type # usefull when we add device to rooms (e.g. to add a light to the light_soucres list)
        else:
            print("error, device type unknown") # -> Cannot happen because we give th epossible types

    # def set_group_addr(self, group_addr):
    #     """Method to make this device part of a certain group address"""
    #     self.group_addr = group_addr
    #
    # def get_group_addr(self):
    #     """Method to get the group addresses of this device"""
    #     return self.group_addr

    def is_enabled(self) -> bool:
        """True if the device is enabled (= active+connected) on the KNX bus"""
        return self.status

    def __repr__(self): # syntax to return when instance is called in the interactive python interpreter
        return f"Device({self.name!r}, {self.refid!r}, status:{self.is_enabled()!r}, {self.individual_addr!r}, {self.group_addr!r})"

    def __str__(self): # syntax when instance is called with print()
        return f"Device : {self.name}  {self.refid}  status:{self.is_enabled()}  {self.individual_addr}  {self.group_addr}"


class FunctionalModule(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status, input_type):
        super().__init__(name, refid, individual_addr, default_status, "functional_module")
        if input_type in ["button", "dimmer"]:
            self.input_type = input_type
        else:
            print("input type unknown") #TODO: write an error handling code

        self._observers = [] #list of _ because private list, still visible from outside, but convention to indicate privacy with _


    def notify(self, notifier): # alert the _observers
        for observer in self._observers:
            observer.update(notifier) #the observer (KNXBus class in room) must have an update method

    def attach(self, observer): #If not in list, add the observer to the list
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer): # Remove the observer from the list
        try:
            self._observers.remove(observer)
        except ValueError:
            pass



class Sensor(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status, sensor_type):
        super().__init__(name, refid, individual_addr, default_status, "sensor")

        #TODO: necessary?
        if sensor_type in ["button", "brightness", "temperature"]:
            self.sensor_type = sensor_type  # usefull to differentiate light, temperature, humidity,...
        else:
            print("sensor type unknown")#TODO: write an error handling code


class Actuator(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status,  actuator_type, default_state=False):
        super().__init__(name, refid, individual_addr, default_status, "actuator")

        self.state = default_state #=OFF if not indicated

        #TODO: necessary?
        if actuator_type in ["light", "heater", "cooler"]:
            self.actuator_type = actuator_type
        else:
            print("actuator_type unknown")

    def switch_state(self):
        self.state = not (self.state)

    def update(self, functional_module):
        print(f"KNX Bus notified {self.name} of the state: {functional_module.state} of the functional module {functional_module.name}")
        self.state = functional_module.state


class SysDevice(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "sys_device")
