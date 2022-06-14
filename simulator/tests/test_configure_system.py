""" Test of system configuration, using functions or JSON config file"""
import pytest
import logging

import system
import devices as dev

# Creation of the system base (devices + room)
button1 = dev.Button("button1", system.IndividualAddress(0, 0, 20))
dimmer1 = dev.Dimmer("dimmer1", system.IndividualAddress(0, 0, 22))
led1 = dev.LED("led1", system.IndividualAddress(0, 0, 1))  # Area 0, Line 0, Device 0
heater1 = dev.Heater(
    "heater1", system.IndividualAddress(0, 0, 11), 400
)  # 400W max power
ac1 = dev.AC("ac1", system.IndividualAddress(0, 0, 12), 400)
switch1 = dev.Switch("switch1", system.IndividualAddress(0, 0, 44))
brightness1 = dev.Brightness("brightness1", system.IndividualAddress(0, 0, 5))
thermometer1 = dev.Thermometer("thermometer1", system.IndividualAddress(0, 0, 33))
humiditysoil1 = dev.HumiditySoil("humiditysoil1", system.IndividualAddress(0, 0, 34))
co2sensor1 = dev.CO2Sensor("co2sensor1", system.IndividualAddress(0, 0, 35))
airsensor1 = dev.AirSensor("airsensor1", system.IndividualAddress(0, 0, 55))
presencesensor1 = dev.PresenceSensor(
    "presencesensor1", system.IndividualAddress(0, 0, 66)
)

simulation_speed_factor = 180
system_dt = 1
room1 = system.Room(
    "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
)
knx_bus = room1.knxbus

ir_button1 = system.InRoomDevice(button1, room1, 0.5, 3.1, 1.0)
ir_dimmer1 = system.InRoomDevice(dimmer1, room1, 0.525, 7.6375, 1.0)
ir_led1 = system.InRoomDevice(led1, room1, 5.7125, 7.5875, 1.0)
ir_heater1 = system.InRoomDevice(heater1, room1, 1.5625, 3.0375, 1.0)
ir_ac1 = system.InRoomDevice(ac1, room1, 0, 1, 3)
ir_switch1 = system.InRoomDevice(switch1, room1, 4.1625, 1.5375, 1.0)
ir_brightness1 = system.InRoomDevice(brightness1, room1, 11.6625, 5.8, 1.0)
ir_thermometer1 = system.InRoomDevice(thermometer1, room1, 1, 1, 2)
ir_humiditysoil1 = system.InRoomDevice(humiditysoil1, room1, 7.25, 1.1875, 1.0)
ir_co2sensor1 = system.InRoomDevice(co2sensor1, room1, 1, 2, 0)
ir_airsensor1 = system.InRoomDevice(airsensor1, room1, 0.5375, 5.5, 1.0)
ir_presencesensor1 = system.InRoomDevice(presencesensor1, room1, 5.8375, 4.1, 1.0)

devices = [
    button1,
    dimmer1,
    led1,
    heater1,
    ac1,
    switch1,
    brightness1,
    thermometer1,
    humiditysoil1,
    co2sensor1,
    airsensor1,
    presencesensor1,
]
ir_devices = [
    ir_button1,
    ir_dimmer1,
    ir_led1,
    ir_heater1,
    ir_ac1,
    ir_switch1,
    ir_brightness1,
    ir_thermometer1,
    ir_humiditysoil1,
    ir_co2sensor1,
    ir_airsensor1,
    ir_presencesensor1,
]
devices_name = [
    "button1",
    "dimmer1",
    "led1",
    "heater1",
    "ac1",
    "switch1",
    "brightness1",
    "thermometer1",
    "humiditysoil1",
    "co2sensor1",
    "airsensor1",
    "presencesensor1",
]
devices_class = [
    dev.Button,
    dev.Dimmer,
    dev.LED,
    dev.Heater,
    dev.AC,
    dev.Switch,
    dev.Brightness,
    dev.Thermometer,
    dev.HumiditySoil,
    dev.CO2Sensor,
    dev.AirSensor,
    dev.PresenceSensor,
]
devices_loc = [
    (0.5, 3.1, 1.0),
    (0.525, 7.6375, 1.0),
    (5.7125, 7.5875, 1.0),
    (1.5625, 3.0375, 1.0),
    (0, 1, 3),
    (4.1625, 1.5375, 1.0),
    (11.6625, 5.8, 1.0),
    (1, 1, 2),
    (7.25, 1.1875, 1.0),
    (1, 2, 0),
    (0.5375, 5.5, 1.0),
    (5.8375, 4.1, 1.0),
]


