""" Test exchange of telegrams"""

import pytest
import sys

sys.path.append("..")
from system import Room
import devices as dev
from system.system_tools import IndividualAddress

system_dt = 1
# Declaration of sensors, actuators and functional modules

# ACTUATORS
led1 = dev.LED("led1", IndividualAddress(0, 0, 1))  # Area 0, Line 0, Device 0
heater1 = dev.Heater("heater1", IndividualAddress(0, 0, 2), 400)  # 400W max power
ac1 = dev.AC("ac1", IndividualAddress(0, 0, 3), 400)
switch1 = dev.Switch("switch1", IndividualAddress(0, 0, 4))
# interface = dev.IPInterface("interface", IndividualAddress(0,0,5))

# SENSORS
bright1 = dev.Brightness("brightness1", IndividualAddress(0, 0, 6))
therm1 = dev.Thermometer("thermometer1", IndividualAddress(0, 0, 7))
humidity_air1 = dev.HumidityAir("humidityair1", IndividualAddress(0, 0, 8))
humidity_soil1 = dev.HumiditySoil("humiditysoil1", IndividualAddress(0, 0, 9))
co2sensor1 = dev.CO2Sensor("co2sensor1", IndividualAddress(0, 0, 10))
airsensor1 = dev.AirSensor("airsensor1", IndividualAddress(0, 0, 11))

# FUNCTIONAL MODULES
button1 = dev.Button("button1", IndividualAddress(0, 0, 12))
dimmer1 = dev.Dimmer("dimmer1", IndividualAddress(0, 0, 13))

# Declaration of the physical system
room1 = Room(
    "bedroom1",
    20,
    20,
    3,
    180,
    "3-levels",
    system_dt,
    "good",
    20.0,
    50.0,
    300,
    test_mode=False,
    svshi_mode=False,
    telegram_logging=False,
)

room1.add_device(led1, 5, 5, 1)


def test_detach():
    # FUNCTIONAL MODULES
    button1 = dev.Button("button1", IndividualAddress(0, 0, 12))

    # Declaration of the physical system
    room1 = Room(
        "bedroom1",
        20,
        20,
        3,
        180,
        "3-levels",
        system_dt,
        "good",
        20.0,
        50.0,
        300,
        test_mode=False,
        svshi_mode=False,
        telegram_logging=False,
    )

    room1.add_device(button1, 5, 5, 1)

    ga1 = "1/1/1"
    room1.attach(button1, ga1)
    before = room1.knxbus.get_info()

    room1.detach(button1, ga1)
    after = room1.knxbus.get_info()

    assert before.get("group_addresses").get(ga1, None) != after.get(
        "group_addresses"
    ).get(ga1, None)


