"""
Module that gather class definitions for the room contained in the system and the device simulated in it.
"""

import logging
import numbers
import os
import sys
from typing import List
from datetime import datetime

import world
from devices import Device
from system.system_tools import Location, Window
from tools.check_tools import check_group_address, check_room_config
from .knxbus import KNXBus


class InRoomDevice:
        """Inner class to represent a device located at a certain position in a room"""
        def __init__(self, device, room,  x:float, y:float, z:float): # device can be Device or Window
            self.room = room
            self.device = device
            self.name = device.name
            self.location = Location(self.room, x, y, z)

        def __eq__(self, other_device):
            return (self.device.name == other_device.device.name
                    and self.location.pos == other_device.location.pos 
                    and self.device.individual_addr == other_device.device.individual_addr)

        def update_location(self, new_x=None, new_y=None, new_z=None):  
            # We keep old location if None is given to avoid program failure (None is not supported and considered an error if given to constructor Location)
            new_z = self.location.z if new_z is None else new_z
            new_y = self.location.y if new_y is None else new_y
            new_x = self.location.x if new_x is None else new_x
            new_loc = Location(self.room, new_x, new_y, new_z)
            self.location = new_loc
        
        def get_irdev_info(self, attribute=None):
            if attribute is not None: # script mode, to store the device attribute in a variable
                if 'effective' in attribute:
                    try:
                        return round(getattr(self.device, attribute)(), 2)
                    except AttributeError:
                        logging.error(f"The device {self.name} has no attribute/method '{attribute}'.")
                        return None
                attr = getattr(self.device, attribute)
                if isinstance(attr, numbers.Number):
                    return round(attr, 2)
            ir_device_dict = {"room_name":self.room.name, "device_name":self.device.name, "location":self.location.pos}
            device_dict = self.device.get_dev_info()
            ir_device_dict.update(device_dict) # concatenate 2 dict by uodating existing keys'value
            return ir_device_dict


