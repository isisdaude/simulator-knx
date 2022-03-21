"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
from .device_abstractions import FunctionalModule
#from abc import ABC, abstractclassmethod


class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        self.state = 0
        self.name = name

    # @property
    # def state(self):
    #     return self.state

    #@state.setter
    def switch_state(self):
        print(f"switch state of {self.name}")
        if (self.state):
            self.state = 0
        else:
            self.state = 1
        self.notify(self) # notify the observers


    # async def subscribe_async(self, observer):
    #     return None
