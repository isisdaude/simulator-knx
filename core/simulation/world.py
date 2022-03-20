"""
Some class definitions for the simulation of the physical world
"""

from typing import List
import time, math, schedule
from core.devices.sensors import Brightness
from core.system.room import InRoomDevice
from core.devices.actuators import Actuator, TemperatureDevice, LightDevice

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

    def add_source(self, source: InRoomDevice): # heatsource is an object that heats the room
        self.sources.append(source)

    def get_temperature(self):
        return self.temperature

    def update(self): 
        '''Apply the update rules, if none then go back to default outside temperature'''
        if(not self.sources):
            self.temperature = self.outside_temperature
        else:
            for s in self.sources:
                if s.get_device().is_connected() and Actuator(s.get_device()).state:#TODO: Every device should have a state
                    self.temperature += TemperatureDevice(s.get_device()).get_update_rule()

    def __repr__(self):
        return f"{self.temperature}"

    def __str__(self):
        return f"{self.temperature}"


def compute_distance(source: InRoomDevice, sensor: InRoomDevice) -> float:
    delta_x = abs(source.get_x_position() - sensor.get_x_position())
    delta_y = abs(source.get_y_position() - sensor.get_y_position())
    dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor
    return dist

class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self):
        self.light_sources: List[InRoomDevice] = []
        """List of all devices that emit light"""

    def add_lightsource(self, lightsource: InRoomDevice):
        self.light_sources.append(lightsource) #lightsource is an object of type light

    # def get_brightness(self, brightness_sensor):
    #     sensor_loc_x = brightness_sensor.loc_x
    #     sensor_loc_y = brightness_sensor.loc_y
    #     brightness = 0 # resulting lumen at the brightness sensor location
    #     for source in self.light_sources:
    #         if (source.state): # if the light is on
    #             source_loc_x = source.loc_x 
    #             source_loc_y = source.loc_y
    #             delta_x = abs(source_loc_x-sensor_loc_x)
    #             delta_y = abs(source_loc_y-sensor_loc_y)
    #             dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor

    #             residual_lumen = (1/dist)*source.lumen # residual lumens from the source at the brightness location
    #             brightness += residual_lumen # we basically add the lumen
    #     return brightness

    def update_sensor(self, sensor: InRoomDevice):
        brightness = 0
        for source in self.light_sources:
            s = LightDevice(source.get_device())

            # If the light is on and connected to the bus
            if s.is_connected() and s.state():
                # Compute distance between sensor and each source
                dist = compute_distance(source, sensor)
                # Compute the new brightness
                residual_lumen = (1/dist)*s.lumen
                brightness += residual_lumen
        # Update the sensor's brightness
        Brightness(sensor.get_device()).update_brightness(brightness) 


    def update(self):
        print("update brightness")
        #TODO: update all brightness sensors, maybe necessary to store them in a list like lightsources
        #self.brightness = get_brightness(brightness_sensor)


class Observer:
    '''Class that implements the transmission over the KNX Bus, between Actuators and FuntionalModules'''
    def __init__(self):
        self.name = "Central Observer"
        self.functional_modules = []
        self.states = []
        self._observers = [] #_ because private list, still visible from outside, but convention to indicate privacy with _

    def add_functional_module(self, device):
        self.functional_modules.append(device)
        self.states.append(device.state) # states of all functional modules added, with respecting indexes

    # def attach_to_functional_modules(self):
    #     for device in functional_modules:
    #         device.attach(self)

    ### TODO: adapt this system with group addresses

    def notify(self): # alert the _observers
        for observer in self._observers:
            observer.update(self.functional_modules[self._observers.index(observer)]) #the observer (Observer class in room) must have an update method

    def attach(self, observer): #If not in list, add the observer to the list
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer): # Remove the observer from the list
        try:
            self._observers.remove(observer)
        except ValueError:
            pass


    def update(self, notifier):
        self.states[self.functional_modules.index(notifier)] = notifier.state
        print(f"{notifier.name} notified {self.name} of its state: {notifier.state}")
        self.notify()








class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''
    ## INITIALISATION ##
    def __init__(self):
        self.time = Time(simulation_speed_factor=240) # simulation_speed_factor=240 -> 1h of simulated time = 1min of simulation
        self.ambient_temperature = AmbientTemperature(default_temp=(20.0))
        self.ambient_light = AmbientLight(default_brightness = 0) #TODO: set a default brightness depending on the time of day (day/night), blinds state (open/closed), and wheather state(sunny, cloudy,...)
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
