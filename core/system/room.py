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

    def __str__(self):
        return f"{self.name} is a room of dimensions {self.width} x {self.length} m2"

    def __repr__(self):
        return f"Room {self.name}"

    def add_device(self, device, x, y): #device is an object
        if(x < 0 or x > self.width or y < 0 or y > self.length):
            print("Cannot add a device that's outside the room!")
        else:
            device.set_physical_location(x, y)
            if device.type == "actuator":
                if device.actuator_type == "light":
                    self.world.ambiant_light.add_lightsource(device) # add device to the light sources list, to be able to calculate brightness from any point of the room
            self.devices.append(device)



class System:
    pass #TODO: further in time, should be the class used for instantiation, should contain list of rooms + a world so that it is common to all rooms
