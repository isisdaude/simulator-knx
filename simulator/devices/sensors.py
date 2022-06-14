"""
Class definitions for the simulated KNX sensors:
Brightness, Thermometer, HumiditySoil, HumidityAir, CO2Sensor, AirSensor and PresenceSensor.
"""

import logging
from typing import Dict, Union, Tuple

from .device_abstractions import Sensor
from system.system_tools import IndividualAddress


class Brightness(Sensor):
    """Concrete class to represent Brightness sensor"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of Brightness device object"""
        super().__init__(name, individual_addr)
        self.brightness = 0

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the Brightness sensor device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the numeric value only, if False, send the string value and basic device info."""
        if value:
            dev_specific_dict = {"brightness": round(self.brightness, 2)}
        else:
            dev_specific_dict = {"brightness": str(round(self.brightness, 2)) + " lux"}
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

    def send_state(self) -> None:
        """
        Send sensor's measured value on the bus,
        only in svshi mode,
        only if the sensor is assigned to a group address."""
        from system import FloatPayload

        if len(self.group_addresses) and hasattr(self, "knxbus"):
            payload = FloatPayload(self.brightness)
            self.send_telegram(payload)


class Thermometer(Sensor):
    """Concrete class to represent a Temperature sensor"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of Thermometer device object"""
        super().__init__(name, individual_addr)
        # DTP
        self.temperature = 0

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the Thermometer device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the numeric value only, if False, send the string value and basic device info."""
        if value:
            dev_specific_dict = {"temperature": round(self.temperature, 2)}
        else:
            dev_specific_dict = {"temperature": str(round(self.temperature, 2)) + " °C"}
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

    def send_state(self) -> None:
        """
        Send sensor's measured value on the bus,
        only in svshi mode,
        only if the sensor is assigned to a group address."""
        from system import FloatPayload

        if len(self.group_addresses) and hasattr(self, "knxbus"):
            payload = FloatPayload(self.temperature)
            self.send_telegram(payload)


class HumidityAir(Sensor):
    """Concrete class to represent a Air Humidity sensor"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of HumidityAir device object"""
        super().__init__(name, individual_addr)
        self.humidity = 0

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the Air Humidity device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the numeric value only, if False, send the string value and basic device info."""
        if value:
            dev_specific_dict = {"humidity": round(self.humidity, 2)}
        else:
            dev_specific_dict = {"humidity": str(round(self.humidity, 2)) + " %"}
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

    def send_state(self) -> None:
        """
        Send sensor's measured value on the bus,
        only in svshi mode,
        only if the sensor is assigned to a group address."""
        from system import FloatPayload

        if len(self.group_addresses) and hasattr(self, "knxbus"):
            payload = FloatPayload(self.humidity)
            self.send_telegram(payload)


class CO2Sensor(Sensor):
    """Concrete class to represent a CO2 Sensor"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of CO2Sensor device object"""
        super().__init__(name, individual_addr)
        self.co2 = 0

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the CO2 Sensor device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the numeric value only, if False, send the string value and basic device info."""
        if value:
            dev_specific_dict = {"co2": round(self.co2, 2)}
        else:
            dev_specific_dict = {"co2": str(round(self.co2, 2)) + " ppm"}
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

    def send_state(self) -> None:
        """
        Send sensor's measured value on the bus,
        only in svshi mode,
        only if the sensor is assigned to a group address."""
        from system import FloatPayload

        if len(self.group_addresses) and hasattr(self, "knxbus"):
            payload = FloatPayload(self.co2)
            self.send_telegram(payload)


class AirSensor(Sensor):
    """Concrete class to represent an Air Sensor: CO2, Humidity and/or Temperature"""

    def __init__(
        self,
        name: str,
        individual_addr: IndividualAddress,
        temp_supported: bool = False,
        hum_supported: bool = False,
        co2_supported: bool = False,
    ) -> None:
        """Initialization of AirSensor device object"""
        super().__init__(name, individual_addr)
        self.temperature = None
        self.humidity = None
        self.co2 = None

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the Air Sensor device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the numeric values only, if False, send the string value and basic device info."""
        if value:
            dev_specific_dict = {}
            if self.temperature is not None:
                dev_specific_dict["temperature"] = round(self.temperature, 2)

            if self.humidity is not None:
                dev_specific_dict["humidity"] = round(self.humidity, 2)

            if self.co2 is not None:
                dev_specific_dict["co2"] = round(self.co2, 2)

        if not value:
            dev_specific_dict = {}
            if self.temperature is not None:
                dev_specific_dict["temperature"] = (
                    str(round(self.temperature, 2)) + " °C"
                )

            if self.humidity is not None:
                dev_specific_dict["humidity"] = str(round(self.humidity, 2)) + " %"

            if self.co2 is not None:
                dev_specific_dict["co2"] = str(round(self.co2, 2)) + " ppm"

            dev_specific_dict.update(self._dev_basic_dict)

        return dev_specific_dict

    def send_state(self) -> None:
        """Cannot send values on the bus, as there is no way (for now) to differenciate temperature from co2 or humidity value on the same group address in SVSHI."""
        pass


