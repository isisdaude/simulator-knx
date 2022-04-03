"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
from typing import List, Tuple
from core.devices.actuators import Heater
from .tools import *
from core.system.tools import IndividualAddress
from .device_abstractions import FunctionalModule
from .sensors import Thermometer
from system.telegrams import ButtonPayload, HeaterPayload, Payload, Telegram, TempControllerPayload


class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")
        # self.state = 0  ## button has no state, it can just be pressed and realeased directly


    def user_input(self):
        print(f"[INFO] The {self.name} has been pressed")
        # self.state = not self.state
        #payload = 0  ##TODO redefine and prepare the payload here, payload = 0 means push-button
        payload = ButtonPayload(pushed=True)
        control_field = True
        self.send_telegram(payload, control_field)
        # send to the knxbus giving itself as argument




class TemperatureController(FunctionalModule):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "thermostat")
        self.state = 10
        self.heaters: List[Tuple[IndividualAddress, int]] = []
        self.room_volume = 0
        self.room_insulation = 'average'

    def user_input(self, wished_temp):
        print(f"User request for {wished_temp}°C in the room, on controller {self.name}.")
        self.state = wished_temp
        #payload = wished_temp ##TODO redefine and prepare the payload here, not in functional module
        payload = TempControllerPayload(wished_temp, Payload.EMPTY_FIELD, Payload.EMPTY_FIELD)
        control_field = 0 # to differentiate between data (temperature read) and control (set heater ON) telegrams
        # depends on the user input/request
        self.send_telegram(payload, control_field = True)
        #TODO: Do we need a telegram for this?

    def receive_telegram(self, telegram: Telegram):
        """Function to react to a received telegram from another device"""
        if isinstance(telegram.payload, HeaterPayload):
            print(f"Got a new value for a heater's max power")
            for idx, (addr, power) in enumerate(self.heaters):
                if addr == telegram.source:
                    self.heaters[idx] = (addr, telegram.payload.max_power)
                    return
            self.heaters.append((telegram.source, telegram.payload.max_power))

    def update_heaters(self):
        """Function to update the heaters' values to reach the desired temperature"""
        for heater in self.heaters:
            required_power(self.state, )