from abc import ABC, abstractclassmethod

class Telegram:
    """Class to represent KNX telegrams and store its fields"""
    def __init__(self, control_field, source_individual_addr, destination_group_addr, payload):
        self.control_field = control_field
        self.source = source_individual_addr
        self.destination = destination_group_addr
        self.payload = payload

    def __str__(self): # syntax when instance is called with print()
        return f" --- -- Telegram -- ---\n-control_field: {self.control_field} \n-source: {self.source}  \n-destination: {self.destination}  \n-payload: {self.payload}\n --- -------------- --- "
        #return f" --- -- Telegram -- ---\n {self.control} | {self.source} | {self.destination} | {self.payload}"

class Payload(ABC):
    """Abstract class to represent the payload given as attribute to the Telegrams sent"""
    
    def __init__(self):
        super().__init__()
    
    EMPTY_FIELD = None
    """Static constant to represent an empty payload field, that is not used."""

class ButtonPayload(Payload):
    """Class to represent the payload of a normal button"""

    def __init__(self, pushed: bool):
        super().__init__()
        self.pushed = pushed
    
    def __str__(self) -> str:
        return "The button is pushed." if self.pushed else "The button is not pushed."

class HeaterPayload(Payload):
    """Class to represent the payload of a heater, fields are none if unused"""

    def __init__(self, max_power):
        super().__init__()
        self.max_power = max_power

    def __str__(self) -> str:
        return f"The maximum power of this heater is {self.max_power}."

class TempControllerPayload(Payload):
    """Class to represent the payload of a temperature controller, fields are none if unused"""

    def __init__(self, temperature_request, heater_power_request, set_heater_power):
        super().__init__()
        self.temperature_request = temperature_request
        self.heater_power_request = heater_power_request
        self.set_heater_power = set_heater_power
    
    def __str__(self) -> str:
        if self.temperature_request is not self.EMPTY_FIELD:
            return f"User request for {self.temperature_request}°C in the room."
        elif self.heater_power_request is not self.EMPTY_FIELD:
            return f"Controller request for a heater's maximum power."
        else:
            return f"The temperature controller sets the power of the heater to {self.set_heater_power}."


    