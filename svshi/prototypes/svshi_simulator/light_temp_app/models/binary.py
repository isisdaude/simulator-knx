###
### DO NOT TOUCH THIS FILE!!!
###

from models.device import Device
from models.multiton import multiton
from typing import Optional


@multiton
class BinarySensor(Device):
    """
    A binary sensor.
    """

    def __init__(self, name: str):
        super().__init__(name, "binary")

    def is_on(self) -> Optional[bool]:
        """
        Returns True if the sensor is on, False if it is off, None if KNX did not answer.
        """
        pass
