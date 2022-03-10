"""
Some class definitions for the rooms contained in the system
"""
from typing import List

from core.devices.device_abstractions import *
from core.simulation.world import *
from abc import ABC, abstractclassmethod

class Room:

    devices: List[Device] = []
    world = World()

    def __init__(self, name, width, length):
        self.name = name
        self.width = width
        self.length = length

    def __str__(self):
        return f"{self.name} is a room of dimensions {self.width} x {self.length} m2"
    
    def __repr__(self):
        return f"Room {self.name}"

class System:
    pass #TODO: further in time, should be the class used for instantiation, should contain list of rooms + a world so that it is common to all rooms
    