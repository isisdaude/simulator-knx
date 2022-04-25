"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
import logging
from .device_abstractions import FunctionalModule
from .sensors import Thermometer
#from abc import ABC, abstractclassmethod


class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        # self.state = 0  ## button has no state, it can just be pressed and realeased directly

    def user_input(self):
        logging.info(f"The {self.name} has been pressed")
        # self.state = not self.state
        payload = 0  ##TODO redefine and prepare the payload here, payload = 0 means push-button
        control_field = True
        self.send_telegram(payload, control_field = True)
        # send to the knxbus giving itself as argument

class Switch(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "switch")
        # self.state = 0  ## button has no state, it can just be pressed and realeased directly
        self.state = False
        self.str_state = "OFF"

    def user_input(self):
        self.state = not self.state
        self.str_state = "ON" if self.str_state=="OFF" else "OFF" #switch the state of the switch
        logging.info(f"The {self.name} has been switched {self.str_state}")
        payload = 1  ##TODO redefine and prepare the payload here, payload = 1 means switch
        control_field = True
        # Send Telegram to the knxbus giving itself as argument
        self.send_telegram(payload, control_field = True)


class TemperatureController(FunctionalModule):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "thermostat")
        self.state = 0
        #self.sensor = Thermometer() ##TODO: init sensor with default config

##TODO:  when temp is set, send telegram to heat sources

    def user_input(self, wished_temp):
        print(f"asked to reach {wished_temp} on controller {self.name}")
        self.state = wished_temp
        payload = wished_temp ##TODO redefine and prepare the payload here, not in functional module
        control_field = 0 # to differentiate between data (temperature read) and control (set heater ON) telegrams
        # depends on the user input/request
        self.send_telegram(payload, control_field = True)
