"""Test creation of devices"""
import pytest
import logging

import system
import devices as dev


# Test configuration of system in developper case
# Functional Modules
devices_config = ["led1", "led2", "button1", "bright1", "heater1"]
button1_config = {
    "name": "button1",
    "indiv_addr": [0, 0, 20],
    "location": [0, 0, 1],
    "group_addresses": ["1/1/1"],
}
dimmer1_config = {
    "name": "dimmer1",
    "indiv_addr": [0, 0, 22],
    "location": [8, 5, 1],
    "group_addresses": ["1/1/1"],
}
# Actuators
led1_config = {
    "name": "led1",
    "indiv_addr": [0, 0, 1],
    "location": [5, 5, 1],
    "group_addresses": ["1/1/1"],
    "max_lumen": 800,
    "state_ratio": 100,
    "beam_angle": 180,
    "state_ratio": 100,
    "effective_lumen": 800,
}
heater1_config = {
    "name": "heater1",
    "indiv_addr": [0, 0, 11],
    "max_power": 400,
    "location": [11, 2, 1],
    "group_addresses": ["1/1/1"],
    "state_ratio": 100,
    "power": 400,
}
ac1_config = {
    "name": "ac1",
    "indiv_addr": [0, 0, 12],
    "max_power": 400,
    "location": [11, 5, 1],
    "group_addresses": ["1/1/1"],
    "state_ratio": 100,
    "power": 400,
}
switch1_config = {
    "name": "switch1",
    "indiv_addr": [0, 0, 44],
    "location": [8, 10, 1],
    "group_addresses": ["1/1/1"],
}
# Sensors
bright1_config = {
    "name": "brightness1",
    "indiv_addr": [0, 0, 5],
    "location": [10, 10, 1],
    "group_addresses": ["1/1/1"],
}
thermometer1_config = {
    "name": "thermometer1",
    "indiv_addr": [0, 0, 33],
    "location": [8, 9, 1],
    "group_addresses": ["1/1/1"],
}
humidity_config = {
    "name": "humiditysoil1",
    "indiv_addr": [0, 0, 34],
    "location": [8, 9, 1],
    "group_addresses": ["1/1/1"],
}
co2sensor1_config = {
    "name": "co2sensor1",
    "indiv_addr": [0, 0, 35],
    "location": [8, 9, 2],
    "group_addresses": ["1/1/1"],
}
airsensor1_config = {
    "name": "airsensor1",
    "indiv_addr": [0, 0, 55],
    "location": [8, 9, 3],
    "group_addresses": ["1/1/1"],
}
presencesensor1_config = {
    "name": "presencesensor1",
    "indiv_addr": [0, 0, 66],
    "location": [8, 2, 1],
    "group_addresses": ["1/1/1"],
}


