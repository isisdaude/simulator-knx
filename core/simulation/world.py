"""
Some class definitions for the simulation of the physical world
"""

from typing import List
import time, math,schedule


class Time:
    '''Class that implements time by handling events that should be executed at regular intervals'''

    ##TODO: instead of using scheduler, should notify everyone at a clock tick?

    def __init__(self):
        pass

    VIRTUAL_INTERVAL = 60
    ''' Clock ticks every X amount of time '''

    PHYSICAL_INTERVAL = 3600
    ''' Real time that passed between 2 clock ticks '''

    def set_virtual_interval(self, interval:int):
        self.VIRTUAL_INTERVAL = interval

    def set_physical_interval(self, interval:int):
        self.PHYSICAL_INTERVAL = interval

    def add_task(self, task):
        '''Adds a task to the scheduler which executes every virtual time interval to represent some physical time interval'''
        schedule.every(Time.VIRTUAL_INTERVAL)

    def remove_task(self):
        '''Removes a task from the scheduler'''
        pass

    def bigbang(self):
        '''Starts time and the execution of tasks every certain intervals'''
        while True:
            schedule.run_pending()
            time.sleep(1)

class Temperature:
    '''Class that implements temperature in a system'''

    update_rules = []
    '''Represents the updating rules used to impact on temperature'''

    '''List of rules representing how temperature should be impacted at every physical interval, as functions'''

    def __init__(self, default_temp:float):
        self.temperature = default_temp
        self.OUTSIDE_TEMPERATURE = default_temp

    def add_update_rule(self, rule:float): #TODO: should we make a class representing a rule so that we can say on what interval or its name or id? or is it overkill?
        '''Add a rule to the list of rules'''
        self.update_rules.append(rule)

    def remove_update_rule(self):
        pass

    def update(self): ##TODO: for the moment we suppose it is only sums, to see if becomes not enough
        '''Appply the update rules, if none then go back to default outside temperature'''
        if(not self.update_rules):
            self.temperature = self.OUTSIDE_TEMPERATURE
        else:
            self.temperature += sum(self.update_rules)

    def __str__(self):
        return f"{self.temperature}"

    def __repr__(self):
        return f"{self.temperature}"


class AmbiantLight:
    '''Class that implements Light in a room'''
    def __init__(self): # light_sources is a list of all devices that emit light
        self.lightsources = []

    def add_lightsource(self, lightsource):
        self.lightsources.append(lightsource) #lightsource is an object of type light

    def get_brightness(self, brightness_sensor):
        sensor_loc_x = brightness_sensor.loc_x
        sensor_loc_y = brightness_sensor.loc_y
        brightness = 0 # resulting lumen at the brightness sensor location
        for source in self.lightsources:
            source_loc_x = source.loc_x  ## TODO: replace all this by a function compute_distance
            source_loc_y = source.loc_y
            delta_x = abs(source_loc_x-sensor_loc_x)
            delta_y = abs(source_loc_y-sensor_loc_y)
            dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor

            residual_lumen = (1/dist)*source.lm # residual lumens from the source at the brightness location
            brightness += residual_lumen # we basically add the lumen
        return brightness


class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''

    ## INSTANCES TO REPRESENT THE WORLD ##

    time = Time()
    temperature = Temperature(default_temp=10.0)

    def change_virtual_interval(self, interval:int):
        self.time.set_virtual_interval(interval)

    def change_physical_interval(self, interval:int):
        self.time.set_physical_interval(interval)


    ## INITIALISATION & GETTERS

    def __init__(self):
        self.ambiant_light = AmbiantLight()

    def get_temperature(self):
        return self.temperature

    def get_time(self):
        pass

    ## STATUS FUNCTIONS ##
    def update_all(self):
        self.temperature.update()

    def add_lightsource(self, lightsource):
        self.ambiant_light.add_lightsource(lightsource)

    def print_status(self):
        print("+---------- STATUS ----------+")
        print(f" Temperature: {self.temperature}")
        #TODO: add others when availaible
        print("+----------------------------+")