def test_correct_device_addition():
    room1 = system.Room(
        "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
    )
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        # Test the the in_room_device has been created and added to room's device list
        assert ir_devices[d] in room1.devices
        assert isinstance(
            room1.devices[room1.devices.index(ir_devices[d])].device, devices_class[d]
        )
        # Test addition to ambient list for each device type
        if isinstance(devices[d], dev.Actuator):
            if isinstance(devices[d], dev.LightActuator):
                assert (
                    ir_devices[d]
                    in room1.world.ambient_light._AmbientLight__light_sources
                )
            elif isinstance(devices[d], dev.TemperatureActuator):
                assert (
                    ir_devices[d]
                    in room1.world.ambient_temperature._AmbientTemperature__temp_sources
                )
        elif isinstance(devices[d], dev.Sensor):
            if isinstance(devices[d], dev.Brightness):
                assert (
                    ir_devices[d]
                    in room1.world.ambient_light._AmbientLight__light_sensors
                )
            elif isinstance(devices[d], dev.Thermometer):
                assert (
                    ir_devices[d]
                    in room1.world.ambient_temperature._AmbientTemperature__temp_sensors
                )
            elif isinstance(devices[d], dev.HumidityAir):
                assert devices[d].humidity == room1.world.ambient_humidity.humidity_out
            ### TODO humidity soil sensor
            ### TODO presence sensor
            elif isinstance(devices[d], dev.CO2Sensor):
                assert ir_devices[d] in room1.world.ambient_co2._AmbientCO2__co2_sensors
            elif isinstance(devices[d], dev.AirSensor):
                assert (
                    ir_devices[d]
                    in room1.world.ambient_temperature._AmbientTemperature__temp_sensors
                )
                assert (
                    ir_devices[d]
                    in room1.world.ambient_humidity._AmbientHumidity__humidity_sensors
                )
                assert ir_devices[d] in room1.world.ambient_co2._AmbientCO2__co2_sensors
        # Test storage of the bus in functional devices class's attributes
        elif isinstance(devices[d], dev.FunctionalModule):
            assert hasattr(devices[d], "knxbus")
            assert room1.knxbus == devices[d].knxbus


ga1 = system.GroupAddress("3-levels", main=1, middle=1, sub=1)
ga1_bus = None
ga1_str = "1/1/1"


def test_correct_attachement_to_bus():
    room1 = system.Room(
        "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
    )
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        room1.attach(devices[d], ga1_str)
        assert ga1 in room1.knxbus.group_addresses
        assert ga1 in devices[d].group_addresses
        for ga_bus in room1.knxbus._KNXBus__ga_buses:
            if ga_bus.group_address == ga1:
                ga1_bus = ga_bus
        if ga1_bus is None:
            assert False
        ga_bus_index = room1.knxbus._KNXBus__ga_buses.index(ga1_bus)
        assert ga1 == room1.knxbus._KNXBus__ga_buses[ga_bus_index].group_address
        if isinstance(devices[d], dev.Actuator):
            assert devices[d] in room1.knxbus._KNXBus__ga_buses[ga_bus_index].actuators
        if isinstance(devices[d], dev.FunctionalModule):
            assert (
                devices[d]
                in room1.knxbus._KNXBus__ga_buses[ga_bus_index].functional_modules
            )
        if isinstance(devices[d], dev.Sensor):
            assert devices[d] in room1.knxbus._KNXBus__ga_buses[ga_bus_index].sensors


ga2 = system.GroupAddress("3-levels", main=2, middle=2, sub=2)
ga2_bus = None
ga2_str = "2/2/2"
led22 = dev.LED("led22", system.IndividualAddress(2, 2, 2))  # Area 0, Line 0, Device 0


