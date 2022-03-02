"""
Gather the class definitions for the simulated KNX devices
"""


class Device:
    def __init__(self, device_type, name, id, location, status): #The constructor is also a good place for imposing various checks on attribute values
        self.device_type = device_type  # 'sensor' 'actuator' 'system'
        self.name = name
        self.id = id
        self.location = location
        self.status = status  # status determine if sensor is activated or not, kind of ON/OFF

    def __repr__(self):
        return f"Device({self.device_type!r}, {self.name!r}, {self.id!r}, {self.location!r}, {self.status!r})"

    def __str__(self):
        return f"DEvice: {self.device_type} {self.name} {self.id} {self.location} {self.status}"


class Sensor(Device):
    def __init__(self, device_type, name, id, location, status, sensor_type):
        super().__init__(device_type, name, id, location, status)
        self.sensor_type = sensor_type  # active or passive, just to add a specific argument to class sensor



class Actuator(Device):
    def __init__(self, device_type, name, id, location, status,  actuator_type):
        super().__init__(device_type, name, id, location, status)
        self.actuator_type = actuator_type



class SysDevice(Device):
    def __init__(self, device_type, name, id, location, status):
        super().__init__(device_type, name, id, location, status)
