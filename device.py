"""
Gather the class definitions for the simulated KNX devices.
"""


class Device:
    """ Root Class module for KNX Devices (Sensors, Actuators and System devices)
    """
    def __init__(self, device_type, name, refid, location, status): #The constructor is also a good place for imposing various checks on attribute values
        self.device_type = device_type  # 'sensor' 'actuator' 'system'
        self.name = name
        self.refid = refid
        self.location = location
        self.status = status  # status determine if sensor is activated or not, kind of ON/OFF
        # Init addresses
        self.individual_addr = 'ia not set'
        self.group_addr = 'ga not set'

    def set_individual_addr(self, individual_addr):
        self.individual_addr = individual_addr

    def set_group_addr(self, group_addr):
        self.group_addr = group_addr


    def __repr__(self): # syntax to return when instance is called in the interactive python interpreter
        return f"Device({self.device_type!r}, {self.name!r}, {self.refid!r}, {self.location!r}, {self.status!r}, {self.individual_addr!r}, {self.group_addr!r})"

    def __str__(self): # syntax when instance is called with print()
        return f"Device - {self.device_type} : {self.name}  {self.refid}  {self.location}  {self.status}  {self.individual_addr}  {self.group_addr}"


class Sensor(Device):
    def __init__(self, device_type, name, refid, location, status, sensor_type):
        super().__init__(device_type, name, refid, location, status)
        self.sensor_type = sensor_type  # active or passive, just to add a specific argument to class sensor



class Actuator(Device):
    def __init__(self, device_type, name, refid, location, status,  actuator_type):
        super().__init__(device_type, name, refid, location, status)
        self.actuator_type = actuator_type



class SysDevice(Device):
    def __init__(self, device_type, name, refid, location, status):
        super().__init__(device_type, name, refid, location, status)
