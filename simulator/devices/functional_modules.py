"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
import logging
from .device_abstractions import FunctionalModule
# from .actuators import
# from .sensors import Thermometer
# from system.tools import IndividualAddress
from system.telegrams import ButtonPayload, SwitchPayload, HeaterPayload, Payload, Telegram, TempControllerPayload

#from abc import ABC, abstractclassmethod


class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        # self.state = 0  ## button has no state, it can just be pressed and realeased directly
        self.class_name = 'Button'

    def user_input(self):
        logging.info(f"The {self.name} has been pressed")
        # self.state = not self.state
        payload = ButtonPayload(pushed=True)
        self.send_telegram(payload, control_field = True)
        # send to the knxbus giving itself as argument

class Switch(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "switch")
        self.class_name = 'Switch'
        # self.state = 0  ## button has no state, it can just be pressed and realeased directly
        self.state = False
        self.str_state = "OFF"

    def user_input(self):
        self.state = not self.state
        self.str_state = "ON" if self.str_state=="OFF" else "OFF" #switch the state of the switch
        logging.info(f"The {self.name} has been switched {self.str_state}")
        payload = SwitchPayload(switched=True)
        # Send Telegram to the knxbus giving itself as argument
        self.send_telegram(payload, control_field = True)


class TemperatureController(FunctionalModule):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "thermostat")
        self.class_name = 'TemperatureController'
        self.state = 10
        self.room_volume = 0
        self.room_insulation = 'average'
        #self.sensor = Thermometer() ##TODO: init sensor with default config

##TODO:  when temp is set, send telegram to heat sources

    def user_input(self, wished_temp):
        logging.info(f"User asked to reach {wished_temp} on controller {self.name}")
        self.state = wished_temp
        self.update_heaters() ## TODO update sources

        # payload = wished_temp ##TODO redefine and prepare the payload here, not in functional module
        # control_field = 0 # to differentiate between data (temperature read) and control (set heater ON) telegrams
        # # depends on the user input/request
        # self.send_telegram(payload, control_field = True)

    def update_heaters(self):
        from system.tools import required_power
        """Function to update the heaters' values to reach the desired temperature"""
        required = required_power(self.state, self.room_volume, self.room_insulation)
        logging.info(f"Sent required wattage to each heater linked to this controller.")
        self.send_telegram(TempControllerPayload(required), True)
