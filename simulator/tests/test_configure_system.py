import pytest
import logging

import system


# Test the speed factor given by user
speed_factor_correct = ['1', ' 1 ', '50', '180', '300.67', '004']
speed_factor_correct_verif = [1.0, 1.0, 50.0, 180.0, 300.67, 4.0]
speed_factor_wrong = ['0.99', '0', '-45', '-792.56']
speed_factor_false = ['a4', '-056','0x4', '0b1001']

def test_correct_speed_factor():
    for s in range(len(speed_factor_correct)):
        assert system.check_simulation_speed_factor(speed_factor_correct[s]) == speed_factor_correct_verif[s]
    
def test_incorrect_speed_factor():
    for wrong_factor in speed_factor_wrong:
        assert system.check_simulation_speed_factor(wrong_factor) == None
    for false_factor in speed_factor_false:
        assert system.check_simulation_speed_factor(false_factor) == None


## Test unit configuration functions (add_device, constructors,...)
speed_factor = 180
group_address_style = '3-levels'
room1_config = {"name":"bedroom1", "dimensions":[20,20,3]}
# Test room configuration (constructor call)
def test_correct_room_config():
    room1 = system.Room("bedroom1", 20, 20, 3, speed_factor, group_address_style)
    assert room1.name == room1_config["name"]
    assert room1.width == room1_config["dimensions"][0]
    assert room1.length == room1_config["dimensions"][1]
    assert room1.height == room1_config["dimensions"][2]
    assert room1.group_address_style == group_address_style

wrong_dimensions = [[-1, 20, 3], [10, 0, 0], [5, '5', 'a']]

def test_incorrect_room_config():
    # Test system exit if empty name
    with pytest.raises(SystemExit) as pytest_wrapped_error:
        room1 = system.Room("", 20, 20, 3, speed_factor, group_address_style)
    assert pytest_wrapped_error.type == SystemExit
    # Test system exit if non alphanumeric char name
    with pytest.raises(SystemExit) as pytest_wrapped_error:
        room1 = system.Room("room_4*", 20, 20, 3, speed_factor, group_address_style)
    assert pytest_wrapped_error.type == SystemExit

    +


    # assert pytest_wrapped_error.value.code == 1 # Only if 'exit(1)' called, no code if sys.exit() is called


# def test_wrong_room_config():


# assert list(led1.location.pos) == led1_config["location"]

# Test configuration of system in developper case 
devices_config = ['led1', 'led2', 'switch1', 'switch2', 'bright1']
led1_config = {"name":"led1", "refid":"M-0_L1", "indiv_addr":[0,0,1], "status":"enabled", "location":[5,5,1], "group_addresses":['1/1/1']}
switch1_config = {"name":"switch1", "refid":"M-0_B1", "indiv_addr":[0,0,20], "status":"enabled", "location":[0,0,1], "group_addresses":['1/1/1']}
bright1_config = {"name":"bright1", "refid":"M-0_L3", "indiv_addr":[0,0,5], "status":"enabled", "location":[20,20,1], "group_addresses":[]}
#heater = 
#cooler = 

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
        
            



