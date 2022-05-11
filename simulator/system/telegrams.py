from abc import ABC, abstractclassmethod
from ast import Assert
import logging



class Telegram:
    """Class to represent KNX telegrams and store its fields"""
    def __init__(self, control_field, source_individual_addr, destination_group_addr, payload):
        from system.tools import IndividualAddress
        self.control_field = control_field
        self.source: IndividualAddress = source_individual_addr
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

class BinaryPayload(Payload):
    """Class to represent a binary payload (True/False)"""
    def __init__(self, binary_state: bool):
        super().__init__()
        # Binary state to send on the bus
        self.binary_state = binary_state

    def __str__(self) -> str:
        return f" BinaryPayload: {self.binary_state}"

class SwitchPayload(Payload):
    """Class to represent a switch 'binary' payload (True/False)"""
    def __init__(self, switch_state: bool):
        super().__init__()
        # Binary state received from the bus
        self.switch_state = switch_state

    def __str__(self) -> str:
        return f" BinaryPayload: {self.switch_state}"

class DimmerPayload(BinaryPayload):
    """Class to represent a dimmer payload (True/False + value)"""
    def __init__(self, binary_state: bool, state_ratio : float):
        super().__init__(binary_state) # Initialize the Binary Payload attribute to determine of device should be turned ON/OFF
        # state_ratio corresponding to dimming value (percentage)
        try:
            assert state_ratio >= 0 and state_ratio <= 100
        except AssertionError:
            logging.error(f"The dimmer value {state_ratio} is not a percentage (0-100).")
            # sys.exite(1) ?
            return
        self.state_ratio = state_ratio

    def __str__(self) -> str:
        return f" DimmerPayload: {self.binary_state} | {self.state_ratio}"

# class SwitchPayload(Payload):
#     """Class to represent the Switch's state (device receiving a boolean on the bus), if demanded by another device or the user"""
#     def __init__(self, switched: bool):
#         super().__init__()
#         self.switched = switched
#     def __str__(self) -> str:
#         ## TODO: display a more truthful payload
#         return ""

class ButtonPayload(Payload):
    """Class for the payload of a Button's state"""
    def __init__(self, state: bool): # pushed: bool,
        super().__init__()
        self.state = state

    # def __str__(self) -> str:
    #     ## TODO: display a more truthful payload
    #     return "The button is pushed." if self.pushed else "The button is not pushed."


# class SwitchPayload(Payload):
#     """Class to represent the payload of a switch (button with state)"""
#     def __init__(self, switched: bool):
#         super().__init__()
#         self.switched = switched

#     def __str__(self) -> str:
#         ## TODO: display a more truthful payload
#         return "The switch is switched." if self.switched else "The switch is not switched."




class HeaterPayload(Payload):
    """Class to represent the payload of a heater, fields are none if unused"""

    def __init__(self, max_power):
        super().__init__()
        self.max_power = max_power

    def __str__(self) -> str:
        ## TODO: display a more truthful payload
        return f"The maximum power of this heater is {self.max_power}."

class TempControllerPayload(Payload):
    """Class to represent the payload of a temperature controller, fields are none if unused"""

    def __init__(self, set_heater_power):
        super().__init__()
        self.set_heater_power = set_heater_power

    def __str__(self) -> str:
        ## TODO: display a more truthful payload
        return f"The temperature controller sets the power of the heater to {self.set_heater_power}."
