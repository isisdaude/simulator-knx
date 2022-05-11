"""
Some class definitions for the simulation of the physical world
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]

from typing import List
import time, math, schedule
import sys, logging
from numpy import mean

#from soupsieve import escape
# sys.path.append("..") # Adds higher directory to python modules path, for relative includes
# sys.path.append("core")
#
# from devices import *
import system

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Time:
    '''Class that implements time by handling events that should be executed at regular intervals'''

    def __init__(self, simulation_speed_factor:float):
        # Real world simulated time that passed between 2 clock ticks
        self.physical_interval = 3600
        self.speed_factor = simulation_speed_factor
        # Amount of time (in seconds) between two software clock ticks
        self.virtual_interval = self.physical_interval/self.speed_factor

    def set_simulation_speed_factor(self, speed_factor):
        self.virtual_interval = self.physical_interval/speed_factor

    def set_virtual_interval(self, interval:float):
        # seconds of software simulation corresponding to a simulated 'real-world' hour
        self.virtual_interval = interval

    # Scheduler management, if not in GUI mode
    def scheduler_init(self):
        self.scheduler = AsyncIOScheduler()
        return self.scheduler

    def scheduler_add_job(self, job_function):
        try:
            self.update_job = self.scheduler.add_job(job_function, 'interval', seconds = self.virtual_interval)
        except AttributeError:
            logging.warning("The Scheduler is not initialized: job cannnot be added")

    def scheduler_start(self):
        try:
            self.scheduler.start()
            self.start_time = time.time()
        except AttributeError:
            logging.warning("The Scheduler is not initialized and cannot be started")

    # Simulation time management
    def simulation_time(self):
        try:
            elapsed_time = time.time() - self.start_time
            return elapsed_time
        except AttributeError:
            logging.warning("The Simulation time is not initialized")

class AmbientTemperature:
    '''Class that implements temperature in a system'''

    def __init__(self, room_volume, default_temp:float):
        self.temperature = default_temp # Will be obsolete when we introduce gradient of temperature
        self.outside_temperature = default_temp
        self.room_volume = room_volume
        """Describes room volume in m3"""
        self.temp_sources = []
        """List of temperature actuators sources in the room"""
        self.temp_sensors = []
        """List of temperature sensors in the room"""
        self.temp_controllers = []

    def add_source(self, source): # Heatsource is an object that heats the room
        self.temp_sources.append(source) #add check on source

    def add_sensor(self, tempsensor):
        self.temp_sensors.append(tempsensor) #add check on sensor

    def add_temp_controllers(self, temp_controllers):
        self.temp_controllers.append(temp_controllers) #add check on sensor

    def update(self):
        from devices import Heater
        '''Apply the update rules taking into consideration the maximum power of each heating device, if none then go back progressively to default outside temperature'''
        logging.info("Temperature update")
        if(not self.temp_sources):
            self.temperature = (self.temperature + self.outside_temperature)//2 # Decreases by the average of temp and outside_temp, is a softer slope
        else:
            max_temps = []
            for source in self.temp_sources: # sources of heat or cold
                if source.device.status:
                    if isinstance(source.device, Heater):
                        max_temps.append(source.device.max_temperature_in_room(self.room_volume,"average"))
                    self.temperature += source.device.update_rule
            max_temp = mean(max_temps)
            if self.temperature >= max_temp:
                self.temperature = (self.temperature + max_temp) // 2 # Decreases by the average of temp and outside_temp, is a softer slope
        temperature_levels = []
        for sensor in self.temp_sensors:
            sensor.temperature = self.temperature
            temperature_levels.append((sensor.name, sensor.temperature))
        for controller in self.temp_controllers:#
            controller.temperature = self.temperature ##TODO: notify the bus with a telegram to heat sources
        return temperature_levels

    def __repr__(self):
        return f"{self.temperature} °C"

    def __str__(self):
        return f"{self.temperature} °C"

class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self):
        self.light_sources: List = []
        """List of all devices that emit light"""
        self.light_sensors: List = []
        """List of all devices that measure brightness"""

    def add_source(self, lightsource):
        self.light_sources.append(lightsource) #lightsource is an object of type

    def add_sensor(self, lightsensor):
        self.light_sensors.append(lightsensor)

    def read_brightness(self, brightness_sensor): #Read brightness at a particular sensor
        brightness = 0
        for source in self.light_sources:
            # If the light is on and enabled on the bus
            if source.device.is_enabled() and source.device.state:
                # Compute distance between sensor and each source
                dist = system.compute_distance(source, brightness_sensor)
                # Compute the new brightness
                residual_lumen = (1/dist)*source.device.lumen*(source.device.state_ratio/100) # we suppose proportionality between state ratio and lumen 
                brightness += residual_lumen
        return brightness

    def update(self): #Updates all brightness sensors of the world (the room)
        logging.info("Brightness update")
        brightness_levels = []
        for sensor in self.light_sensors:
            # Update the sensor's brightness
            sensor.device.brightness = self.read_brightness(sensor) # set the newly calculated sensor brightness
            brightness_levels.append((sensor.device.name, sensor.device.brightness))

        return brightness_levels

class AmbientHumidity:
    # elements that influence humidity:
    # - windows
    # - heater/cooler
    def __init__(self):
        self.default_humidity = 50 # Relative Humidity in %

class AmbientCO2:
    # elements that influence humidity:
    # - windows
    def __init__(self):
        self.default_CO2 = 600 # ppm



class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''
    ## INITIALISATION ##
    def __init__(self, room_width, room_length, room_height, simulation_speed_factor):
        self.time = Time(simulation_speed_factor) # simulation_speed_factor=240 -> 1h of simulated time = 1min of simulation
        self.ambient_temperature = AmbientTemperature(room_width*room_height*room_length, default_temp=(20.0))
        self.ambient_light = AmbientLight() #TODO: set a default brightness depending on the time of day (day/night), blinds state (open/closed), and wheather state(sunny, cloudy,...)
        self.ambient_humidity = AmbientHumidity()
        self.ambient_CO2 = AmbientCO2()
        self.ambient_world = [self.ambient_temperature, self.ambient_light]

    def update(self):
        brightness_levels = self.ambient_light.update()
        temperature_levels = self.ambient_temperature.update()
        return brightness_levels, temperature_levels

    def get_world_state(self): # one world per room, so status of the room
        print("+---------- STATUS ----------+")
        print(f" Temperature: {self.ambient_temperature.temperature}")
        #TODO: add others when availaible
        print("+----------------------------+")
