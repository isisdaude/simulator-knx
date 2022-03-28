"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
from .device_abstractions import FunctionalModule
#from abc import ABC, abstractclassmethod


class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        # self.state = 0  ## button has no state, it can just be pressed and realeased directly


    def user_input(self):
        print(f"[INFO] The {self.name} has been pressed")
        # self.state = not self.state
        payload = 0  ##TODO redefine and prepare the payload here, payload = 0 means push-button
        control_field = True
        self.send_telegram(payload, control_field = True)
        # send to the knxbus giving itself as argument




class TemperatureController(FunctionalModule):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "thermostat")
        self.state = 0


    def user_input(self, wished_temp):
        print(f"asked to reach {wished_temp} on controller {self.name}")
        self.state = wished_temp
        payload = wished_temp ##TODO redefine and prepare the payload here, not in functional module
        control_field = 0 # to differentiate between data (temperature read) and control (set heater ON) telegrams
        # depends on the user input/request
        self.send_telegram(payload, control_field = True)
