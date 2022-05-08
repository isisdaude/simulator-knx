"""
Some class definitions for the rooms contained in the system
"""

import logging, sys
from typing import List
import gui
import simulation as sim
from devices import Device

from .tools import Location, check_group_address, check_simulation_speed_factor
from .knxbus import KNXBus
from abc import ABC, abstractclassmethod

class InRoomDevice:
        """Inner class to represent a device located at a certain position in a room"""
        def __init__(self, device: Device, room,  x:float, y:float, z:float):
            self.device = device
            self.name = device.name
            self.location = Location(room, x, y, z)
            self.type = type(device)  ## whait is this ?

        def __eq__(self, other_device):
            return self.name == other_device.name

        def get_position(self):
            return self.location.pos

        def get_x(self) -> float:
            return self.location.pos[0]

        def get_y(self) -> float:
            return self.location.pos[1]

        def get_z(self) -> float:
            return self.location.pos[2]


class Room:
    """Class representing the abstraction of a room, containing devices at certain positions and a physical world representation"""

    """List of devices in the room at certain positions"""
    def __init__(self, name: str, width: int, length: int, height:int, simulation_speed_factor:float, group_address_style:str):
        """The room's given name"""
        try:
            assert len(name) > 0
            assert name.isalnum() # check alphanumericness
        except AssertionError:
            logging.error("A non-empty alphanumeric name is required to create the room, check your config before launching the simulator")
            sys.exit(1)
        self.name = name
        """Along x axis"""
        self.width = width
        """Along y axis"""
        self.length = length
        """Along z axis"""
        self.height = height
        """Representation of the world"""
        try:
            assert simulation_speed_factor == check_simulation_speed_factor(simulation_speed_factor)
        except AssertionError:
            logging.error(f"The simulation speed factor {simulation_speed_factor} is incorrect, check your config before launching the simulator")
            sys.exit()
        self.world = sim.World(self.width, self.length, self.height, simulation_speed_factor)
        """Representation of the KNX Bus"""
        self.knxbus= KNXBus()
        """List of all devices in the room"""
        self.devices: List[InRoomDevice] = []
        """Simulation status to pause/resume"""
        self.simulation_status = True
        """Group addresses style by default"""
        self.group_address_style = group_address_style 


    def add_device(self, device: Device, x: float, y: float, z:float):
        from devices import Actuator, LightActuator, TemperatureActuator, Sensor, Brightness, FunctionalModule, Switch, TemperatureController
        """Adds a device to the room at the given position"""
        if(x < 0 or x > self.width or y < 0 or y > self.length):
            logging.warning("Cannot add a device outside the room")
            return

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
        elif isinstance(device, FunctionalModule):
            if isinstance(device, Switch):
                device.connect_to(self.knxbus) # The device connect to the Bus to send telegrams
            if isinstance(device, TemperatureController):
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
            brightness_levels, temperature_levels = self.world.update() #call the update function of all ambient modules in world
            #brightness_levels = brightness_sensor_name, brightness
            if gui_mode:
                try: # attributes are created in main (proto_simulator)
                    gui.update_window(interval, self.window, self.world.time.speed_factor, self.world.time.start_time)
                except AttributeError:
                    logging.error("Cannot update GUI window due to Room/World attributes missing (not defined)")
                except Exception as msg:
                    logging.error(f"Cannot update GUI window: '{msg}'")
                try:
                    self.window.update_sensors(brightness_levels, temperature_levels) #only brightness for now #TODO implement for temperatures
                except Exception as msg:
                    logging.error(f"Cannot update sensors value on GUI window: '{msg}'")




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
