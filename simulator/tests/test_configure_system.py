#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import devices as dev

# Creation of the system base (devices + room)
button1 = dev.Button("button1", "M-0_S1", system.IndividualAddress(0,0,20), "enabled")
dimmer1 = dev.Dimmer("dimmer1", "M-0_D1", system.IndividualAddress(0,0,22), "enabled")
led1 = dev.LED("led1", "M-0_L1", system.IndividualAddress(0,0,1), "enabled") #Area 0, Line 0, Device 0
heater1 = dev.Heater("heater1", "M-0_H1", system.IndividualAddress(0,0,11), "enabled", 400) #400W max power
ac1 = dev.AC("ac1", "M-0_C1", system.IndividualAddress(0,0,12), "enabled", 400)
switch1 = dev.Switch("switch1", "M-0_S1", system.IndividualAddress(0,0,44), "enabled")
brightness1 = dev.Brightness("brightness1", "M-0_L3", system.IndividualAddress(0,0,5), "enabled")
thermometer1 = dev.Thermometer("thermometer1", "M-0_T1", system.IndividualAddress(0,0,33), "enabled")
airsensor1 = dev.AirSensor("airsensor1", "M-0_A1", system.IndividualAddress(0,0,55), "enabled")
presencesensor1 = dev.PresenceSensor("presencesensor1", "M-0_A1", system.IndividualAddress(0,0,66), "enabled")

simulation_speed_factor = 180
room1 = system.Room("bedroom1", 12.5, 10, 3, simulation_speed_factor, '3-levels', test_mode=True)
knx_bus = room1.knxbus

ir_button1 = system.InRoomDevice(button1, room1, 0, 0, 1)
ir_dimmer1 = system.InRoomDevice(dimmer1, room1, 0, 0, 2)
ir_led1 = system.InRoomDevice(led1, room1, 0, 1, 1)
ir_heater1 = system.InRoomDevice(heater1, room1, 0, 1, 2)
ir_ac1 = system.InRoomDevice(ac1, room1, 0, 1, 3)
ir_switch1 = system.InRoomDevice(switch1, room1, 0, 1, 4)
ir_brightness1 = system.InRoomDevice(brightness1, room1, 1, 1, 1)
ir_thermometer1 = system.InRoomDevice(thermometer1, room1, 1, 1, 2)
ir_airsensor1 = system.InRoomDevice(airsensor1, room1, 1, 1, 3)
ir_presencesensor1 = system.InRoomDevice(presencesensor1, room1, 1, 1, 4)

devices = [button1, dimmer1, led1, heater1, ac1, switch1, brightness1, thermometer1, airsensor1, presencesensor1]
ir_devices = [ir_button1, ir_dimmer1, ir_led1, ir_heater1, ir_ac1, ir_switch1, ir_brightness1, ir_thermometer1, ir_airsensor1, ir_presencesensor1]
devices_name = ["button1", "dimmer1", "led1", "heater1", "ac1", "switch1", "brightness1", "thermometer1", "airsensor1", "presencesensor1"]
devices_class = [dev.Button, dev.Dimmer, dev.LED, dev.Heater, dev.AC, dev.Switch, dev.Brightness, dev.Thermometer, dev.AirSensor, dev.PresenceSensor]
devices_loc = [(0, 0, 1), (0, 0, 2), (0, 1, 1), (0, 1, 2), (0, 1, 3), (0, 1, 4), (1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 1, 4)]

