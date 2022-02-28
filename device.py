"""
Gather the class definitions for the simulated KNX devices
"""


class Device:
    def __init__(self, name, id, location, status):
        self.name = name
        self.id = id
        self.location = location
        self.status = status  # status determine if sensor is activated or not, kind of ON/OFF


class Sensor(Device):
    def __init__(self, sensor_type):
        super().__init__(name, id, location, status)
        self.sensor_type = sensor_type  # active or passive, just to add a specific argument to class sensor



class Actuator(Device):
    def __init__(self, act_state):
        super().__init__(name, id, location, status)

        
        
class SysDevice(Device):
    def __init__(self, name):
        self.name = name
