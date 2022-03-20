"""
Some class definitions for the rooms contained in the system
"""
from typing import List
from devices import *
from simulation import *
from abc import ABC, abstractclassmethod

class InRoomDevice:
        """Inner class to represent a device located at a certain position in a room"""
        def __init__(self, device: Device, x:float, y:float):
            self.device = device
            self.position = (x,y)
            self.name = device.name
            self.type = type(device)
        
        def get_device(self) -> Device:
            return self.device

        def get_position(self):
            return self.position

        def get_x_position(self) -> float:
            return self.position[0]

        def get_y_position(self) -> float:
            return self.position[1]

class Room:
    """Class representing the abstraction of a room, containing devices at certain positions and a physical world representation"""
   

    devices: List[InRoomDevice] = []
    """List of devices in the room at certain positions"""

    def __init__(self, name: str, width: int, length: int):
        self.name = name
        """The room's given name"""
        self.width = width
        """Along x axis"""
        self.length = length
        """Along y axis"""
        self.world = World()
        """Representation of the world"""

    def add_device(self, device: Device, x: float, y: float):
        """Adds a device to the room at the given position"""
        if(x < 0 or x > self.width or y < 0 or y > self.length):
            print("Cannot add a device outside the room!")
            return
        
        in_room_device = InRoomDevice(device, x, y)
        self.devices.append(in_room_device)

        if isinstance(device, Actuator):
            if isinstance(device, LightDevice):
                self.world.ambient_light.add_lightsource(in_room_device)
                print(f"A light source was added at {x} : {y}.")
            elif isinstance(device, TemperatureDevice):
                self.world.ambient_temperature.add_heatingsource(in_room_device)
                print(f"A device acting on temperature was added at {x} : {y}.")
        elif isinstance(device, Sensor):
            if isinstance(device, Button):
                print(f"A button was added at {x} : {y}.")
            elif isinstance(device, Brightness):
                print(f"A brightness sensor was added at {x} : {y}.")
        

    def __str__(self):
        str_repr =  f"# {self.name} is a room of dimensions {self.width} x {self.length} m2 with devices:\n"
        for room_device in self.devices:
            str_repr += f"-> {room_device.name} at location ({room_device.get_x_position()}, {room_device.get_y_position()})"
            if room_device.type == Actuator:
                str_repr += "ON" if Actuator(room_device.device).state else "OFF"
                str_repr += f" is {Actuator(room_device.device).state}"
            str_repr += "\n"
        return str_repr

    def __repr__(self):
        return f"Room {self.name}"


class System:
    pass #TODO: further in time, should be the class used for instantiation, should contain list of rooms + a world so that it is common to all rooms
