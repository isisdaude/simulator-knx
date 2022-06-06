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
    
    def get_dev_info(self, value=False):
        dev_specific_dict = {"brightness":str(round(self.brightness, 2))+" lux"}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

class Thermometer(Sensor):
    """Concrete class to represent a thermometer"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('Thermometer', name, refid, location, default_status, "temperature")
        # DTP
        self.temperature = 0
    def get_dev_info(self, value=False):
        dev_specific_dict = {"temperature":str(round(self.temperature, 2))+" °C"}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

class HumiditySoil(Sensor):
    """Concrete class to represent a Humidity sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('HumiditySoil', name, refid, location, default_status, "humiditysoil")
        self.humiditysoil = 10 # arbitrary init of soil humidity
    def get_dev_info(self, value=False):
        dev_specific_dict = {"humiditysoil":str(round(self.humiditysoil, 2))+" %"}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict
    def set_value(self, value):
        value = float(value)
        ## TODO check if its a number
        if value < 0 or value > 100:
            logging.warning(f"The soil humidity value shoudl be in (0-100), but {value} was given>=.")
            return None
        else:
            self.humiditysoil = value
            return 1

class HumidityAir(Sensor):
    """Concrete class to represent a Humidity sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('HumidityAir', name, refid, location, default_status, "humidity")
        self.humidity = 0
    def get_dev_info(self, value=False):
        dev_specific_dict = {"humidity":str(round(self.humidity, 2))+" %"}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

class CO2Sensor(Sensor):
    """Concrete class to represent a CO2 Sensor"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('CO2Sensor', name, refid, location, default_status, "co2")
        self.co2level = 0
    def get_dev_info(self, value=False):
        dev_specific_dict = {"co2level":str(round(self.co2level, 2))+" ppm"}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
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
    def get_dev_info(self, value=False):
        dev_specific_dict = {"temperature":str(round(self.temperature, 2))+" °C", "humidity":str(round(self.humidity, 2))+" %", "co2level":str(round(self.co2level, 2))+" ppm"}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

class PresenceSensor(Sensor):
    """Concrete class to represent a Presence Detector"""
    def __init__(self, name, refid, location, default_status):
        super().__init__('PresenceSensor', name, refid, location, default_status, "presence")
        # self.presence = False
        self.state = False
    def get_dev_info(self, value=False):
        dev_specific_dict = {"presence":self.state}
        if not value:
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict
    def set_value(self, value):
        value_bool = bool(value)
        if value_bool not in [True, False]:
            logging.warning(f"The presence value should be in [True, False], but {value} was given.")
            return None
        else:
            self.state = value_bool
            return 1

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
