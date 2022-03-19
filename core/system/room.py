"""
Some class definitions for the rooms contained in the system
"""
from typing import List

import devices as dev
import simulation as sim

#from devices.device_abstractions import *
#import devices.device_abstractions
#from core.simulation.world import *
from abc import ABC, abstractclassmethod

class Room:
    #devices: List[Device] = []
    devices = []

    def __init__(self, name, width, length):
        self.name = name
        self.width = width #x
        self.length = length #y
        self.world = sim.World()
        self.observer = sim.Observer() # Manage KNX Bus communications

    def add_device(self, device, x, y): #device is an object
        if(x < 0 or x > self.width or y < 0 or y > self.length):
            print("Cannot add a device outside the room!")
        else:
            device.set_physical_location(x, y)
            if device.dev_type == "actuator":
                if device.actuator_type == "light":
                    self.world.ambient_light.add_lightsource(device) # add device to the light sources list, to be able to calculate brightness from any point of the room
                    self.observer.attach(device) #We add all lights to the observer list, TODO: manage with group addresses, for now, index of light corresponds to index of button
                    print("light added")
                elif device.actuator_type == "heater":
                    self.world.ambient_temperature.add_heatingsource(device)
                    print("heater added")
                elif device.actuator_type == "cooler":
                    self.world.ambient_temperature.add_coolingsource(device)
                    print("cooler added")

            elif device.dev_type == "sensor":
                if device.sensor_type == "brightness":
                    print("brightness sensor added")
                elif device.sensor_type == "temperature":
                    print("temperature sensor added")

            elif device.dev_type == "functional_module":
                if device.input_type == "button":
                    print("button added")
                elif device.input_type == "dimmer":
                    print("dimmer added")
                self.observer.add_functional_module(device)
                device.attach(self.observer) # We attach the functional device to the observer class

            self.devices.append(device)



    def update_world(self):
        self.world.update() #call the update function of all ambient modules in world

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
