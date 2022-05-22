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
        super().__init__('Brightness', name, refid, location, default_status, "brightness")
        self.brightness = 0
    
    def get_dev_info(self):
        dev_specific_dict = {"brightness":self.brightness}
        dev_specific_dict.update(self.dev_basic_dict)
        return dev_specific_dict

class Thermometer(Sensor):
    """Concrete class to represent a thermometer"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('Thermometer', name, refid, location, default_status, "temperature")
        # DTP
        self.temperature = 0
    def get_dev_info(self):
        dev_specific_dict = {"temperature":self.temperature}
        dev_specific_dict.update(self.dev_basic_dict)
        return dev_specific_dict

class HumiditySensor(Sensor):
    """Concrete class to represent a Humidity sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('HumiditySensor', name, refid, location, default_status, "humidity")
        self.humidity = 0
    def get_dev_info(self):
        dev_specific_dict = {"humidity":self.humidity}
        dev_specific_dict.update(self.dev_basic_dict)
        return dev_specific_dict

class CO2Sensor(Sensor):
    """Concrete class to represent a CO2 Sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('CO2Sensor', name, refid, location, default_status, "co2")
        self.co2level = 0
    def get_dev_info(self):
        dev_specific_dict = {"co2level":self.co2level}
        dev_specific_dict.update(self.dev_basic_dict)
        return dev_specific_dict

class AirSensor(Sensor):
    """Concrete class to represent am Air Sensor: CO2, Humidity and/or Temperature"""
    def __init__(self, name, refid, location, default_status, temp_supported=False, hum_supported=False, co2_supported=False):
        super().__init__('AirSensor', name, refid, location, default_status, "air")
        if temp_supported:
            self.temperature = None
        if hum_supported:
            self.humidity = None
        if co2_supported:
            self.co2level = None
    def get_dev_info(self):
        dev_specific_dict = {"temperature":self.temperature, "humidity":self.humidity, "co2level":self.co2level}
        dev_specific_dict.update(self.dev_basic_dict)
        return dev_specific_dict

class PresenceSensor(Sensor):
    """Concrete class to represent a Presence Detector"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('PresenceSensor', name, refid, location, default_status, "presence")
        self.presence = False
    def get_dev_info(self):
        dev_specific_dict = {"presence":self.presence}
        dev_specific_dict.update(self.dev_basic_dict)
        return dev_specific_dict

# class MovementDetector(Sensor):
#     """Concrete class to represent a CO2 Sensor"""
#     def __init__(self, name, refid, location, default_status):
#         super().__init__('MovementDetector', name, refid, location, default_status, "movement")
#         self.movement = False


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
