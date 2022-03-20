"""
Some class definitions for the simulation of the physical world
"""

from typing import List
import time, math, schedule
from core.system.room import InRoomDevice


class Time:
    '''Class that implements time by handling events that should be executed at regular intervals'''

    ##TODO: instead of using scheduler, should notify everyone at a clock tick?

    def __init__(self, simulation_speed_factor):
        # Real world simulated time that passed between 2 clock ticks
        self.physical_interval = 3600
        # Amount of time (in seconds) between two software clock ticks
        self.virtual_interval = self.physical_interval/simulation_speed_factor

    def set_simulation_speed_factor(self, speed_factor):
        self.virtual_interval = self.physical_interval/speed_factor

    def set_virtual_interval(self, interval:int):
        # seconds of software simulation corresponding to a simulated 'real-world' hour
        self.virtual_interval = interval

    # def add_task(self, task):
    #     '''Adds a task to the scheduler which executes every virtual time interval to represent some physical time interval'''
    #     schedule.every(Time.VIRTUAL_INTERVAL)
    # def remove_task(self):
    #     '''Removes a task from the scheduler'''
    #     pass
    # def bigbang(self):
    #     '''Starts time and the execution of tasks every certain intervals'''
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(1)

class AmbientTemperature:
    '''Class that implements temperature in a system'''

    def __init__(self, default_temp:float):
        self.temperature = default_temp
        self.outside_temperature = default_temp
        self.sources: List[InRoomDevice] = []

    def add_source(self, source): # heatsource is an object that heats the room
        self.sources.append(source)

    def get_temperature(self):
        return self.temperature

    def update(self): 
        '''Apply the update rules, if none then go back to default outside temperature'''
        if(not self.sources):
            self.temperature = self.outside_temperature
        else:
            for s in self.sources:
                s.

    def __repr__(self):
        return f"{self.temperature}"

    def __str__(self):
        return f"{self.temperature}"




class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self): # light_sources is a list of all devices that emit light
        self.light_sources = []

    def add_lightsource(self, lightsource):
        self.light_sources.append(lightsource) #lightsource is an object of type light

    def get_brightness(self, brightness_sensor):
        sensor_loc_x = brightness_sensor.loc_x
        sensor_loc_y = brightness_sensor.loc_y
        brightness = 0 # resulting lumen at the brightness sensor location
        for source in self.light_sources:
            if (source.state): # if the light is on
                source_loc_x = source.loc_x  ## TODO: replace all this by a function compute_distance
                source_loc_y = source.loc_y
                delta_x = abs(source_loc_x-sensor_loc_x)
                delta_y = abs(source_loc_y-sensor_loc_y)
                dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor

                residual_lumen = (1/dist)*source.lumen # residual lumens from the source at the brightness location
                brightness += residual_lumen # we basically add the lumen
        return brightness


class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''

    ## INITIALISATION ##
    def __init__(self):
        self.time = Time(simulation_speed_factor=240) # simulation_speed_factor=240 -> 1h of simulated time = 1min of simulation
        self.ambient_temperature = AmbientTemperature(default_temp=(20.0))
        self.ambient_light = AmbientLight()

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
