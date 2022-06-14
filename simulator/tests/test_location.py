""" Test Location object creation"""
import pytest
import logging

import system
import devices as dev


simulation_speed_factor = 180
led1 = dev.LED("led1", system.IndividualAddress(0, 0, 1))

correct_locations = [[0, 0, 0], [12.5, 10, 3], [2, 6, 1.5]]
# Out-of-bounds locations, supposed to be replaced in the room's bounds
wrong_locations = [[0, 0, -1], [120, 10, 3], [2.4, -128, 55]]
wrong_locations_expected = [[0, 0, 0], [12.5, 10, 3], [2.4, 0, 3]]
# False location, we expect a sys exit
false_locations = [[2, "six", 1.5], ["0x12", None, 2], [10, 10, ""]]


def test_correct_location():
    # Creation of Location object and placement of devices in room
    for loc in correct_locations:
        room1 = system.Room(
            "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
        )
        loc_object = system.Location(room1, loc[0], loc[1], loc[2])
        # Assert good creation of location object
        assert list(loc_object.pos) == loc
        room1.add_device(led1, loc[0], loc[1], loc[2])
        for ir_device in room1.devices:
            if ir_device.name == led1.name:
                assert ir_device.location.pos is not None
                assert ir_device.location.pos == loc_object.pos
    # Update of the location
    room1 = system.Room(
        "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
    )
    room1.add_device(led1, 1, 1, 1)
    for loc in correct_locations:
        loc_object = system.Location(room1, loc[0], loc[1], loc[2])
        for ir_device in room1.devices:
            if ir_device.name == led1.name:
                ir_device.update_location(new_x=loc[0], new_y=loc[1], new_z=loc[2])
                assert ir_device.location.pos is not None
                assert ir_device.location.pos == loc_object.pos


def test_wrong_location():
    # Creation of Location object and wrong placement of devices in room
    for l in range(len(wrong_locations)):
        wrong_loc = wrong_locations[l]
        expected_loc = wrong_locations_expected[l]
        room1 = system.Room(
            "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
        )
        wrong_loc_object = system.Location(
            room1, wrong_loc[0], wrong_loc[1], wrong_loc[2]
        )
        expected_loc_object = system.Location(
            room1, expected_loc[0], expected_loc[1], expected_loc[2]
        )
        # Assert wrong Location object is replaced inside the room
        assert wrong_loc_object.pos == expected_loc_object.pos
        # Assert addition of the device to the room was done after replacement nside the room
        room1.add_device(led1, wrong_loc[0], wrong_loc[1], wrong_loc[2])
        for ir_device in room1.devices:
            if ir_device.name == led1.name:
                assert ir_device.location.pos == expected_loc_object.pos

    # Update with a wrong location
    room1 = system.Room(
        "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
    )
    room1.add_device(led1, 1, 1, 1)
    for l in range(len(wrong_locations)):
        wrong_loc = wrong_locations[l]
        expected_loc = wrong_locations_expected[l]
        expected_loc_object = system.Location(
            room1, expected_loc[0], expected_loc[1], expected_loc[2]
        )
        for ir_device in room1.devices:
            if ir_device.name == led1.name:
                ir_device.update_location(
                    new_x=wrong_loc[0], new_y=wrong_loc[1], new_z=wrong_loc[2]
                )
                assert ir_device.location.pos == expected_loc_object.pos


def test_false_location():
    # Creation of Location object and placement of devices in room
    for false_loc in false_locations:
        room1 = system.Room(
            "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
        )
        with pytest.raises(SystemExit) as pytest_wrapped_error:
            false_loc_object = system.Location(
                room1, false_loc[0], false_loc[1], false_loc[2]
            )
        assert pytest_wrapped_error.type == SystemExit
        with pytest.raises(SystemExit) as pytest_wrapped_error:
            room1.add_device(led1, false_loc[0], false_loc[1], false_loc[2])
        assert pytest_wrapped_error.type == SystemExit
    # Update with a false location
    room1 = system.Room(
        "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
    )
    room1.add_device(led1, 1, 1, 1)
    for false_loc in false_locations:
        for ir_device in room1.devices:
            if ir_device.name == led1.name:
                with pytest.raises(SystemExit) as pytest_wrapped_error:
                    ir_device.update_location(
                        new_x=false_loc[0], new_y=false_loc[1], new_z=false_loc[2]
                    )
                assert pytest_wrapped_error.type == SystemExit