def test_correct_devices_creation():
    # Test correct Button
    button1 = dev.Button("button1", system.IndividualAddress(0, 0, 20))
    assert button1.name == button1_config["name"]
    assert button1.individual_addr.area == button1_config["indiv_addr"][0]
    assert button1.individual_addr.line == button1_config["indiv_addr"][1]
    assert button1.individual_addr.device == button1_config["indiv_addr"][2]
    # Test correct Dimmer
    dimmer1 = dev.Dimmer("dimmer1", system.IndividualAddress(0, 0, 22))
    assert dimmer1.name == dimmer1_config["name"]
    assert dimmer1.individual_addr.area == dimmer1_config["indiv_addr"][0]
    assert dimmer1.individual_addr.line == dimmer1_config["indiv_addr"][1]
    assert dimmer1.individual_addr.device == dimmer1_config["indiv_addr"][2]
    # Test correct LED
    led1 = dev.LED("led1", system.IndividualAddress(0, 0, 1))
    assert led1.name == led1_config["name"]
    assert led1.max_lumen == led1_config["max_lumen"]
    assert led1.beam_angle == led1_config["beam_angle"]
    assert led1.individual_addr.area == led1_config["indiv_addr"][0]
    assert led1.individual_addr.line == led1_config["indiv_addr"][1]
    assert led1.individual_addr.device == led1_config["indiv_addr"][2]
    assert led1.state_ratio == led1_config["state_ratio"]
    assert led1.effective_lumen() == led1_config["effective_lumen"]
    # Test correct Heater
    heater1 = dev.Heater(
        "heater1", system.IndividualAddress(0, 0, 11), 400
    )  # 400W max power
    assert heater1.name == heater1_config["name"]
    assert heater1.individual_addr.area == heater1_config["indiv_addr"][0]
    assert heater1.individual_addr.line == heater1_config["indiv_addr"][1]
    assert heater1.individual_addr.device == heater1_config["indiv_addr"][2]
    assert heater1.max_power == heater1_config["max_power"]
    assert heater1.state_ratio == heater1_config["state_ratio"]
    assert heater1.effective_power() == heater1_config["power"]
    # Test correct AC
    ac1 = dev.AC("ac1", system.IndividualAddress(0, 0, 12), 400)
    assert ac1.name == ac1_config["name"]
    assert ac1.individual_addr.area == ac1_config["indiv_addr"][0]
    assert ac1.individual_addr.line == ac1_config["indiv_addr"][1]
    assert ac1.individual_addr.device == ac1_config["indiv_addr"][2]
    assert ac1.max_power == ac1_config["max_power"]
    assert ac1.state_ratio == ac1_config["state_ratio"]
    assert ac1.effective_power() == ac1_config["power"]
    # Test correct switch
    switch1 = dev.Switch("switch1", system.IndividualAddress(0, 0, 44))
    assert switch1.name == switch1_config["name"]
    assert switch1.individual_addr.area == switch1_config["indiv_addr"][0]
    assert switch1.individual_addr.line == switch1_config["indiv_addr"][1]
    assert switch1.individual_addr.device == switch1_config["indiv_addr"][2]
    # Test correct Brightness sensor
    bright1 = dev.Brightness("brightness1", system.IndividualAddress(0, 0, 5))
    assert bright1.name == bright1_config["name"]
    assert bright1.individual_addr.area == bright1_config["indiv_addr"][0]
    assert bright1.individual_addr.line == bright1_config["indiv_addr"][1]
    assert bright1.individual_addr.device == bright1_config["indiv_addr"][2]
    # Test correct Thermometer
    thermometer1 = dev.Thermometer("thermometer1", system.IndividualAddress(0, 0, 33))
    assert thermometer1.name == thermometer1_config["name"]
    assert thermometer1.individual_addr.area == thermometer1_config["indiv_addr"][0]
    assert thermometer1.individual_addr.line == thermometer1_config["indiv_addr"][1]
    assert thermometer1.individual_addr.device == thermometer1_config["indiv_addr"][2]
    # Test correct HumiditySoil
    humiditysoil1 = dev.HumiditySoil(
        "humiditysoil1", system.IndividualAddress(0, 0, 34)
    )
    assert humiditysoil1.name == humidity_config["name"]
    assert humiditysoil1.individual_addr.area == humidity_config["indiv_addr"][0]
    assert humiditysoil1.individual_addr.line == humidity_config["indiv_addr"][1]
    assert humiditysoil1.individual_addr.device == humidity_config["indiv_addr"][2]
    # Test correct CO2Sensor
    co2sensor1 = dev.CO2Sensor("co2sensor1", system.IndividualAddress(0, 0, 35))
    assert co2sensor1.name == co2sensor1_config["name"]
    assert co2sensor1.individual_addr.area == co2sensor1_config["indiv_addr"][0]
    assert co2sensor1.individual_addr.line == co2sensor1_config["indiv_addr"][1]
    assert co2sensor1.individual_addr.device == co2sensor1_config["indiv_addr"][2]
    # Test correct AirSensor
    airsensor1 = dev.AirSensor("airsensor1", system.IndividualAddress(0, 0, 55))
    assert airsensor1.name == airsensor1_config["name"]
    assert airsensor1.individual_addr.area == airsensor1_config["indiv_addr"][0]
    assert airsensor1.individual_addr.line == airsensor1_config["indiv_addr"][1]
    assert airsensor1.individual_addr.device == airsensor1_config["indiv_addr"][2]
    # Test correct PresenceSensor
    presencesensor1 = dev.PresenceSensor(
        "presencesensor1", system.IndividualAddress(0, 0, 66)
    )
    assert presencesensor1.name == presencesensor1_config["name"]
    assert (
        presencesensor1.individual_addr.area == presencesensor1_config["indiv_addr"][0]
    )
    assert (
        presencesensor1.individual_addr.line == presencesensor1_config["indiv_addr"][1]
    )
    assert (
        presencesensor1.individual_addr.device
        == presencesensor1_config["indiv_addr"][2]
    )


