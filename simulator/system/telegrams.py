from abc import ABC
import logging

class Telegram:
    """Class to represent KNX telegrams and store its fields"""
    def __init__(self, control_field, source_individual_addr, destination_group_addr, payload):
        from system import IndividualAddress, GroupAddress
        self.control_field = control_field
        self.source: IndividualAddress = source_individual_addr
        self.destination: GroupAddress = destination_group_addr
        self.payload: Payload = payload

    def __str__(self): # syntax when instance is called with print() 
        return f" --- -- Telegram -- ---\n-control_field: {self.control_field} \n-source: {self.source}  \n-destination: {self.destination}  \n-payload: {self.payload}\n --- -------------- --- "
        #return f" --- -- Telegram -- ---\n {self.control} | {self.source} | {self.destination} | {self.payload}"

class Payload(ABC):
    """Abstract class to represent the payload given as attribute to the Telegrams sent"""
    def __init__(self):
        super().__init__()
        self.content = None

    EMPTY_FIELD = None
    """Static constant to represent an empty payload field, that is not used."""

    def __repr__(self) -> str:
        return f"{self.content}"


class BinaryPayload(Payload):
    """Class to represent a binary payload (True/False)"""
    def __init__(self, binary_state: bool):
        super().__init__()
        # Binary state to send on the bus
        self.content: bool = binary_state

    def __str__(self) -> str:
        return f" BinaryPayload: state={self.content}"

    def __repr__(self) -> str:
        return super().__repr__()

class DimmerPayload(BinaryPayload):
    """Class to represent a dimmer payload (True/False + value)"""
    def __init__(self, binary_state: bool, state_ratio: float):
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
        return f" DimmerPayload: state={self.content} | ratio={self.state_ratio}"

class HeaterPayload(Payload):
    """Class to represent the payload of a heater, fields are none if unused"""

    def __init__(self, max_power: float):
        super().__init__()
        self.content: float = max_power

    def __str__(self) -> str:
        ## TODO: display a more truthful payload
        return f"The maximum power of this heater is {self.content}."
