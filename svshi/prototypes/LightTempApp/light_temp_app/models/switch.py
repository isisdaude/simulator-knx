###
### DO NOT TOUCH THIS FILE!!!
###

from models.device import Device
from models.multiton import multiton
from typing import Optional


@multiton
class Switch(Device):
    """
    A switch.
    """

    def __init__(self, name: str):
        super().__init__(name, "switch")

    def on(self):
        """
        Turns the switch on.
        """
        pass

    def off(self):
        """
        Turns the switch off.
        """
        pass

    def is_on(self) -> Optional[bool]:
        """
        Returns True if the switch is on, False if it is off, None if KNX did not answer.
        """
        pass
