"""
Some class definitions for the simulation of the physical world
"""
import schedule, time

class World:
    pass #TODO: should contain an instance of Time for clock ticking

class Time:
    ''' Clock ticks every X amount of time '''
    VIRTUAL_INTERVAL = 60
    ''' Real time that passed between 2 clock ticks '''
    PHYSICAL_INTERVAL = 3600

    def add_task(task):
        schedule.every(Time.VIRTUAL_INTERVAL)
    
    def remove_task():
        pass

    def bigbang():
        while True:
            schedule.run_pending()
            time.sleep(1)