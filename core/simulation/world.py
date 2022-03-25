"""
Some class definitions for the simulation of the physical world
"""


from typing import List
import time, math, schedule
import sys
sys.path.append("..") # Adds higher directory to python modules path, for relative includes
sys.path.append("core")

from devices import *


class Time:
    '''Class that implements time by handling events that should be executed at regular intervals'''

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
        self.source = []

    def add_source(self, source): # heatsource is an object that heats the room
        self.sources.append(source)

    def update(self):
        '''Apply the update rules, if none then go back to default outside temperature'''
        print("update Temperature")
        if(not self.sources):
            self.temperature = self.outside_temperature
        else:
            for source in self.sources: # sources of heat of cold
                if source.device.is_enabled():
                    self.temperature += source.device.update_rule

    def __repr__(self):
        return f"{self.temperature} °C"

    def __str__(self):
        return f"{self.temperature} °C"

    def required_power_of_heater_for_room(m3=1, desired_temperature=20, insulation_state="good"):
        temp_to_watts = [(24, 93), (22, 85), (20, 77), (18, 70)]
        """Recommended temperature associated to required number of watts per m3"""

        insulation_to_correction_factor = {"good": -10/100, "bad": 15/100}
        """Situation of the insulation of the room associated to the correction factor for the heating"""
        watt = [watt[1] for watt in temp_to_watts if watt[0] == desired_temperature][0]

        desired_wattage = m3*watt
        desired_wattage += desired_wattage*insulation_to_correction_factor[insulation_state]

        return desired_wattage

print(AmbientTemperature.required_power_of_heater_for_room(20, 18, "good"))

class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self):
        self.light_sources: List = []
        """List of all devices that emit light"""
        self.light_sensors: List = []
        """List of all devices that measure brightness"""

    def add_source(self, lightsource, lightsensor):
        self.light_sources.append(lightsource) #lightsource is an object of type    def add_sensor(self, lightsensor::
        self.light_sensors.append(lightsensor)

    def compute_distance(source, sensor) -> float:
        """ Computes euclidian distance between a sensor and a actuator"""
        delta_x = abs(source.location.x - sensor.location.x)
        delta_y = abs(source.location.y - sensor.location.y)
        dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor
        return dist


    def read_brightness(self, brightness_sensor): #Read brightness at a particular sensor
        brightness = 0 # resulting lumen at the brightness sensor location
        for source in self.light_sources:
            if (source.device.state): # if the light is on
                dist = self.compute_distance(brightness_sensor, source) # InrRoomDevice types
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
                    dist = self.compute_distance(source, sensor)
                    # Compute the new brightness
                    residual_lumen = (1/dist)*source.device.lumen
                    brightness += residual_lumen
            # Update the sensor's brightness
            sensor.device.brightness = brightness # set the newly calculated sensor brightness


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
