"""
Some class definitions for the simulation of the physical world
"""

import schedule, time


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

    def add_task(task):
        '''Adds a task to the scheduler which executes every virtual time interval to represent some physical time interval'''
        schedule.every(Time.VIRTUAL_INTERVAL)
    
    def remove_task():
        '''Removes a task from the scheduler'''
        pass

    def bigbang():
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


class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''
    
    ## INSTANCES TO REPRESENT THE WORLD ##
    time = Time()

    def change_virtual_interval(self, interval:int):
        self.time.set_virtual_interval(interval)

    def change_physical_interval(self, interval:int):
        self.time.set_physical_interval(interval)

    temperature = Temperature(default_temp=10.0)

    ## INITIALISATION & GETTERS
    def __init__(self):
        pass

    def get_temperature(self):
        return self.temperature

    def get_time(self):
        pass

    ## STATUS FUNCTIONS ##
    def update_all(self):
        self.temperature.update()

    def print_status(self):
        print("+---------- STATUS ----------+")
        print(f" Temperature: {self.temperature}")
        #TODO: add others when availaible
        print("+----------------------------+")
