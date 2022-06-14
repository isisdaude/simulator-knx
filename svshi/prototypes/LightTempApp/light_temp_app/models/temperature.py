###
### DO NOT TOUCH THIS FILE!!!
###

from models.device import Device
from models.multiton import multiton
from typing import Optional


@multiton
class TemperatureSensor(Device):
    """
    A temperature sensor.
    """

    def __init__(self, name: str):
        super().__init__(name, "temperature")

    def read(self) -> Optional[float]:
        """
        Reads the value of the sensor. Returns None if KNX did not answer.
        """
        pass
