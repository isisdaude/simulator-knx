"""
Some class definitions for the rooms contained in the system
"""
from typing import List
from devices import *
from simulation import *
from abc import ABC, abstractclassmethod

class Room:
    #devices: List[Device] = []
    devices = []

    def __init__(self, name: str, width: int, length: int):
        self.name = name
        self.width = width #x
        self.length = length #y
        self.world = World()

    def add_device(self, device: Device, x: float, y: float):
        if(x < 0 or x > self.width or y < 0 or y > self.length):
            print("Cannot add a device outside the room!")
        else:
            device.set_physical_location(x, y)
            if device.dev_type == "actuator":
                if device.actuator_type == "light":
                    self.world.ambiant_light.add_lightsource(device) # add device to the light sources list, to be able to calculate brightness from any point of the room
                    print("light added")
                elif device.actuator_type == "heater":
                    self.world.ambiant_temperature.add_heatingsource(device)
                    print("heater added")
                elif device.actuator_type == "cooler":
                    self.world.ambiant_temperature.add_coolingsource(device)
                    print("cooler added")
            if device.dev_type == "sensor":
                if device.sensor_type == "button":
                    print("button added")
                elif device.sensor_type == "brightness":
                    print("brightness sensor added")
            self.devices.append(device)

    def __str__(self):
        str_repr =  f"# {self.name} is a room of dimensions {self.width} x {self.length} m2 with devices:\n"
        for device in self.devices:
            str_repr += f"-> {device.name} at location ({device.loc_x}, {device.loc_y})"
            if device.dev_type == "actuator":
                state = "ON" if device.state else "OFF"
                str_repr += f" is {state}"
            str_repr += "\n"
        return str_repr

    def __repr__(self):
        return f"Room {self.name}"


class System:
    pass #TODO: further in time, should be the class used for instantiation, should contain list of rooms + a world so that it is common to all rooms
