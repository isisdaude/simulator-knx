#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import devices as dev


# Test configuration of system in developper case 
# Functional Modules
devices_config = ['led1', 'led2', 'button1', 'bright1', 'heater1']
button1_config = {"name":"button1", "refid":"M-0_S1", "indiv_addr":[0,0,20], "status":"enabled", "location":[0,0,1], "group_addresses":['1/1/1']}
dimmer1_config = {"name":"dimmer1", "refid":"M-0_D1", "indiv_addr":[0,0,22], "status":"enabled", "location":[8,5,1], "group_addresses":['1/1/1']}
# Actuators
led1_config = {"name":"led1", "refid":"M-0_L1", "indiv_addr":[0,0,1], "status":"enabled", "location":[5,5,1], "group_addresses":['1/1/1'], "max_lumen":800, "state_ratio":100, "beam_angle":180, "state_ratio":100, "effective_lumen":800}
heater1_config = {"name":"heater1", "refid":"M-0_H1", "indiv_addr":[0,0,11], "status":"enabled", "max_power":400, "location":[11,2,1], "group_addresses":['1/1/1'], "state_ratio":100, "power":400}
ac1_config = {"name":"ac1", "refid":"M-0_C1", "indiv_addr":[0,0,12], "status":"enabled", "max_power":400, "location":[11,5,1], "group_addresses":['1/1/1'], "state_ratio":100, "power":400}
switch1_config = {"name":"switch1", "refid":"M-0_S3", "indiv_addr":[0,0,44], "status":"enabled", "location":[8,10,1], "group_addresses":['1/1/1']}
# Sensors
bright1_config = {"name":"brightness1", "refid":"M-0_L3", "indiv_addr":[0,0,5], "status":"enabled", "location":[10,10,1], "group_addresses":['1/1/1']}
thermometer1_config = {"name":"thermometer1", "refid":"M-0_T1", "indiv_addr":[0,0,33], "status":"enabled", "location":[8,9,1], "group_addresses":['1/1/1']}
humidity_config = {"name":"humiditysoil1", "refid":"M-0_HU1", "indiv_addr":[0,0,34], "status":"enabled", "location":[8,9,1], "group_addresses":['1/1/1']}
co2sensor1_config = {"name":"co2sensor1", "refid":"M-0_CO2", "indiv_addr":[0,0,35], "status":"enabled", "location":[8,9,2], "group_addresses":['1/1/1']}
airsensor1_config = {"name":"airsensor1", "refid":"M-0_A1", "indiv_addr":[0,0,55], "status":"enabled", "location":[8,9,3], "group_addresses":['1/1/1']}
presencesensor1_config = {"name":"presencesensor1", "refid":"M-0_P1", "indiv_addr":[0,0,66], "status":"enabled", "location":[8,2,1], "group_addresses":['1/1/1']}


