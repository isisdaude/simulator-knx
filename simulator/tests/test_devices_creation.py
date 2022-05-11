#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import devices as dev


# Test configuration of system in developper case 
devices_config = ['led1', 'led2', 'button1', 'bright1', 'heater1']
led1_config = {"name":"led1", "refid":"M-0_L1", "indiv_addr":[0,0,1], "status":"enabled", "location":[5,5,1], "group_addresses":['1/1/1']}
button1_config = {"name":"button1", "refid":"M-0_S1", "indiv_addr":[0,0,20], "status":"enabled", "location":[0,0,1], "group_addresses":['1/1/1']}
bright1_config = {"name":"brightness1", "refid":"M-0_L3", "indiv_addr":[0,0,5], "status":"enabled", "location":[20,20,1], "group_addresses":[]}
heater1_config = {"name":"heater1", "refid":"M-0_H1", "indiv_addr":[0,0,11], "status":"enabled", "max_power":400, "location":[20,20,1], "group_addresses":[]}
ac1_config = {"name":"ac1", "refid":"M-0_C1", "indiv_addr":[0,0,12], "status":"enabled", "max_power":400, "location":[20,20,1], "group_addresses":[]}
#heater = 
#cooler = 

def test_correct_devices_creation():
    # Test correct LED
    led1 = dev.LED("led1", "M-0_L1", system.IndividualAddress(0,0,1), "enabled") 
    assert led1.name == led1_config["name"]
    assert led1.refid == led1_config["refid"]
    assert led1.individual_addr.area == led1_config["indiv_addr"][0]
    assert led1.individual_addr.line == led1_config["indiv_addr"][1]
    assert led1.individual_addr.device == led1_config["indiv_addr"][2]
    assert led1.status == led1_config["status"]
    # Test correct Button
    button1 = dev.Button("button1", "M-0_S1", system.IndividualAddress(0,0,20), "enabled")
    assert button1.name == button1_config["name"]
    assert button1.refid == button1_config["refid"]
    assert button1.individual_addr.area == button1_config["indiv_addr"][0]
    assert button1.individual_addr.line == button1_config["indiv_addr"][1]
    assert button1.individual_addr.device == button1_config["indiv_addr"][2]
    assert button1.status == button1_config["status"]
    # Test correct Brightness sensor
    bright1 = dev.Brightness("brightness1", "M-0_L3", system.IndividualAddress(0,0,5), "enabled")
    assert bright1.name == bright1_config["name"]
    assert bright1.refid == bright1_config["refid"]
    assert bright1.individual_addr.area == bright1_config["indiv_addr"][0]
    assert bright1.individual_addr.line == bright1_config["indiv_addr"][1]
    assert bright1.individual_addr.device == bright1_config["indiv_addr"][2]
    assert bright1.status == bright1_config["status"]
    # Test correct Heater
    heater1 = dev.Heater("heater1", "M-0_H1", system.IndividualAddress(0,0,11), "enabled", 400) #400W max power
    assert heater1.name == heater1_config["name"]
    assert heater1.refid == heater1_config["refid"]
    assert heater1.individual_addr.area == heater1_config["indiv_addr"][0]
    assert heater1.individual_addr.line == heater1_config["indiv_addr"][1]
    assert heater1.individual_addr.device == heater1_config["indiv_addr"][2]
    assert heater1.status == heater1_config["status"]
    assert heater1.max_power == heater1_config["max_power"]
    # Test correct AC
    ac1 = dev.AC("ac1", "M-0_C1", system.IndividualAddress(0,0,12), "enabled", 400)
    assert ac1.name == ac1_config["name"]
    assert ac1.refid == ac1_config["refid"]
    assert ac1.individual_addr.area == ac1_config["indiv_addr"][0]
    assert ac1.individual_addr.line == ac1_config["indiv_addr"][1]
    assert ac1.individual_addr.device == ac1_config["indiv_addr"][2]
    assert ac1.status == ac1_config["status"]
    assert ac1.max_power == ac1_config["max_power"]
    ## TODO: add devices

## TODO: add devices
devices_classes = { "LED": dev.LED, "Button": dev.Button, "Brightness": dev.Brightness, "Heater":dev.Heater, "AC":dev.AC}
false_device_names = ["", "device_4*", 420]
## TODO: add devices
wrong_device_names = {  "LED":["LED1", "led 1", "led_1", "bright4"],
                        "Button":["BUTTON1", "button 1", "button_1", "switch4"],
                        "Brightness":["BRIGHT1", "bright 1", "bright_1", "heater4"],
                        "Heater":["HEATER1", "heater 1", "heater_1", "button1"],
                        "AC":["AC1", "ac 1", "ac_1", "led4"]} 
                      
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
#         assert room.group_address_style == group_address_style
#         for inroom_device in room.devices:
#             assert inroom_device.device.name in config_devices
#             try:
#                 config_devices.remove(inroom_device.device.name)
#             except ValueError: # if no more items in the list
#                 logging.warning(f"Device {inroom_device.device.name} not in test list")
        
            