"""
Gather the abstract class definitions for the simulated KNX devices.
"""

from abc import ABC, abstractmethod


class Device(ABC):
    """ Root Class module for KNX Devices (Sensors, Actuators and System devices)
    """
    def __init__(self, name, refid, individual_addr, default_status, type): #The constructor is also a good place for imposing various checks on attribute values
        self.name = name
        self.refid = refid
        self.individual_addr = individual_addr
        self.status = default_status  # enable/disable status determine if sensor is activated or not, kind of ON/OFF
        self.type = type # usefull when we add device to rooms (e.g. to add a light to the light_soucres list)
        # Init addresses
        self.group_addr = 'ga not set'

    def set_individual_addr(self, individual_addr):
        self.individual_addr = individual_addr

    def set_group_addr(self, group_addr):
        self.group_addr = group_addr

    def get_individual_addr(self):
        return self.individual_addr

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
    def __init__(self, name, refid, line, default_status, sensor_type):
        super().__init__(name, refid, line, default_status, "sensor")
        self.sensor_type = sensor_type  # ausefull to differentiate light, temperature, humidity,...



class Actuator(Device, ABC):
    def __init__(self, name, refid, line, default_status,  actuator_type):
        super().__init__(name, refid, line, default_status, "actuator")
        self.actuator_type = actuator_type

    def turnOn(self):
        self.status = True

    def turnOff(self):
        self.status = False

class SysDevice(Device, ABC):
    def __init__(self, name, refid, line, default_status):
        super().__init__(name, refid, line, default_status)