def test_correct_devices_creation():
    # Test correct Button
    button1 = dev.Button("button1", "M-0_S1", system.IndividualAddress(0,0,20), "enabled")
    assert button1.name == button1_config["name"]
    assert button1.refid == button1_config["refid"]
    assert button1.individual_addr.area == button1_config["indiv_addr"][0]
    assert button1.individual_addr.line == button1_config["indiv_addr"][1]
    assert button1.individual_addr.device == button1_config["indiv_addr"][2]
    assert button1.status == button1_config["status"]
    # Test correct Dimmer
    dimmer1 = dev.Dimmer("dimmer1", "M-0_D1", system.IndividualAddress(0,0,22), "enabled")
    assert dimmer1.name == dimmer1_config["name"]
    assert dimmer1.refid == dimmer1_config["refid"]
    assert dimmer1.individual_addr.area == dimmer1_config["indiv_addr"][0]
    assert dimmer1.individual_addr.line == dimmer1_config["indiv_addr"][1]
    assert dimmer1.individual_addr.device == dimmer1_config["indiv_addr"][2]
    assert dimmer1.status == dimmer1_config["status"]
    # Test correct LED
    led1 = dev.LED("led1", "M-0_L1", system.IndividualAddress(0,0,1), "enabled") 
    assert led1.name == led1_config["name"]
    assert led1.refid == led1_config["refid"]
    assert led1.max_lumen == led1_config["max_lumen"]
    assert led1.beam_angle == led1_config["beam_angle"]
    assert led1.individual_addr.area == led1_config["indiv_addr"][0]
    assert led1.individual_addr.line == led1_config["indiv_addr"][1]
    assert led1.individual_addr.device == led1_config["indiv_addr"][2]
    assert led1.status == led1_config["status"]
    assert led1.state_ratio == led1_config["state_ratio"]
    assert led1.effective_lumen() == led1_config["effective_lumen"]
    # Test correct Heater
    heater1 = dev.Heater("heater1", "M-0_H1", system.IndividualAddress(0,0,11), "enabled", 400) #400W max power
    assert heater1.name == heater1_config["name"]
    assert heater1.refid == heater1_config["refid"]
    assert heater1.individual_addr.area == heater1_config["indiv_addr"][0]
    assert heater1.individual_addr.line == heater1_config["indiv_addr"][1]
    assert heater1.individual_addr.device == heater1_config["indiv_addr"][2]
    assert heater1.status == heater1_config["status"]
    assert heater1.max_power == heater1_config["max_power"]
    assert heater1.state_ratio == heater1_config["state_ratio"]
    assert heater1.power == heater1_config["power"]
    # Test correct AC
    ac1 = dev.AC("ac1", "M-0_C1", system.IndividualAddress(0,0,12), "enabled", 400)
    assert ac1.name == ac1_config["name"]
    assert ac1.refid == ac1_config["refid"]
    assert ac1.individual_addr.area == ac1_config["indiv_addr"][0]
    assert ac1.individual_addr.line == ac1_config["indiv_addr"][1]
    assert ac1.individual_addr.device == ac1_config["indiv_addr"][2]
    assert ac1.status == ac1_config["status"]
    assert ac1.max_power == ac1_config["max_power"]
    assert ac1.state_ratio == ac1_config["state_ratio"]
    assert ac1.power == ac1_config["power"]
    # Test correct switch
    switch1 = dev.Switch("switch1", "M-0_S3", system.IndividualAddress(0,0,44), "enabled")
    assert switch1.name == switch1_config["name"]
    assert switch1.refid == switch1_config["refid"]
    assert switch1.individual_addr.area == switch1_config["indiv_addr"][0]
    assert switch1.individual_addr.line == switch1_config["indiv_addr"][1]
    assert switch1.individual_addr.device == switch1_config["indiv_addr"][2]
    assert switch1.status == switch1_config["status"]
    # Test correct Brightness sensor
    bright1 = dev.Brightness("brightness1", "M-0_L3", system.IndividualAddress(0,0,5), "enabled")
    assert bright1.name == bright1_config["name"]
    assert bright1.refid == bright1_config["refid"]
    assert bright1.individual_addr.area == bright1_config["indiv_addr"][0]
    assert bright1.individual_addr.line == bright1_config["indiv_addr"][1]
    assert bright1.individual_addr.device == bright1_config["indiv_addr"][2]
    assert bright1.status == bright1_config["status"]
    # Test correct Thermometer
    thermometer1 = dev.Thermometer("thermometer1", "M-0_T1", system.IndividualAddress(0,0,33), "enabled")
    assert thermometer1.name == thermometer1_config["name"]
    assert thermometer1.refid == thermometer1_config["refid"]
    assert thermometer1.individual_addr.area == thermometer1_config["indiv_addr"][0]
    assert thermometer1.individual_addr.line == thermometer1_config["indiv_addr"][1]
    assert thermometer1.individual_addr.device == thermometer1_config["indiv_addr"][2]
    assert thermometer1.status == thermometer1_config["status"]
    # Test correct HumiditySoil
    humiditysoil1 = dev.HumiditySoil("humiditysoil1", "M-0_HU1", system.IndividualAddress(0,0,34), "enabled")
    assert humiditysoil1.name == humidity_config["name"]
    assert humiditysoil1.refid == humidity_config["refid"]
    assert humiditysoil1.individual_addr.area == humidity_config["indiv_addr"][0]
    assert humiditysoil1.individual_addr.line == humidity_config["indiv_addr"][1]
    assert humiditysoil1.individual_addr.device == humidity_config["indiv_addr"][2]
    assert humiditysoil1.status == humidity_config["status"]
    # Test correct CO2Sensor
    co2sensor1 = dev.CO2Sensor("co2sensor1", "M-0_CO2", system.IndividualAddress(0,0,35), "enabled")
    assert co2sensor1.name == co2sensor1_config["name"]
    assert co2sensor1.refid == co2sensor1_config["refid"]
    assert co2sensor1.individual_addr.area == co2sensor1_config["indiv_addr"][0]
    assert co2sensor1.individual_addr.line == co2sensor1_config["indiv_addr"][1]
    assert co2sensor1.individual_addr.device == co2sensor1_config["indiv_addr"][2]
    assert co2sensor1.status == co2sensor1_config["status"]
    # Test correct AirSensor
    airsensor1 = dev.AirSensor("airsensor1", "M-0_A1", system.IndividualAddress(0,0,55), "enabled")
    assert airsensor1.name == airsensor1_config["name"]
    assert airsensor1.refid == airsensor1_config["refid"]
    assert airsensor1.individual_addr.area == airsensor1_config["indiv_addr"][0]
    assert airsensor1.individual_addr.line == airsensor1_config["indiv_addr"][1]
    assert airsensor1.individual_addr.device == airsensor1_config["indiv_addr"][2]
    assert airsensor1.status == airsensor1_config["status"]
    # Test correct PresenceSensor
    presencesensor1 = dev.PresenceSensor("presencesensor1", "M-0_P1", system.IndividualAddress(0,0,66), "enabled")
    assert presencesensor1.name == presencesensor1_config["name"]
    assert presencesensor1.refid == presencesensor1_config["refid"]
    assert presencesensor1.individual_addr.area == presencesensor1_config["indiv_addr"][0]
    assert presencesensor1.individual_addr.line == presencesensor1_config["indiv_addr"][1]
    assert presencesensor1.individual_addr.device == presencesensor1_config["indiv_addr"][2]
    assert presencesensor1.status == presencesensor1_config["status"]


