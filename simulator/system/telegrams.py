"""
Class definitions related to Telegrams and their Payload.
"""

import logging
from abc import ABC


class Telegram:
    """Class to represent a KNX telegram and store its fields"""

    def __init__(self, source_individual_addr, destination_group_addr, payload):
        """
        Initialization of a telegram object.

        source_individual_addr : IndividualAddress,
        destination_group_addr : GroupAddress,
        payload : Payload.
        """
        from system import IndividualAddress, GroupAddress

        self.source: IndividualAddress = source_individual_addr
        self.destination: GroupAddress = destination_group_addr
        self.payload: Payload = payload

    def __str__(self):
        return f" --- -- Telegram -- ---\n-source: {self.source}  \n-destination: {self.destination}  \n-payload: {self.payload}\n --- -------------- --- "


class Payload(ABC):
    """Abstract class to represent the payload given as attribute to the Telegram object.s"""

    def __init__(self) -> None:
        """
        Initialization of a payload object.

        content can be a boolean (True/False for device's state) or a float (Temperature for thermometer value)."""
        super().__init__()
        self.content = None

    def __repr__(self) -> str:
        return f"{self.content}"


class BinaryPayload(Payload):
    """Class to represent a binary payload (True/False)"""

    def __init__(self, binary_state: bool) -> None:
        super().__init__()
        self.content: bool = binary_state

    def __str__(self) -> str:
        return f" BinaryPayload: state={self.content}"

    def __repr__(self) -> str:
        return super().__repr__()


class DimmerPayload(BinaryPayload):
    """Class to represent a dimmer payload (True/False + value)"""

    def __init__(self, binary_state: bool, state_ratio: float) -> None:
        """
        Initialization of dimmer payload object.

        state_ratio is a percentage.
        """
        super().__init__(binary_state)
        try:
            assert state_ratio >= 0 and state_ratio <= 100
            self.state_ratio = state_ratio
        except AssertionError:
            logging.error(
                f"The dimmer value {state_ratio} is not a percentage (0-100), the payload cannot be created."
            )

    def __str__(self) -> str:
        return f" DimmerPayload: state={self.content} | ratio={self.state_ratio}"


class FloatPayload(Payload):
    """Class to represent the payload of a float (e.g. for Sensor values send on bus for svshi)."""

    def __init__(self, value: float) -> None:
        super().__init__()
        self.content: float = value

    def __repr__(self) -> str:
        return super().__repr__()