def test_correct_detachement_from_bus():
    room1 = system.Room(
        "bedroom1", 12.5, 10, 3, simulation_speed_factor, "3-levels", test_mode=True
    )
    room1.add_device(led22, 2, 2, 2)
    # We attaxch a first device
    room1.attach(led22, ga2_str)
    for d in range(len(devices)):
        x, y, z = devices_loc[d]
        room1.add_device(devices[d], x, y, z)
        # We attach a second device
        room1.attach(devices[d], ga2_str)
        for ga_bus in room1.knxbus._KNXBus__ga_buses:
            if ga_bus.group_address == ga2:
                ga2_bus = ga_bus
        if ga2_bus is None:
            assert False
        ga_bus_index = room1.knxbus._KNXBus__ga_buses.index(ga2_bus)
        # Test detachement (attachement is correct because of the previous test)
        room1.detach(devices[d], ga2_str)
        assert ga2 not in devices[d].group_addresses
        if isinstance(devices[d], dev.Actuator):
            assert (
                devices[d] not in room1.knxbus._KNXBus__ga_buses[ga_bus_index].actuators
            )
        if isinstance(devices[d], dev.FunctionalModule):
            assert (
                devices[d]
                not in room1.knxbus._KNXBus__ga_buses[ga_bus_index].functional_modules
            )
        if isinstance(devices[d], dev.Sensor):
            assert (
                devices[d] not in room1.knxbus._KNXBus__ga_buses[ga_bus_index].sensors
            )
    # Test removal of ga_bus if no device connected to it
    room1.detach(led22, ga2_str)
    assert ga2 not in led22.group_addresses
    assert ga2 not in room1.knxbus.group_addresses
    assert ga2_bus not in room1.knxbus._KNXBus__ga_buses


def test_correct_window_creation_addition():
    window1_config = {
        "name": "window1",
        "room": room1,
        "wall": "north",
        "loc_offset": 4,
        "size": [2, 1],
        "win_loc": (4, 10, 1.5),
    }
    window1 = system.Window("window1", room1, "north", 4, [2, 1], test_mode=True)
    assert window1.name == window1_config["name"]
    assert window1.wall == window1_config["wall"]
    assert window1.location_offset == window1_config["loc_offset"]
    assert window1.window_loc == window1_config["win_loc"]
    assert window1.size == window1_config["size"]
    window1.max_lumen_from_out_lux(1000)
    assert window1.max_lumen == 2000
    assert window1.effective_lumen() == 2000

    window2_config = {
        "name": "window2",
        "room": room1,
        "wall": "east",
        "loc_offset": 4,
        "size": [2, 1],
        "win_loc": (12.5, 4, 1.5),
    }
    window2 = system.Window("window2", room1, "east", 4, [2, 1], test_mode=True)
    assert window2.name == window2_config["name"]
    assert window2.wall == window2_config["wall"]
    assert window2.location_offset == window2_config["loc_offset"]
    assert window2.window_loc == window2_config["win_loc"]
    assert window2.size == window2_config["size"]

    room1.add_window(window1)
    ir_window1 = system.InRoomDevice(window1, room1, 4, 10, 1.5)
    assert ir_window1 in room1.windows
    assert ir_window1 in room1.world.ambient_light._AmbientLight__windows


def test_correct_update_loc():
    ir_button1.update_location(new_x=2, new_y=3, new_z=1.5)
    assert ir_button1.location.pos == (2, 3, 1.5)


from tools import configure_system, configure_system_from_file


def test_configure_system():
    room_conf, system_dt_conf = configure_system(
        simulation_speed_factor, system_dt, test_mode=True
    )
    # Check Room config
    assert isinstance(room_conf, system.Room)
    assert system_dt_conf == system_dt
    assert room_conf._Room__system_dt == system_dt
    assert room_conf._Room__speed_factor == simulation_speed_factor
    # other assertions could be made on corect devices and group addresses implemented, but it would change if a future dev changes the configuration function,
    # and the test is simply to show that configuration works and does not fail with correct values


devices_conf = [
    button1,
    dimmer1,
    led1,
    heater1,
    switch1,
    brightness1,
    humiditysoil1,
    airsensor1,
    presencesensor1,
]
devices_name_conf = [
    "button1",
    "dimmer1",
    "led1",
    "heater1",
    "switch1",
    "brightness1",
    "humiditysoil1",
    "airsensor1",
    "presencesensor1",
]
devices_class_conf = [
    dev.Button,
    dev.Dimmer,
    dev.LED,
    dev.Heater,
    dev.Switch,
    dev.Brightness,
    dev.HumiditySoil,
    dev.AirSensor,
    dev.PresenceSensor,
]
devices_loc_conf = [
    (0.5, 3.1, 1.0),
    (0.525, 7.6375, 1.0),
    (5.7125, 7.5875, 1.0),
    (1.5625, 3.0375, 1.0),
    (4.1625, 1.5375, 1.0),
    (11.6625, 5.8, 1.0),
    (7.25, 1.1875, 1.0),
    (0.5375, 5.5, 1.0),
    (5.8375, 4.1, 1.0),
]
group_addresses = {"1/1/1": [button1, heater1], "1/1/2": [dimmer1, led1]}
world_states = {
    "temp_out": 20.0,
    "temp_in": 25.0,
    "hum_out": 50.0,
    "hum_in": 35.0,
    "co2_out": 300.0,
    "co2_in": 800.0,
    "datetime": "today",
    "weather": "clear",
    "room_insulation": "average",
}


