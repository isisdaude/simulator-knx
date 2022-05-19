"""
Some class definitions for the rooms contained in the system
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import logging, sys
import numbers
from typing import List

import gui
import simulation as sim
from devices import Device

from .tools import Location
from .check_tools import check_group_address, check_room_config #, check_simulation_speed_factor
from .knxbus import KNXBus
from abc import ABC, abstractclassmethod

class InRoomDevice:
        """Inner class to represent a device located at a certain position in a room"""
        def __init__(self, device: Device, room,  x:float, y:float, z:float):
            self.room = room
            self.device = device
            self.name = device.name
            self.location = Location(self.room, x, y, z)
            # if self.location.pos is None:
            #     logging.error(f"The device '{self.name}' location is out of room's bounds -> program terminated.")
            #     sys.exit(1)
            # self.type = type(device)  ## whait is this ?

        def __eq__(self, other_device):
            return self.name == other_device.name

        def update_location(self, new_x=None, new_y=None, new_z=None):  
            # We keep old location if None is given to avoid program failure (None is not supported and considered an error if given to constructor Location)
            new_z = self.location.z if new_z is None else new_z
            new_y = self.location.y if new_y is None else new_y
            new_x = self.location.x if new_x is None else new_x
            new_loc = Location(self.room, new_x, new_y, new_z)
            # if new_loc.pos is None:
            #     logging.error(f"The device '{self.name}' location is out of room's bounds -> program terminated.")
            #     sys.exit(1)
            self.location = new_loc

        def get_position(self):
            return self.location.pos

        def get_x(self) -> float:
            return self.location.x

        def get_y(self) -> float:
            return self.location.y

        def get_z(self) -> float:
            return self.location.z




class Room:
    """Class representing the abstraction of a room, containing devices at certain positions and a physical world representation"""

    """List of devices in the room at certain positions"""
    def __init__(self, name: str, width: float, length: float, height:float, simulation_speed_factor:float, group_address_style:str, system_dt=1, insulation='average', out_temp=20.0, out_hum=50.0, out_co2=300): # system_dt is delta t in seconds between updates
        """Check and assign room configuration"""
        self.name, self.width, self.length, self.height, self.speed_factor, self.group_address_style, self.insulation = check_room_config(name, width, length, height, simulation_speed_factor, group_address_style, insulation)
        """Creation of the world object from room config"""
        self.world = sim.World(self.width, self.length, self.height, self.speed_factor, system_dt, self.insulation, out_temp, out_hum, out_co2)
        """Representation of the KNX Bus"""
        self.knxbus= KNXBus()
        """List of all devices in the room"""
        self.devices: List[InRoomDevice] = []
        """Simulation status to pause/resume"""
        self.simulation_status = True
        


    def add_device(self, device: Device, x: float, y: float, z:float):
        from devices import Actuator, LightActuator, TemperatureActuator, Sensor, Brightness, FunctionalModule, Button, TemperatureController, Thermometer, AirSensor
        """Adds a device to the room at the given position"""
        # if(x < 0 or x > self.width or y < 0 or y > self.length):
        #     logging.warning("Cannot add a device outside the room")
        #     return

        in_room_device = InRoomDevice(device, self, x, y, z) #self is for the room, important if we want to find the room of a certain device
        self.devices.append(in_room_device)

        if isinstance(device, Actuator):
            if isinstance(device, LightActuator):
                #self.knxbus.attach(device) # Actuator subscribes to KNX Bus
                self.world.ambient_light.add_source(in_room_device)
                #print(f"A light source was added at {x} : {y}.")
            elif isinstance(device, TemperatureActuator):
                self.world.ambient_temperature.add_source(in_room_device)
                #print(f"A device acting on temperature was added at {x} : {y}.")
        elif isinstance(device, Sensor):
            if isinstance(device, Brightness):
                self.world.ambient_light.add_sensor(in_room_device)
                #print(f"A brightness sensor was added at {x} : {y}.")
            elif isinstance(device, Thermometer):
                self.world.ambient_temperature.add_sensor(in_room_device)
            elif isinstance(device, AirSensor):
                self.world.ambient_temperature.add_sensor(in_room_device)
                self.world.ambient_humidity.add_sensor(in_room_device)
                self.world.ambient_co2.add_sensor(in_room_device)
        elif isinstance(device, FunctionalModule):
            if isinstance(device, Button):
                device.connect_to(self.knxbus) # The device connect to the Bus to send telegrams
            elif isinstance(device, TemperatureController):
                device.room_volume = self.width*self.length*self.height
                device.room_insulation = self.insulation
                device.connect_to(self.knxbus) # The device connect to the Bus to send telegrams
                self.world.ambient_temperature.add_sensor(in_room_device)
                #print(f"A button was added at {x} : {y}.")
        return in_room_device # return for gui

    ### TODO: implement removal of devices
    # def remove_device(self, in_room_device):
    #     for device in self.devices:
    #         if device == in_room_device:
    #             if isinstance(device, FunctionalModule):
    #                 device.disconnect_from_knxbus()

    def attach(self, device, group_address:str):
        ga = check_group_address(self.group_address_style, group_address)
        if ga:
            self.knxbus.attach(device, ga)
            return 1
        else:
            return 0
    
    def detach(self, device, group_address:str):
        ga = check_group_address(self.group_address_style, group_address)
        if ga in self.knxbus.group_addresses:
            self.knxbus.detach(device, ga)
            return 1
        else:
            return 0
                # remove from List
                # detach from bus
                # remove from world

    def update_world(self, interval=1, gui_mode=False):
        if self.simulation_status:
            brightness_levels, temperature_levels, humidity_levels, co2_levels = self.world.update() #call the update function of all ambient modules in world
            #brightness_levels = brightness_sensor_name, brightness
            if gui_mode:
                try: # attributes are created in main (proto_simulator)
                    gui.update_window(interval, self.window, self.world.time.speed_factor, self.world.time.start_time)
                except AttributeError:
                    logging.error("Cannot update GUI window due to Room/World attributes missing (not defined)")
                except Exception:
                    logging.error(f"Cannot update GUI window: '{sys.exc_info()[0]}'")
                try:
                    self.window.update_sensors(brightness_levels, temperature_levels, humidity_levels, co2_levels) 
                except Exception:
                    logging.error(f"Cannot update sensors value on GUI window: '{sys.exc_info()[0]}'")




    # def __str__(self): # TODO: write str representation of room
        # str_repr =  f"# {self.name} is a room of dimensions {self.width} x {self.length} m2 and {self.height}m of height with devices:\n"
        # for room_device in self.devices:
        #     str_repr += f"-> {room_device.name} at location ({room_device.get_x()}, {room_device.get_y()})"
        #     if room_device.type == Actuator:
        #         str_repr += "ON" if room_device.device.state else "OFF"
        #         str_repr += f" is {room_device.device.state}"
        #     str_repr += "\n"
        # return str_repr

    def __repr__(self):
        return f"Room {self.name}"


# class System:
#     pass #TODO: further in time, should be the class used for instantiation, should contain list of rooms + a world so that it is common to all rooms
