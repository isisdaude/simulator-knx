"""
Some class definitions for the simulated KNX sensors.
"""
from .device_abstractions import Sensor
from abc import ABC, abstractclassmethod

class Brightness(Sensor):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "brightness")


class Temperature(Sensor):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "temperature")
