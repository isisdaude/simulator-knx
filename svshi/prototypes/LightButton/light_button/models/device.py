###
### DO NOT TOUCH THIS FILE!!!
###

from abc import ABC


class Device(ABC):
    """
    A KNX device.
    """

    def __init__(self, name: str, type: str):
        super().__init__()
        self.name = name
        self.type = type