class HumiditySoil(Sensor):
    """Concrete class to represent a Soil Moisture sensor"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of HumiditySoil device object"""
        super().__init__(name, individual_addr)
        self.humiditysoil = 10  # arbitrary init of soil humidity

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the Soil Moisture device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the numeric value only, if False, send the string value and basic device info."""
        if value:
            dev_specific_dict = {"humiditysoil": round(self.humiditysoil, 2)}
        else:
            dev_specific_dict = {
                "humiditysoil": str(round(self.humiditysoil, 2)) + " %"
            }
            dev_specific_dict.update(self._dev_basic_dict)
        return dev_specific_dict

    def set_value(self, value: float) -> Union[None, int]:
        """
        Set the measured soil moisture value (0-100).
        Called with API command 'set' to change a physical state, here the soil moisture.
        """
        if value < 0 or value > 100:
            logging.warning(
                f"The soil humidity value should be in (0-100), but {value} was given."
            )
            return None
        else:
            self.humiditysoil = value
            return 1

    def send_state(self) -> None:
        """
        Send sensor's measured value on the bus,
        only in svshi mode,
        only if the sensor is assigned to a group address."""
        from system import FloatPayload

        if len(self.group_addresses) and hasattr(self, "knxbus"):
            payload = FloatPayload(self.humiditysoil)
            self.send_telegram(payload)


class PresenceSensor(Sensor):
    """Concrete class to represent a Presence Sensor"""

    def __init__(self, name: str, individual_addr: IndividualAddress) -> None:
        """Initialization of PresenceSensor device object"""
        super().__init__(name, individual_addr)
        # self.presence = False
        self.state = False

    def get_dev_info(
        self, value: bool = False
    ) -> Dict[str, Union[str, float, Tuple[float, float, float]]]:
        """
        Return information about the Presence Sensor device's states and configuration, method called via CLI commmand 'getinfo'.

        value : if True, send the boolean value only, if False, send the string value and basic device info."""
        dev_specific_dict = {"presence": self.state}
        if not value:
            dev_specific_dict = self._dev_basic_dict
        return dev_specific_dict

    def set_value(self, value: bool) -> Union[None, int]:
        """
        Set the measured presence value (True/False).
        Called with API command 'set' to change a physical state, here the presence.
        """
        if value not in [True, False]:
            logging.warning(
                f"The presence value should be in [True, False], but {value} was given."
            )
            return None
        else:
            self.state = value
            return 1

    def send_state(self) -> None:
        """
        Send sensor's measured value on the bus,
        only in svshi mode,
        only if the sensor is assigned to a group address."""
        from system import FloatPayload

        if len(self.group_addresses) and hasattr(self, "knxbus"):
            payload = FloatPayload(self.humiditysoil)
            self.send_telegram(payload)