class Room:
    """Class representing the abstraction of a room, containing devices at certain positions and a physical world representation"""

    """List of devices in the room at certain positions"""
    def __init__(self, name: str, width: float, length: float, height:float, simulation_speed_factor:float, group_address_style:str, system_dt=1, insulation='average', temp_out=20.0, hum_out=50.0, co2_out=300, temp_in=25.0, hum_in=35.0, co2_in=800, date_time="today", weather="clear", test_mode=False, svshi_mode=False, telegram_logging=False, interface=None): # system_dt is delta t in seconds between updates # TODO script mode remove print telegrams
        self.__test_mode = test_mode # flag to avoid using gui package when testing, pyglet not supported by pyglet
        """Check and assign room configuration"""
        self.name, self.width, self.length, self.height, self.__speed_factor, self.__group_address_style, self.__insulation = check_room_config(name, width, length, height, simulation_speed_factor, group_address_style, insulation)
        """Creation of the world object from room config"""
        self.world = world.World(self.width, self.length, self.height, self.__speed_factor, system_dt, self.__insulation, temp_out, hum_out, co2_out, temp_in, hum_in, co2_in, date_time, weather) #date_time is simply a string keyword from config file at this point
        """Representation of the KNX Bus"""
        self.knxbus= KNXBus(svshi_mode)
        """List of all devices in the room"""
        self.devices: List[InRoomDevice] = []
        self.windows: List[InRoomDevice] = []
        """Simulation status to pause/resume"""
        self.simulation_status = True
        self.__paused_tick_counter = 0
        self.__system_dt = system_dt
        if telegram_logging:
            tel_logging_path = "./logs/" + datetime.now().strftime("%d-%m-%Y_%H%M%S")
            os.mkdir(tel_logging_path)
            self.telegram_logging_file_path = tel_logging_path + "/telegram_logs.txt" # path to txt file for telegram logs
        """if SVSHI mode activated, waits for a connection and starts the communication"""
        self.svshi_mode = svshi_mode
        self.telegram_logging = telegram_logging
        if self.svshi_mode:
            if interface is not None: # Simulation reloaded, we keep same interface
                self.__interface = interface
                self.__interface.room = self
            else:
                from svshi_interface.main import Interface
                self.__interface = Interface(self, self.telegram_logging)
            from devices.actuators import IPInterface
            from system import IndividualAddress
            if self.__interface is not None:
                self.interface_device = IPInterface("ipinterface1", "M-O_X000", IndividualAddress(0, 0, 0), "enabled", self.__interface)

    def get_interface(self):
        if self.svshi_mode:
            return self.__interface
        else:
            return None


    def add_device(self, device: Device, x: float, y: float, z: float=1):
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
            if self.svshi_mode:
                in_room_device.device.interface = self.__interface
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
            logging.info(f"FunctionalModule {device.name} establiched connection with the bus")
            device.connect_to(self.knxbus) # The device connect to the Bus to send telegrams on it
        return in_room_device # Return for gui


    def add_window(self, window:Window):
        # we consider windows as devices (actuator for light with outdoor light, potentially actuator for humidity and co2)
        x, y, z = window.window_loc[0],  window.window_loc[1], window.window_loc[2]
        in_room_device = InRoomDevice(window, self, x, y, z)
        self.windows.append(in_room_device)
        self.world.ambient_light.add_source(in_room_device)

    def attach(self, device, group_address:str):
        ga = check_group_address(self.__group_address_style, group_address)
        if ga:
            self.knxbus.attach(device, ga)
            if self.svshi_mode:
                self.knxbus.attach(self.interface_device, ga)
            return 1 
        else: ##TODO utile?
            return 0
    
    def detach(self, device, group_address:str):
        ga = check_group_address(self.__group_address_style, group_address)
        if ga:
            self.knxbus.detach(device, ga)
            return 1
        else: ##TODO utile?
            return 0


    def update_world(self, interval=1, gui_mode=False):
        if self.__test_mode == False:
            import gui
            if self.simulation_status: # True if system is running (not in pause)
                if self.__paused_tick_counter > 0:
                    logging.info(f"Simulation was paused for {self.__paused_tick_counter * self.__system_dt} seconds")
                    self.__paused_tick_counter = 0
                # world.update updates value of all sensors system instances 
                date_time, weather, time_of_day, out_lux, brightness_levels, temperature_levels, rising_temp, humidity_levels, co2_levels, humiditysoil_levels, presence_sensors_states = self.world.update() #call the update function of all ambient modules in world
                if gui_mode:
                    try: # attributes are created in main (proto_simulator)
                        gui.update_gui_window(interval, self.gui_window, date_time, self.world.time.simulation_time(str_mode=True), weather, time_of_day, out_lux, self.svshi_mode)
                    except AttributeError as msg:
                        logging.error(f"Cannot update GUI window due to Room/World attributes missing : '{msg}'")
                    except Exception:
                        logging.error(f"Cannot update GUI window: '{sys.exc_info()[0]}'")
                    try: # update gui devices instances
                        self.gui_window.update_sensors(brightness_levels, temperature_levels, rising_temp, humidity_levels, co2_levels, humiditysoil_levels, presence_sensors_states) 
                    except Exception:
                        logging.error(f"Cannot update sensors value on GUI window: '{sys.exc_info()[0]}'")
                elif gui_mode == False:
                    True
                    # print("not gui mode")
                ## TODO update sensors without using the gui
            else: # Simulation on pause
                self.__paused_tick_counter += 1
                print(f" Simulation paused for {self.__paused_tick_counter * self.__system_dt} seconds"+30*" ", end='\r') 
                
        elif self.__test_mode:
            True
            # print("test mode")
            ## TODO update sensors without using the gui

    def get_dim(self):
        return (self.width, self.length, self.height)

    def get_device_info(self, device_name:str, attribute=None):
        for ir_device in self.devices:
            if device_name == ir_device.name:
                # print(f"ir_device {ir_device.name} found in rooms list")
                ir_dev_dict = ir_device.get_irdev_info(attribute=attribute)
                # print(f"ir_dev_dict: '{ir_dev_dict}'")
                return ir_dev_dict
        logging.warning(f" Device's name '{device_name}' not found in list of room '{self.name}' ")
        return 0

    def get_world_info(self, ambient=None, str_mode=True):
        return self.world.get_info(ambient, self, str_mode=str_mode) # if room (self) not provided, brightness is average of sensors
    
    def get_bus_info(self):
        bus_dict = {"group address encoding style":self.__group_address_style}
        bus_dict.update(self.knxbus.get_info())
        return bus_dict
        #TODO number of group addresses and their devices
    
    def get_room_info(self):
        room_dict = {"name":self.name, "width/length/height": str(self.width) +"x"+ str(self.length) +"x"+ str(self.height), "volume": str(self.width*self.length*self.height) + " m3", "insulation":self.__insulation, "devices":[]}
        for ir_dev in self.devices:
            room_dict['devices'].append(ir_dev.name)
        return room_dict

    def __repr__(self):
        return f"Room {self.name}"
    

