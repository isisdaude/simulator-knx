#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system


## Test unit configuration functions (add_device, constructors,...)
speed_factor = 180
group_address_style = '3-levels'
room1_config = {"name":"bedroom1", "dimensions":[20,20,3]}
# Test correct room configuration (constructor call)
def test_correct_room_creation():
    room1 = system.Room("bedroom1", 20, 20, 3, speed_factor, group_address_style)
    assert room1.name == room1_config["name"]
    assert room1.width == room1_config["dimensions"][0]
    assert room1.length == room1_config["dimensions"][1]
    assert room1.height == room1_config["dimensions"][2]
    assert room1.group_address_style == group_address_style

wrong_room_names = ["", "room_4*", 420]
wrong_room_dimensions = [[-1, 20, 3], [10, 0, 0], [5, '5', 'a']]

# Test incorrect room name
def test_incorrect_room_name():
    for wrong_name in wrong_room_names:
        with pytest.raises(SystemExit) as pytest_wrapped_error:
            room1 = system.Room(wrong_name, 20, 20, 3, speed_factor, group_address_style)
        assert pytest_wrapped_error.type == SystemExit

# Test incorrect room dimensions
def test_incorrect_room_dimensions():
    # Test system exit with wrong room dimensions
    for wrong_dimensions in wrong_room_dimensions:
        x, y, z = [wrong_dimensions[d] for d in range(3)]
        with pytest.raises(SystemExit) as pytest_wrapped_error:
            room1 = system.Room("bedroom1", x, y, z, speed_factor, group_address_style)
        assert pytest_wrapped_error.type == SystemExit

# Test incorrect room speed_factor
wrong_room_speed_factors = ['0.99', '0', '-45', '-792.56'] + ['a4', '-056','0x4', '0b1001']
def test_incorrect_room_speed_factor():
    for wrong_speed_factor in wrong_room_speed_factors:
        with pytest.raises(SystemExit) as pytest_wrapped_error:
            room1 = system.Room("bedroom1", 20, 20, 3, wrong_speed_factor, group_address_style)
        assert pytest_wrapped_error.type == SystemExit
        
# Test incorrect room group address style
wrong_room_ga_styles = ['0-levels', '1-levels', '2-level', '2levels', '3level', '4-levels']
def test_incorrect_room_ga_style():
    for wrong_ga_style in wrong_room_ga_styles:
        with pytest.raises(SystemExit) as pytest_wrapped_error:
            room1 = system.Room("bedroom1", 20, 20, 3, speed_factor, wrong_ga_style)
        assert pytest_wrapped_error.type == SystemExit


    # assert pytest_wrapped_error.value.code == 1 # Only if 'exit(1)' called, no code if sys.exit() is called






