"""
Some class definitions for the simulated KNX functional modules (button, switch, Temp controller,...).
"""
from typing import List, Tuple
from devices.actuators import Heater
from .tools import *
from system.tools import IndividualAddress
from .device_abstractions import FunctionalModule
from .sensors import Thermometer
from system.telegrams import ButtonPayload, HeaterPayload, Payload, Telegram, TempControllerPayload


class Button(FunctionalModule):
    def __init__(self, name, refid, location, default_status):
        super().__init__(name, refid, location, default_status, "button")

    def user_input(self):
        print(f"[INFO] The {self.name} has been pressed")
        payload = ButtonPayload(pushed=True)
        control_field = True
        self.send_telegram(payload, control_field)

class TemperatureController(FunctionalModule):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "thermostat")
        self.state = 10
        self.room_volume = 0
        self.room_insulation = 'average'

    def user_input(self, wished_temp):
        print(
            f"User request for {wished_temp}°C in the room, on controller {self.name}.")
        self.state = wished_temp
        self.update_heaters()

    def receive_telegram(self, telegram: Telegram):
        """Function to react to a received telegram from another device"""
        pass

    def update_heaters(self):
        """Function to update the heaters' values to reach the desired temperature"""
        required = required_power(
            self.state, self.room_volume, self.room_insulation)
        print(f"Sent required wattage to each heater linked to this controller.")
        self.send_telegram(TempControllerPayload(required), True)
