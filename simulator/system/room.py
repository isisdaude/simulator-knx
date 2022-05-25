"""
Some class definitions for the rooms contained in the system
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import logging, sys
import numbers
from typing import List

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

        def __eq__(self, other_device):
            return (self.device.name == other_device.device.name and
                    self.location.pos == other_device.location.pos and
                    self.device.individual_addr == other_device.device.individual_addr and 
                    self.device.refid == other_device.device.refid)

        def update_location(self, new_x=None, new_y=None, new_z=None):  
            # We keep old location if None is given to avoid program failure (None is not supported and considered an error if given to constructor Location)
            new_z = self.location.z if new_z is None else new_z
            new_y = self.location.y if new_y is None else new_y
            new_x = self.location.x if new_x is None else new_x
            new_loc = Location(self.room, new_x, new_y, new_z)
            self.location = new_loc

        def get_position(self):
            return self.location.pos

        # def get_x(self) -> float:
        #     return self.location.x

        # def get_y(self) -> float:
        #     return self.location.y

        # def get_z(self) -> float:
        #     return self.location.z
        
        def get_irdev_info(self):
            ir_device_dict = {"room_name":self.room.name, "device_name":self.device.name, "location":self.location.pos}
            # print(f"ir_device_dict: '{ir_device_dict}'")
            device_dict = self.device.get_dev_info()
            # print(f"device_dict: '{device_dict}'")
            ir_device_dict.update(device_dict) # concatenate 2 dict by uodating existing keys'value
            # print(f"ir_device_dict(update): '{ir_device_dict}'")
            return ir_device_dict
            



class Room:
    """Class representing the abstraction of a room, containing devices at certain positions and a physical world representation"""

    """List of devices in the room at certain positions"""
    def __init__(self, name: str, width: float, length: float, height:float, simulation_speed_factor:float, group_address_style:str, system_dt=1, insulation='average', temp_out=20.0, hum_out=50.0, co2_out=300, test_mode=False): # system_dt is delta t in seconds between updates
        self.test_mode = test_mode # flag to avoid using gui package when testing, pyglet not supported by pyglet
        """Check and assign room configuration"""
        self.name, self.width, self.length, self.height, self.speed_factor, self.group_address_style, self.insulation = check_room_config(name, width, length, height, simulation_speed_factor, group_address_style, insulation)
        """Creation of the world object from room config"""
        self.world = sim.World(self.width, self.length, self.height, self.speed_factor, system_dt, self.insulation, temp_out, hum_out, co2_out)
        """Representation of the KNX Bus"""
        self.knxbus= KNXBus()
        """List of all devices in the room"""
        self.devices: List[InRoomDevice] = []
        """Simulation status to pause/resume"""
        self.simulation_status = True
        


    def add_device(self, device: Device, x: float, y: float, z:float):
        from devices import FunctionalModule, Button, Dimmer, Actuator, LightActuator, TemperatureActuator, Sensor, Brightness, Thermometer, AirSensor, HumiditySoil, HumidityAir, CO2Sensor, PresenceSensor
        """Adds a device to the room at the given position"""

        in_room_device = InRoomDevice(device, self, x, y, z) #self is for the room, important if we want to find the room of a certain device
        self.devices.append(in_room_device)

        if isinstance(device, Actuator):
            if isinstance(device, LightActuator):
                self.world.ambient_light.add_source(in_room_device)
            elif isinstance(device, TemperatureActuator):
                self.world.ambient_temperature.add_source(in_room_device)
        elif isinstance(device, Sensor):
            if isinstance(device, Brightness):
                self.world.ambient_light.add_sensor(in_room_device)
            elif isinstance(device, Thermometer):
                self.world.ambient_temperature.add_sensor(in_room_device)
            elif isinstance(device, HumiditySoil): 
                self.world.soil_moisture.add_sensor(in_room_device)
            elif isinstance(device, HumidityAir): 
                self.world.ambient_humidity.add_sensor(in_room_device) 
            elif isinstance(device, CO2Sensor):
                self.world.ambient_co2.add_sensor(in_room_device)
            elif isinstance(device, AirSensor):
                self.world.ambient_temperature.add_sensor(in_room_device)
                self.world.ambient_humidity.add_sensor(in_room_device)
                self.world.ambient_co2.add_sensor(in_room_device)
            elif isinstance(device, PresenceSensor):
                self.world.presence.add_sensor(in_room_device)

        elif isinstance(device, FunctionalModule):
            device.connect_to(self.knxbus) # The device connect to the Bus to send telegrams
            # if isinstance(device, Button):
            #     device.connect_to(self.knxbus) # The device connect to the Bus to send telegrams
            # elif isinstance(device, Dimmer):
            #     device.connect_to(self.knxbus)
        return in_room_device # Return for gui

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
        if self.test_mode == False:
            import gui
            if self.simulation_status:
                # world.update updates value of all sensors system instances 
                brightness_levels, temperature_levels, humidity_levels, co2_levels, humiditysoil_levels, presence_sensors_states = self.world.update() #call the update function of all ambient modules in world
                #brightness_levels = brightness_sensor_name, brightness
                if gui_mode:
                    try: # attributes are created in main (proto_simulator)
                        gui.update_window(interval, self.window, self.world.time.simulation_time(str_mode=True))
                    except AttributeError:
                        logging.error("Cannot update GUI window due to Room/World attributes missing (not defined)")
                    except Exception:
                        logging.error(f"Cannot update GUI window: '{sys.exc_info()[0]}'")
                    try: # update gui devices instances
                        self.window.update_sensors(brightness_levels, temperature_levels, humidity_levels, co2_levels, humiditysoil_levels, presence_sensors_states) 
                    except Exception:
                        logging.error(f"Cannot update sensors value on GUI window: '{sys.exc_info()[0]}'")
                elif gui_mode == False:
                    True
                    # print("not gui mode")
                ## TODO update sensors without using the gui
        elif self.test_mode:
            True
            # print("test mode")
            ## TODO update sensors without using the gui

    def get_dim(self):
        return (self.width, self.length, self.height)

    def get_device_info(self, device_name:str):
        for ir_device in self.devices:
            if device_name == ir_device.name:
                # print(f"ir_device {ir_device.name} found in rooms list")
                ir_dev_dict = ir_device.get_irdev_info()
                # print(f"ir_dev_dict: '{ir_dev_dict}'")
                return ir_dev_dict
        logging.warning(f" Device's name '{device_name}' not found in list of room '{self.name}' ")
        return 0

    def get_world_info(self, ambient=None, str_mode=True):
        return self.world.get_info(ambient, self, str_mode=str_mode) # if room (self) not provided, brightness is average of sensors
    
    def get_bus_info(self):
        bus_dict = {"group address encoding style":self.group_address_style}
        bus_dict.update(self.knxbus.get_info())
        return bus_dict
        #TODO number of group addresses and their devices
    
    def get_room_info(self):
        room_dict = {"name":self.name, "width": self.width, "length":self.length, "height":self.height, "volume": self.width*self.length*self.height, "insulation":self.insulation, "devices":[]}
        for ir_dev in self.devices:
            room_dict['devices'].append(ir_dev.name)
        return room_dict

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
