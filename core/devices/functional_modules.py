"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
from .device_abstractions import FunctionalModules
#from abc import ABC, abstractclassmethod


class Button(FunctionalModules):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        self.state = 0

    # @property
    # def state(self):
    #     return self.state

    #@state.setter
    def switch_state(self):
        if (self.state):
            self.state = 0
        else:
            self.state = 1
        self.notify(self) # notify the observers


    # async def subscribe_async(self, observer):
    #     return None