devices_classes = { "Button": dev.Button, "Dimmer": dev.Dimmer , "LED": dev.LED, "Heater":dev.Heater, "AC":dev.AC, "Switch": dev.Switch, "Brightness": dev.Brightness, "Thermometer": dev.Thermometer, "HumiditySoil":dev.HumiditySoil, "CO2Sensor":dev.CO2Sensor, "AirSensor": dev.AirSensor, "PresenceSensor": dev.PresenceSensor}
false_device_names = ["", "device_4*", 420]
wrong_device_names = {  "Button":["BUTTON1", "button 1", "button_1", "switch4"],
                        "Dimmer":["DIMMER1", "dimmer 1", "dimmer_1", "led3"],
                        "LED":["LED1", "led 1", "led_1", "bright4"],
                        "Heater":["HEATER1", "heater 1", "heater_1", "button1"],
                        "AC":["AC1", "ac 1", "ac_1", "led4"],
                        "Switch":["SWITCH1", "switch 1", "switch_1", "ac4"],
                        "Brightness":["BRIGHT1", "bright 1", "bright_1", "heater4"],
                        "Thermometer":["THERMOMETER1", "thermometer 1", "thermometer_1", "bright2"],
                        "HumiditySoil":["HUMIDITYSENSOR1", "humidity sensor 1", "humiditysoil_1", "thermometer1"],
                        "CO2Sensor":["CO2SENSOR1", "co2 sensor 1", "co2sensor_1", "humiditysoil1"],
                        "AirSensor":["AIRSENSOR1", "air sensor 1", "airsensor_1", "thermometer2"],
                        "PresenceSensor":["PRESENCESENSOR1", "presence sensor 1", "presencesensor_1", "button2"]
                        } 
                      
# Test Sys Exit if incorrect device name 
def test_incorrect_device_name():
    for dev_name in false_device_names:
        for dev_class in devices_classes:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](dev_name, "M-0_XX", system.IndividualAddress(1,1,1), "enabled") 
            assert pytest_wrapped_error.type == SystemExit
    for dev_class in wrong_device_names:
        for wrong_name in wrong_device_names[dev_class]:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](wrong_name, "M-0_XX", system.IndividualAddress(1,1,1), "enabled")
            assert pytest_wrapped_error.type == SystemExit

# Test Sys Exit if incorrect refid
false_device_refid = ["", " ", 420]
def test_incorrect_device_refid():
    for dev_refid in false_device_refid:
        for dev_class in devices_classes:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](dev_class.lower(), dev_refid, system.IndividualAddress(1,1,1), "enabled") 
            assert pytest_wrapped_error.type == SystemExit

# Test Sys Exit if incorrect Individual Address
false_indiv_addr = [(-1,0,12), (2.4, 10,10), (0, 20, 200), ('a', 'l0', 20)]
def test_incorrect_device_ia():
    for dev_ia in false_indiv_addr:
        for dev_class in devices_classes:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](dev_class.lower(), "M-0_XX", system.IndividualAddress(dev_ia[0],dev_ia[1],dev_ia[2]), "enabled") 
            assert pytest_wrapped_error.type == SystemExit

# Test Sys Exit if incorrect status
false_status = ["enable", "ok", 420, "disable", "nop", "activated", ""]
def test_incorrect_device_status():
    for status in false_status:
        for dev_class in devices_classes:
            with pytest.raises(SystemExit) as pytest_wrapped_error:
                devices_classes[dev_class](dev_class.lower(), "M-0_XX", system.IndividualAddress(1,1,1), status) 
            assert pytest_wrapped_error.type == SystemExit



## TODO: add an example for each device type

# def test_configure_system_correct():
#     rooms = system.configure_system(speed_factor)
#     assert len(rooms) == 1  ##TODO: change this test if multiple rooms
#     for room in rooms:
#         assert room.__.group_address_style == group_address_style
#         for inroom_device in room.devices:
#             assert inroom_device.device.name in config_devices
#             try:
#                 config_devices.remove(inroom_device.device.name)
#             except ValueError: # if no more items in the list
#                 logging.warning(f"Device {inroom_device.device.name} not in test list")
        
            