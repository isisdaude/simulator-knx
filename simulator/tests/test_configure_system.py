#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import devices as dev

# Creation of the system base (devices + room)
led1 = dev.LED("led1", "M-0_L1", system.IndividualAddress(0,0,1), "enabled") #Area 0, Line 0, Device 0
switch1 = dev.Switch("switch1", "M-0_S1", system.IndividualAddress(0,0,20), "enabled")
brightness1 = dev.Brightness("brightness1", "M-0_L3", system.IndividualAddress(0,0,5), "enabled")
simulation_speed_factor = 180
room1 = system.Room("bedroom1", 20, 20, 3, simulation_speed_factor, '3-levels')

ir_led1 = system.InRoomDevice(led1, room1, 5, 5, 1)
ir_switch1 = system.InRoomDevice(switch1, room1, 0, 0, 1)
ir_bright1 = system.InRoomDevice(brightness1, room1, 20, 20, 1)
## TODO: add devices
devices = [led1, switch1, brightness1]
ir_devices = [ir_led1, ir_switch1, ir_bright1]
devices_name = ["led1", "switch1", "brightness1"]
devices_loc = [[5, 5, 1], [0, 0, 1], [20, 20, 1]]

def test_correct_device_addition():
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        # Test that there is no unit issue (indiv addr,...)
        room1.add_device(devices[d], x, y, z)
        # Test the the in_room_device has been created and added to room's device list
        assert ir_devices[d] in room1.devices
        # Test if name of device is the same as name of in_room_device object
        assert room1.devices[room1.devices.index(ir_devices[d])].name == devices_name[d]


# test addition to ambient list for each device
# test





