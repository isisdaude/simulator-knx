"""
Some class definitions for the simulated KNX sensors.
"""
import logging
from .device_abstractions import Sensor
from abc import ABC, abstractclassmethod

# class Button(Sensor):
#     """Concrete class to represent buttons"""
#     def __init__(self, name, refid, location, default_status):
#         super().__init__(name, refid, location, default_status, "button")
#         self.state = False

#     def press(self):
#         if(self.state == True):
#             self.state = False
#         else:
#             self.state = True

class Brightness(Sensor):
    """Concrete class to represent a sensor of brightness"""
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "brightness")
        self.brightness = 0

class Thermometer(Sensor):
    """Concrete class to represent a thermometer"""
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "temperature")
        # DTP
        self.temperature = 0

class HumiditySensor(Sensor):
    """Concrete class to represent a Humidity sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "humidity")
        self.humidity = 0

class CO2Sensor(Sensor):
    """Concrete class to represent a CO2 Sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "co2")
        self.co2level = 0


class PresenceDetector(Sensor):
    """Concrete class to represent a CO2 Sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "presence")
        self.presence = False

class MovementDetector(Sensor):
    """Concrete class to represent a CO2 Sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "movement")
        self.movement = False


# if type == "binary":
#                 type = "BinarySensor"
#             elif type == "temperature":
#                 type = "TemperatureSensor"
#             elif type == "humidity":
#                 type = "HumiditySensor"
#             elif type == "switch":
#                 type = "Switch"
#             elif type == "co2":
#                 type = "CO2Sensor"
