"""
Some class definitions for the simulation of the physical world
"""


from typing import List
import time, math, schedule
import sys
sys.path.append("..") # Adds higher directory to python modules path, for relative includes

from devices import *
from system import InRoomDevice, compute_distance



class Time:
    '''Class that implements time by handling events that should be executed at regular intervals'''

    ##TODO: instead of using scheduler, should notify everyone at a clock tick?

    def __init__(self, simulation_speed_factor:float):
        # Real world simulated time that passed between 2 clock ticks
        self.physical_interval = 3600
        # Amount of time (in seconds) between two software clock ticks
        self.virtual_interval = self.physical_interval/simulation_speed_factor

    def set_simulation_speed_factor(self, speed_factor):
        self.virtual_interval = self.physical_interval/speed_factor

    def set_virtual_interval(self, interval:float):
        # seconds of software simulation corresponding to a simulated 'real-world' hour
        self.virtual_interval = interval


class AmbientTemperature:
    '''Class that implements temperature in a system'''

    def __init__(self, default_temp:float):
        self.temperature = default_temp # Will be obsolete when we introduce gradient of temperature
        self.outside_temperature = default_temp
        self.sources: List[InRoomDevice] = []

    def add_source(self, source: InRoomDevice): # heatsource is an object that heats the room
        self.sources.append(source)

    def update(self):
        '''Apply the update rules, if none then go back to default outside temperature'''
        print("update Temperature")
        if(not self.sources):
            self.temperature = self.outside_temperature
        else:
            for source in self.sources: # sources of heat of cold
                if source.device.is_enabled() and source.device.state:#TODO: Every device should have a state
                    self.temperature += source.device.update_rule

    def __repr__(self):
        return f"{self.temperature} °C"

    def __str__(self):
        return f"{self.temperature} °C"



class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self):
        self.light_sources: List[InRoomDevice] = []
        """List of all devices that emit light"""
        self.light_sensors: List[InRoomDevice] = []
        """List of all devices that measure brightness"""

    def add_source(self, lightsource: InRoomDevice):
        self.light_sources.append(lightsource) #lightsource is an object of type InRoomDevice
    def add_sensor(self, lightsensor: InRoomDevice):
        self.light_sensors.append(lightsensor)

    def read_brightness(self, brightness_sensor: InRoomDevice): #Read brightness at a particular sensor
        brightness = 0 # resulting lumen at the brightness sensor location
        for source in self.light_sources:
            if (source.device.state): # if the light is on
                dist = compute_distance(brightness_sensor, source) # InrRoomDevice types
                residual_lumen = (1/dist)*source.device.lumen # residual lumens from the source at the brightness location
                brightness += residual_lumen # we basically add the lumen
        return brightness

    def update(self): #Updates all brightness sensors of the world (the room)
        print("update brightness")
        for sensor in self.light_sensors:
            brightness = 0
            for source in self.light_sources:
                # If the light is on and enabled on the bus
                if source.device.is_enabled() and source.device.state:
                    # Compute distance between sensor and each source
                    dist = compute_distance(source, sensor) #InRoomDevice Types
                    # Compute the new brightness
                    residual_lumen = (1/dist)*source.device.lumen
                    brightness += residual_lumen
            sensor.device.brightness = brightness # set the newly calculated sensor brightness
            # # Update the sensor's brightness
            # sensor.device.update_brightness(brightness)


class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''
    ## INITIALISATION ##
    def __init__(self):
        self.time = Time(simulation_speed_factor=240) # simulation_speed_factor=240 -> 1h of simulated time = 1min of simulation
        self.ambient_temperature = AmbientTemperature(default_temp=(20.0))
        self.ambient_light = AmbientLight() #TODO: set a default brightness depending on the time of day (day/night), blinds state (open/closed), and wheather state(sunny, cloudy,...)
        self.ambient_world = [self.ambient_temperature, self.ambient_light]

    def update(self):
        for ambient in self.ambient_world:
            ambient.update()

    # def get_time(self):
    #     pass
    ## STATUS FUNCTIONS ##
    # def update_all(self):
    #     self.temperature.update()

    def print_status(self): # one world per room, so status of the room
        print("+---------- STATUS ----------+")
        print(f" Temperature: {self.ambient_temperature.temperature}")
        #TODO: add others when availaible
        print("+----------------------------+")