def test_dev_info():
    # ACTUATORS
    led1 = dev.LED("led1", IndividualAddress(0, 0, 1))  # Area 0, Line 0, Device 0
    heater1 = dev.Heater("heater1", IndividualAddress(0, 0, 2), 400)  # 400W max power
    ac1 = dev.AC("ac1", IndividualAddress(0, 0, 3), 400)
    switch1 = dev.Switch("switch1", IndividualAddress(0, 0, 4))

    # SENSORS
    bright1 = dev.Brightness("brightness1", IndividualAddress(0, 0, 6))
    therm1 = dev.Thermometer("thermometer1", IndividualAddress(0, 0, 7))
    humidity_air1 = dev.HumidityAir("humidityair1", IndividualAddress(0, 0, 8))
    humidity_soil1 = dev.HumiditySoil("humiditysoil1", IndividualAddress(0, 0, 9))
    co2sensor1 = dev.CO2Sensor("co2sensor1", IndividualAddress(0, 0, 10))
    airsensor1 = dev.AirSensor("airsensor1", IndividualAddress(0, 0, 11))

    # FUNCTIONAL MODULES
    button1 = dev.Button("button1", IndividualAddress(0, 0, 12))
    dimmer1 = dev.Dimmer("dimmer1", IndividualAddress(0, 0, 13))

    # TO TEST FUNCTIONING
    led1 = dev.LED("led1", IndividualAddress(0, 0, 1))

    assert button1.get_dev_info() == {
        "state": False,
        "class_name": "Button",
        "individual_address": "0.0.12",
    }
    assert dimmer1.get_dev_info() == {
        "state": False,
        "state_ratio": 100,
        "class_name": "Dimmer",
        "individual_address": "0.0.13",
    }

    assert led1.get_dev_info() == {
        "state": False,
        "max_lumen": 800,
        "effective_lumen": 800.0,
        "beam_angle": 180,
        "state_ratio": 100,
        "class_name": "LED",
        "individual_address": "0.0.1",
    }
    assert heater1.get_dev_info() == {
        "state": False,
        "update_rule": 1,
        "max_power": 400,
        "state_ratio": 100,
        "effective_power": 400.0,
        "class_name": "Heater",
        "individual_address": "0.0.2",
    }
    assert ac1.get_dev_info() == {
        "state": False,
        "update_rule": -1,
        "max_power": 400,
        "state_ratio": 100,
        "effective_power": 400.0,
        "class_name": "AC",
        "individual_address": "0.0.3",
    }
    assert switch1.get_dev_info() == {
        "state": False,
        "class_name": "Switch",
        "individual_address": "0.0.4",
    }

    assert bright1.get_dev_info() == {
        "brightness": "0 lux",
        "class_name": "Brightness",
        "individual_address": "0.0.6",
    }
    assert bright1.get_dev_info(True) == {"brightness": 0}

    assert therm1.get_dev_info(True) == {"temperature": 0}
    assert therm1.get_dev_info() == {
        "temperature": "0 °C",
        "class_name": "Thermometer",
        "individual_address": "0.0.7",
    }

    assert humidity_air1.get_dev_info(True) == {"humidity": 0}
    assert humidity_air1.get_dev_info() == {
        "humidity": "0 %",
        "class_name": "HumidityAir",
        "individual_address": "0.0.8",
    }

    assert humidity_soil1.get_dev_info() == {
        "humiditysoil": "10 %",
        "class_name": "HumiditySoil",
        "individual_address": "0.0.9",
    }
    assert humidity_soil1.get_dev_info(True) == {"humiditysoil": 10}

    assert co2sensor1.get_dev_info(True) == {"co2": 0}
    assert co2sensor1.get_dev_info() == {
        "co2": "0 ppm",
        "class_name": "CO2Sensor",
        "individual_address": "0.0.10",
    }

    assert airsensor1.get_dev_info() == {
        "class_name": "AirSensor",
        "individual_address": "0.0.11",
    }
    airsensor1.temperature = 1.0
    airsensor1.humidity = 40
    airsensor1.co2 = 400
    assert airsensor1.get_dev_info(True) == {
        "temperature": 1.0,
        "humidity": 40,
        "co2": 400,
    }
    assert airsensor1.get_dev_info() == {
        "temperature": "1.0 °C",
        "humidity": "40 %",
        "co2": "400 ppm",
        "class_name": "AirSensor",
        "individual_address": "0.0.11",
    }

    room1 = Room(
        "bedroom1",
        20,
        20,
        3,
        180,
        "3-levels",
        system_dt,
        "good",
        20.0,
        50.0,
        300,
        test_mode=False,
        svshi_mode=False,
        telegram_logging=False,
    )

    from svshi_interface.main import Interface

    interface = Interface(room1, False, testing=True)
    interface_device = dev.IPInterface(
        "ipinterface", IndividualAddress(0, 0, 14), interface
    )

    assert interface_device.get_dev_info() is None


def test_humidity_soil_set_value():
    humidity_soil1 = dev.HumiditySoil("humiditysoil1", IndividualAddress(0, 0, 9))

    assert humidity_soil1.set_value(-1) is None
    assert humidity_soil1.set_value(101) is None

    assert humidity_soil1.set_value(45) == 1


def test_user_input_functional_modules():
    # FUNCTIONAL MODULES
    button1 = dev.Button("button1", IndividualAddress(0, 0, 12))
    dimmer1 = dev.Dimmer("dimmer1", IndividualAddress(0, 0, 13))

    # TO TEST FUNCTIONING
    led1 = dev.LED("led1", IndividualAddress(0, 0, 1))

    # Declaration of the physical system
    room1 = Room(
        "bedroom1",
        20,
        20,
        3,
        180,
        "3-levels",
        system_dt,
        "good",
        20.0,
        50.0,
        300,
        test_mode=False,
        svshi_mode=False,
        telegram_logging=False,
    )

    room1.add_device(button1, 5, 5, 1)
    room1.add_device(dimmer1, 10, 10, 1)
    room1.add_device(led1, 0, 0, 0)

    ga1 = "1/1/1"
    room1.attach(button1, ga1)
    room1.attach(led1, ga1)

    before = led1.state

    button1.user_input(True)

    after = led1.state

    assert before != after

    button1.user_input()

    after = led1.state

    assert before == after

    room1.detach(button1, ga1)

    room1.attach(dimmer1, ga1)

    dimmer1.user_input(True, 100)

    after = led1.state

    assert before != after