def test_configure_system_from_file():
    config_path = "config/config_test_config.json"
    # devices: brightness1, airsensor1, button1, heater1, dimmer1, led1
    room_conf, system_dt_conf = configure_system_from_file(
        config_path, system_dt, test_mode=True
    )
    window1 = system.Window("window1", room_conf, "north", 4, (2, 1), test_mode=True)
    assert isinstance(room_conf, system.Room)
    assert system_dt_conf == system_dt
    assert room_conf._Room__system_dt == system_dt
    assert room_conf._Room__speed_factor == simulation_speed_factor

    # Check correct devices, with correct locations
    ir_button1_conf = system.InRoomDevice(button1, room_conf, 0.5, 3.1, 1.0)
    ir_dimmer1_conf = system.InRoomDevice(dimmer1, room_conf, 0.525, 7.6375, 1.0)
    ir_led1_conf = system.InRoomDevice(led1, room_conf, 5.7125, 7.5875, 1.0)
    ir_heater1_conf = system.InRoomDevice(heater1, room_conf, 1.5625, 3.0375, 1.0)
    ir_switch1_conf = system.InRoomDevice(switch1, room_conf, 4.1625, 1.5375, 1.0)
    ir_brightness1_conf = system.InRoomDevice(brightness1, room_conf, 11.6625, 5.8, 1.0)
    ir_humiditysoil1_conf = system.InRoomDevice(
        humiditysoil1, room_conf, 7.25, 1.1875, 1.0
    )
    ir_airsensor1_conf = system.InRoomDevice(airsensor1, room_conf, 0.5375, 5.5, 1.0)
    ir_presencesensor1_conf = system.InRoomDevice(
        presencesensor1, room_conf, 5.8375, 4.1, 1.0
    )
    ir_devices_conf = [
        ir_button1_conf,
        ir_dimmer1_conf,
        ir_led1_conf,
        ir_heater1_conf,
        ir_switch1_conf,
        ir_brightness1_conf,
        ir_humiditysoil1_conf,
        ir_airsensor1_conf,
        ir_presencesensor1_conf,
    ]
    index = 0
    for ir_device in ir_devices_conf:
        assert ir_device in room_conf.devices
        ir_device_room = room_conf.devices[room_conf.devices.index(ir_device)]
        assert isinstance(ir_device_room.device, devices_class_conf[index])
        assert (
            ir_device_room.name
            == ir_device_room.device.name
            == devices_name_conf[index]
        )
        assert ir_device_room.location.pos == devices_loc_conf[index]
        index += 1

    # Check window
    window1_config = {
        "name": "window1",
        "room": room1,
        "wall": "north",
        "loc_offset": 4,
        "size": [2, 1.5],
        "win_loc": (4, 10, 1.5),
    }
    ir_window1 = system.InRoomDevice(window1, room1, 4, 10, 1.5)
    assert ir_window1 in room_conf.windows
    assert ir_window1 in room_conf.world.ambient_light._AmbientLight__windows
    ir_window1_room = room_conf.windows[room_conf.windows.index(ir_window1)]
    assert ir_window1_room.name == ir_window1_room.device.name == window1_config["name"]
    window1_room = ir_window1_room.device
    assert window1_room.wall == window1_config["wall"]
    assert window1_room.location_offset == window1_config["loc_offset"]
    assert window1_room.window_loc == window1_config["win_loc"]
    assert window1_room.size == window1_config["size"]
    assert (
        room_conf.world.ambient_light._AmbientLight__lux_out == 10752
    )  # clear day at 11, datetime="2022/06/13/11/00"
    assert hasattr(window1_room, "max_lumen")
    assert window1_room.max_lumen == 32256.0  # area * out_lux
    assert round(window1_room.effective_lumen(), 1) == 32256.0  # no blinds

    # Check correct group addresses
    for ga in group_addresses:
        main, middle, sub = ga.split("/")
        ga_conf = system.GroupAddress("3-levels", main=main, middle=middle, sub=sub)
        assert ga_conf in room_conf.knxbus.group_addresses
        for ga_bus in room_conf.knxbus._KNXBus__ga_buses:
            if ga_bus.group_address is ga_conf:
                for device in group_addresses[ga]:
                    if isinstance(device, dev.Actuator):
                        assert device in ga_bus.actuators
                    if isinstance(device, dev.Sensor):
                        assert device in ga_bus.sensors
                    if isinstance(device, dev.FunctionalModule):
                        assert device in ga_bus.functional_modules
