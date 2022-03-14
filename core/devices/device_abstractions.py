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
        self.individual_addr = individual_addr
        self.status = default_status  # enable/disable status determine if sensor is activated or not, kind of ON/OFF
        if dev_type in ["actuator", "sensor", "sysdevice"]: #TODO: maybe create a config file, with the list of different types?
            self.dev_type = dev_type # usefull when we add device to rooms (e.g. to add a light to the light_soucres list)
        else:
            print("error, device type unknown")
            #TODO: raise error
        # Init addresses
        self.group_addr = 'ga not set'

    #def set_individual_addr(self, individual_addr):
        #self.individual_addr = individual_addr
    #def get_individual_addr(self):
        #return self.individual_addr

    def set_group_addr(self, group_addr):
        self.group_addr = group_addr

    def get_group_addr(self):
        return self.group_addr

    def set_physical_location(self, x, y): # relative to the current room, for now
        self.loc_x = x ##TODO: change with a class location
        self.loc_y = y ## so that we have self.loc.x et self.loc.y

    def get_status(self): #TODO: rename it to on/off, and add attribute that really represent status to sensors
        return self.status

    def __repr__(self): # syntax to return when instance is called in the interactive python interpreter
        return f"Device({self.name!r}, {self.refid!r}, {self.status!r}, {self.individual_addr!r}, {self.group_addr!r})"

    def __str__(self): # syntax when instance is called with print()
        return f"Device : {self.name}  {self.refid}  {self.status}  {self.individual_addr}  {self.group_addr}"


class Sensor(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status, sensor_type):
        super().__init__(name, refid, individual_addr, default_status, "sensor")
        if sensor_type in ["button", "brightness", "temperature"]:
            self.sensor_type = sensor_type  # usefull to differentiate light, temperature, humidity,...
        else:
            print("sensor type unknown")


class Actuator(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status,  actuator_type, state):
        super().__init__(name, refid, individual_addr, default_status, "actuator")
        if actuator_type in ["light", "heater", "cooler"]:
            self.actuator_type = actuator_type
        else:
            print("actuator_type unknown")
        self.state = state # init at False=off for all actuators, unless especially expressed

    def switch_state(self):
        self.state = not (self.state)

    # def turnOn(self):
    #     self.status = True
    # def turnOff(self):
    #     self.status = False

class SysDevice(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "sysdevice")