def test_update_state_actuator():
    # ACTUATORS
    led1 = dev.LED("led1", IndividualAddress(0, 0, 1))  # Area 0, Line 0, Device 0
    heater1 = dev.Heater("heater1", IndividualAddress(0, 0, 2), 400)  # 400W max power
    ac1 = dev.AC("ac1", IndividualAddress(0, 0, 3), 400)
    switch1 = dev.Switch("switch1", IndividualAddress(0, 0, 4))

    from system.telegrams import Telegram, BinaryPayload, DimmerPayload, FloatPayload
    from system import GroupAddress

    ga = GroupAddress("3-levels", 0, 0, 0)

    bin_telegram = Telegram(led1.individual_addr, ga, BinaryPayload(True))
    dimmer_telegram = Telegram(led1.individual_addr, ga, DimmerPayload(False, 100))

    before = led1.state
    led1.update_state(bin_telegram)

    assert before != led1.state

    led1.update_state(dimmer_telegram)
    assert before == led1.state

    before = heater1.state
    heater1.update_state(bin_telegram)

    assert before != heater1.state

    heater1.update_state(dimmer_telegram)
    assert before == heater1.state

    before = ac1.state
    ac1.update_state(bin_telegram)

    assert before != ac1.state

    ac1.update_state(dimmer_telegram)
    assert before == ac1.state

    before = switch1.state
    switch1.update_state(bin_telegram)

    assert before != switch1.state

    switch1.update_state(dimmer_telegram)
    assert before == switch1.state

    # Declaration of the physical system
    room1 = Room(
        "bedroom1",
        20,
        20,
        3,
        180,
        "3-levels",
        system_dt,
        "good",
        20.0,
        50.0,
        300,
        test_mode=False,
        svshi_mode=False,
        telegram_logging=False,
    )

    from svshi_interface.main import Interface

    interface = Interface(room1, False, testing=True)
    interface_device = dev.IPInterface(
        "ipinterface", IndividualAddress(0, 0, 14), interface
    )

    float_telegram = Telegram(led1.individual_addr, ga, FloatPayload(2.1))
    interface_device.update_state(bin_telegram)
    interface_device.update_state(float_telegram)
    interface_device.update_state(dimmer_telegram)

    from svshi_interface.telegram_parser import TelegramParser

    parser = TelegramParser({"0/0/0": BinaryPayload})

    element = interface_device.interface._Interface__sending_queue.get()
    assert str(parser.from_knx_telegram(element)) == str(bin_telegram)

    parser = TelegramParser({"0/0/0": FloatPayload})
    element = interface_device.interface._Interface__sending_queue.get()
    assert str(parser.from_knx_telegram(element)) == str(float_telegram)

    parser = TelegramParser()
    element = interface_device.interface._Interface__sending_queue.get()
    assert str(parser.from_knx_telegram(element)) == str(
        Telegram(led1.individual_addr, ga, BinaryPayload(False))
    )


def test_fails_on_wrong_update_value():

    with pytest.raises(SystemExit) as exc_info:
        heater1 = dev.Heater(
            "heater1", IndividualAddress(0, 0, 2), 400, update_rule=-1
        )  # 400W max power
        assert "The Heater should have update_rule > 0, but -1 was given." in exc_info

    with pytest.raises(SystemExit) as exc_info:
        ac1 = dev.AC("ac1", IndividualAddress(0, 0, 3), 400, update_rule=1)
        assert "The AC should have update_rule < 0, but 1 was given." in exc_info


class TestingReceiveDevice(dev.Actuator):
    def __init__(
        self, name: str, individual_addr: IndividualAddress, received: bool = False
    ) -> None:
        """Initialization of a LED device object"""
        super().__init__(name, individual_addr, received)

    from system.telegrams import Telegram

    def update_state(self, telegram: Telegram) -> None:
        self.state = True

    def get_dev_info(self):
        pass


def test_sensors_send_telegrams():
    # SENSORS
    bright1 = dev.Brightness("brightness1", IndividualAddress(0, 0, 6))
    therm1 = dev.Thermometer("thermometer1", IndividualAddress(0, 0, 7))
    humidity_air1 = dev.HumidityAir("humidityair1", IndividualAddress(0, 0, 8))
    humidity_soil1 = dev.HumiditySoil("humiditysoil1", IndividualAddress(0, 0, 9))
    co2sensor1 = dev.CO2Sensor("co2sensor1", IndividualAddress(0, 0, 10))

    # TO TEST FUNCTIONING
    led1 = dev.LED("led1", IndividualAddress(0, 0, 1))

    test_receive = TestingReceiveDevice(
        "testingreceivedevice", IndividualAddress(0, 0, 30)
    )

    # Declaration of the physical system
    room1 = Room(
        "bedroom1",
        20,
        20,
        3,
        180,
        "3-levels",
        system_dt,
        "good",
        20.0,
        50.0,
        300,
        test_mode=False,
        svshi_mode=False,
        telegram_logging=False,
    )

    room1.add_device(bright1, 5, 5, 1)
    bright1.knxbus = room1.knxbus
    room1.add_device(therm1, 10, 10, 1)
    therm1.knxbus = room1.knxbus
    room1.add_device(humidity_air1, 11, 10, 1)
    humidity_air1.knxbus = room1.knxbus
    room1.add_device(humidity_soil1, 12, 10, 1)
    humidity_soil1.knxbus = room1.knxbus
    room1.add_device(co2sensor1, 13, 10, 1)
    co2sensor1.knxbus = room1.knxbus
    room1.add_device(led1, 0, 0, 0)
    room1.add_device(test_receive, 0, 1, 0)

    def try_sending_state(sensor):
        """Helper function for sending the state, receiving the telegram and reinitalizing the state"""
        room1.attach(sensor, ga1)
        sensor.send_state()
        assert test_receive.state == True
        room1.detach(sensor, ga1)
        test_receive.state = False

    ga1 = "1/1/1"
    room1.attach(test_receive, ga1)

    try_sending_state(bright1)
    try_sending_state(therm1)
    try_sending_state(humidity_air1)
    try_sending_state(humidity_soil1)
    try_sending_state(co2sensor1)