devices_classes = {
    "Button": dev.Button,
    "Dimmer": dev.Dimmer,
    "LED": dev.LED,
    "Heater": dev.Heater,
    "AC": dev.AC,
    "Switch": dev.Switch,
    "Brightness": dev.Brightness,
    "Thermometer": dev.Thermometer,
    "HumiditySoil": dev.HumiditySoil,
    "CO2Sensor": dev.CO2Sensor,
    "AirSensor": dev.AirSensor,
    "PresenceSensor": dev.PresenceSensor,
}
false_device_names = ["", "device_4*", 420]
wrong_device_names = {
    "Button": ["BUTTON1", "button 1", "button_1", "switch4"],
    "Dimmer": ["DIMMER1", "dimmer 1", "dimmer_1", "led3"],
    "LED": ["LED1", "led 1", "led_1", "bright4"],
    "Heater": ["HEATER1", "heater 1", "heater_1", "button1"],
    "AC": ["AC1", "ac 1", "ac_1", "led4"],
    "Switch": ["SWITCH1", "switch 1", "switch_1", "ac4"],
    "Brightness": ["BRIGHT1", "bright 1", "bright_1", "heater4"],
    "Thermometer": ["THERMOMETER1", "thermometer 1", "thermometer_1", "bright2"],
    "HumiditySoil": [
        "HUMIDITYSENSOR1",
        "humidity sensor 1",
        "humiditysoil_1",
        "thermometer1",
    ],
    "CO2Sensor": ["CO2SENSOR1", "co2 sensor 1", "co2sensor_1", "humiditysoil1"],
    "AirSensor": ["AIRSENSOR1", "air sensor 1", "airsensor_1", "thermometer2"],
    "PresenceSensor": [
        "PRESENCESENSOR1",
        "presence sensor 1",
        "presencesensor_1",
        "button2",
    ],
}

# Test Sys Exit if incorrect device name
def test_incorrect_device_name():
    for dev_name in false_device_names:
        for dev_class in devices_classes:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](dev_name, system.IndividualAddress(1, 1, 1))
            assert pytest_wrapped_error.type == SystemExit
    for dev_class in wrong_device_names:
        for wrong_name in wrong_device_names[dev_class]:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](
                    wrong_name, system.IndividualAddress(1, 1, 1)
                )
            assert pytest_wrapped_error.type == SystemExit


# Test Sys Exit if incorrect Individual Address
false_indiv_addr = [(-1, 0, 12), (2.4, 10, 10), (0, 20, 200), ("a", "l0", 20)]


def test_incorrect_device_ia():
    for dev_ia in false_indiv_addr:
        for dev_class in devices_classes:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](
                    dev_class.lower(),
                    system.IndividualAddress(dev_ia[0], dev_ia[1], dev_ia[2]),
                )
            assert pytest_wrapped_error.type == SystemExit
