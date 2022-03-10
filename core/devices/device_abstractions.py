"""
Gather the abstract class definitions for the simulated KNX devices.
"""

from abc import ABC, abstractmethod


class Device(ABC):
    """ Root Class module for KNX Devices (Sensors, Actuators and System devices)
    """
    def __init__(self, name, refid, line, default_status): #The constructor is also a good place for imposing various checks on attribute values
        self.name = name
        self.refid = refid
        self.line = line
        self.status = default_status  # status determine if sensor is activated or not, kind of ON/OFF
        # Init addresses
        self.individual_addr = 'ia not set'
        self.group_addr = 'ga not set'

    def set_individual_addr(self, individual_addr):
        self.individual_addr = individual_addr

    def set_group_addr(self, group_addr):
        self.group_addr = group_addr

    def get_individual_addr(self):
        return self.individual_addr

    def get_group_addr(self):
        return self.group_addr
         
    def get_status(self):
        return self.status

    def __repr__(self): # syntax to return when instance is called in the interactive python interpreter
        return f"Device({self.name!r}, {self.refid!r}, {self.location!r}, {self.status!r}, {self.individual_addr!r}, {self.group_addr!r})"

    def __str__(self): # syntax when instance is called with print()
        return f"Device : {self.name}  {self.refid}  {self.location}  {self.status}  {self.individual_addr}  {self.group_addr}"


class Sensor(Device, ABC):
    def __init__(self, name, refid, line, default_status, sensor_type):
        super().__init__(name, refid, line, default_status)
        self.sensor_type = sensor_type  # active or passive, just to add a specific argument to class sensor => do we really need to?

class Actuator(Device, ABC):
    def __init__(self, name, refid, line, default_status,  actuator_type):
        super().__init__(name, refid, line, default_status)
        self.actuator_type = actuator_type

class SysDevice(Device, ABC):
    def __init__(self, name, refid, line, default_status):
        super().__init__(name, refid, line, default_status)