def test_correct_device_addition():
    room1 = system.Room("bedroom1", 12.5, 10, 3, simulation_speed_factor, '3-levels', test_mode=True)
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        # Test the the in_room_device has been created and added to room's device list
        assert ir_devices[d] in room1.devices
        assert isinstance(room1.devices[room1.devices.index(ir_devices[d])].device, devices_class[d])
        # Test addition to ambient list for each device type
        if isinstance(devices[d], dev.Actuator):
            if isinstance(devices[d], dev.LightActuator):
                assert ir_devices[d] in room1.world.ambient_light.light_sources
            elif isinstance(devices[d], dev.TemperatureActuator):
                assert ir_devices[d] in room1.world.ambient_temperature.temp_sources
        elif isinstance(devices[d], dev.Sensor):
            if isinstance(devices[d], dev.Brightness):
                assert ir_devices[d] in room1.world.ambient_light.light_sensors
            elif isinstance(devices[d], dev.Thermometer):
                assert ir_devices[d] in room1.world.ambient_temperature.temp_sensors
            elif isinstance(devices[d], dev.AirSensor):
                assert ir_devices[d] in room1.world.ambient_temperature.temp_sensors
                assert ir_devices[d] in room1.world.ambient_humidity.humidity_sensors
                assert ir_devices[d] in room1.world.ambient_co2.co2_sensors
        # Test storage of the bus in functional devices class's attributes 
        elif isinstance(devices[d], dev.FunctionalModule):
            assert hasattr(devices[d], 'knxbus')
            assert room1.knxbus == devices[d].knxbus
        
## TODO test world creation first

ga1 = system.GroupAddress('3-levels', main=1, middle=1, sub=1)
# ga1_bus = system.GroupAddressBus(ga1)
ga1_bus = None
ga1_str = '1/1/1'
def test_correct_attachement_to_bus():
    room1 = system.Room("bedroom1", 12.5, 10, 3, simulation_speed_factor, '3-levels', test_mode=True)
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        room1.attach(devices[d], ga1_str)
        assert ga1 in room1.knxbus.group_addresses
        assert ga1 in devices[d].group_addresses
        for ga_bus in room1.knxbus.ga_buses:
            if ga_bus.group_address == ga1:
                ga1_bus = ga_bus
        if ga1_bus is None:
            assert False
        ga_bus_index = room1.knxbus.ga_buses.index(ga1_bus)
        assert ga1 == room1.knxbus.ga_buses[ga_bus_index].group_address
        if isinstance(devices[d], dev.Actuator):
            assert devices[d] in room1.knxbus.ga_buses[ga_bus_index].actuators
        if isinstance(devices[d], dev.FunctionalModule):
            assert devices[d] in room1.knxbus.ga_buses[ga_bus_index].functional_modules
        if isinstance(devices[d], dev.Sensor):
            assert devices[d] in room1.knxbus.ga_buses[ga_bus_index].sensors

ga2 = system.GroupAddress('3-levels', main=2, middle=2, sub=2)
# ga2_bus = system.GroupAddressBus(ga2)
ga2_bus = None
ga2_str = '2/2/2'
led22 = dev.LED("led22", "M-0_L22", system.IndividualAddress(2,2,2), "enabled") #Area 0, Line 0, Device 0
def test_correct_detachement_from_bus():
    room1 = system.Room("bedroom1", 12.5, 10, 3, simulation_speed_factor, '3-levels', test_mode=True)
    room1.add_device(led22, 2, 2, 2)
    # We attaxch a first device
    room1.attach(led22, ga2_str) 
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        # We attach a second device
        room1.attach(devices[d], ga2_str)
        for ga_bus in room1.knxbus.ga_buses:
            if ga_bus.group_address == ga2:
                ga2_bus = ga_bus
        if ga2_bus is None:
            assert False
        ga_bus_index = room1.knxbus.ga_buses.index(ga2_bus)
        # Test detachement (attachement is correct because of the previous test)
        room1.detach(devices[d], ga2_str)
        assert ga2 not in devices[d].group_addresses
        if isinstance(devices[d], dev.Actuator):
            assert devices[d] not in room1.knxbus.ga_buses[ga_bus_index].actuators
        if isinstance(devices[d], dev.FunctionalModule):
            assert devices[d] not in room1.knxbus.ga_buses[ga_bus_index].functional_modules
        if isinstance(devices[d], dev.Sensor):
            assert devices[d] not in room1.knxbus.ga_buses[ga_bus_index].sensors
    # Test removal of ga_bus if no device connected to it
    room1.detach(led22, ga2_str)
    assert ga2 not in led22.group_addresses
    assert ga2 not in room1.knxbus.group_addresses
    assert ga2_bus not in room1.knxbus.ga_buses


# TODO: test wrong config files, test good/wrong attachement to bus, detachement





