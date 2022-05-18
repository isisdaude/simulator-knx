#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import devices as dev

# Creation of the system base (devices + room)
led1 = dev.LED("led1", "M-0_L1", system.IndividualAddress(0,0,1), "enabled") #Area 0, Line 0, Device 0
button1 = dev.Button("button1", "M-0_S1", system.IndividualAddress(0,0,20), "enabled")
brightness1 = dev.Brightness("brightness1", "M-0_L3", system.IndividualAddress(0,0,5), "enabled")
simulation_speed_factor = 180
room1 = system.Room("bedroom1", 12.5, 10, 3, simulation_speed_factor, '3-levels')

ir_led1 = system.InRoomDevice(led1, room1, 2.5, 2.5, 1)
ir_button1 = system.InRoomDevice(button1, room1, 0, 0, 1)
ir_bright1 = system.InRoomDevice(brightness1, room1, 12.5, 10, 1)
## TODO: add devices
devices = [led1, button1, brightness1]
ir_devices = [ir_led1, ir_button1, ir_bright1]
devices_name = ["led1", "button1", "brightness1"]
devices_class = [dev.LightActuator, dev.Button, dev.Brightness]
devices_loc = [(5, 5, 1), (0, 0, 1), (20, 20, 1)]

def test_correct_device_addition():
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        # Test the the in_room_device has been created and added to room's device list
        assert ir_devices[d] in room1.devices
        # Test if name of device is the same as name of in_room_device object
        assert room1.devices[room1.devices.index(ir_devices[d])].name == devices_name[d]
        # Test if loc is correct
        assert room1.devices[room1.devices.index(ir_devices[d])].location.pos == devices_loc[d]
        
# test addition to ambient list for each device
    # for functional module: test if bus is added to the device object
## must test world creation first


def test_correct_attachement_to_bus():
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)

    



# test good attach to bus





