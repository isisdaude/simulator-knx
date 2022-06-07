###
### DO NOT TOUCH THIS FILE!!!
###

from models.device import Device
from models.multiton import multiton
from typing import Optional


@multiton
class HumiditySensor(Device):
    """
    A humidity sensor.
    """

    def __init__(self, name: str):
        super().__init__(name, "humidity")

    def read(self) -> Optional[float]:
        """
        Reads the value of the sensor. Returns None if KNX did not answer.
        """
        pass
