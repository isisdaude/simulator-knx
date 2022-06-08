#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import logging, sys, json, os

import devices as dev
from system.system_tools import IndividualAddress, Window
from .check_tools import check_group_address, check_simulation_speed_factor
# from system.room import Room


DEV_CLASSES = { "LED": dev.LED, "Heater":dev.Heater, "AC":dev.AC, "Switch": dev.Switch,
                "Button": dev.Button, "Dimmer": dev.Dimmer, #"TemperatureController": dev.TemperatureController,  #"Switch": dev.Switch,
                "Brightness": dev.Brightness, "Thermometer": dev.Thermometer, "HumiditySoil":dev.HumiditySoil, "HumidityAir":dev.HumidityAir,
                "CO2Sensor": dev.CO2Sensor, "PresenceSensor": dev.PresenceSensor, "AirSensor": dev.AirSensor}

## User command mode (script or CLI)
GUI_MODE        = 'gui'
CLI_INT_MODE    = 'cli'
## User interface mode, this flag is only taken into account if INTERFACE_MODE = CLI_MODE, no CLI if GUI launched
SCRIPT_MODE     = 'script'
CLI_COM_MODE    = 'cli'  
## Configuration mode
FILE_CONFIG     = 'file'     # configuration from json file
DEFAULT_CONFIG  = 'default'     # configuration from default json file (~3devices)
EMPTY_CONFIG    = 'empty'     # configuration with no devices
DEV_CONFIG      = 'dev'     # configuration from python function
# Path to save system configuration when modified using the GUI
SAVED_CONFIG_PATH = os.path.abspath("docs/config/") + '/'
# Config file paths
COMPLETE_FILE_PATH = "./config/sim_config_bedroom.json"
DEFAULT_CONFIG_PATH = "./config/default_config.json"
EMPTY_CONFIG_PATH = "./config/empty_config.json"
SVSHI_CONFIG_PATH = "./config/svshi_config.json"


def configure_system(simulation_speed_factor, system_dt=1, test_mode=False, svshi_mode=False, telegram_logging=False):
    from system import Room
    system_dt=1
    # Declaration of sensors, actuators and functional modules
    led1 = dev.LED("led1", "M-0_L1", IndividualAddress(0,0,1), "enabled") #Area 0, Line 0, Device 0
    led2 = dev.LED("led2", "M-0_L1", IndividualAddress(0,0,2), "enabled")

    heater1 = dev.Heater("heater1", "M-0_H1", IndividualAddress(0,0,11), "enabled", 400) #400W max power
    ac1 = dev.AC("ac1", "M-0_AC1", IndividualAddress(0,0,12), "enabled", 400)
    button1 = dev.Button("button1", "M-0_S1", IndividualAddress(0,0,20), "enabled")
    button2 = dev.Button("button2", "M-0_S2", IndividualAddress(0,0,21), "enabled")
    bright1 = dev.Brightness("brightness1", "M-0_L3", IndividualAddress(0,0,5), "enabled")

    outside_temperature = 20.0
    humidity_out = 50.0
    outside_co2 = 300
    room_insulation = 'good'
    # Declaration of the physical system
    room1 = Room("bedroom1", 20, 20, 3, simulation_speed_factor, '3-levels', system_dt,
                room_insulation, outside_temperature, humidity_out, outside_co2, test_mode=test_mode, 
                svshi_mode=svshi_mode, telegram_logging=telegram_logging) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
    # room1.__.group_address_style = '3-levels'
    room1.add_device(led1, 5, 5, 1)
    room1.add_device(led2, 10, 19, 1)
    room1.add_device(button1, 0, 0, 1)
    room1.add_device(button2, 0, 1, 1)
    room1.add_device(bright1, 20, 20, 1)

    room1.add_device(heater1, 0, 5, 1)
    room1.add_device(ac1, 20, 5, 1)
    print(room1)

    # Group addresses # '3-levels', '2-levels' or 'free'
    # ga1 = GroupAddress('3-levels', main = 1, middle = 1, sub = 1)
    ga1 = '1/1/1'
    room1.attach(led1, ga1) # Actuator is linked to the group address ga1 through the KNXBus
    room1.attach(button1, ga1)
    # return the room object to access all elements of the room (world included)
    return room1, system_dt

def configure_system_from_file(config_file_path, system_dt=1, test_mode=False, svshi_mode=False, telegram_logging=False):
    from system import Room
    with open(config_file_path, "r") as file:
        config_dict = json.load(file) ###
    knx_config = config_dict["knx"]
    group_address_encoding_style = check_group_address(knx_config["group_address_style"], style_check=True)
    if not group_address_encoding_style:
        logging.error("Incorrect group address, check the config file before launching the simulator")
        sys.exit()
    world_config = config_dict["world"]
    # Store number of main elements 
    number_of_rooms = world_config["number_of_rooms"]
    number_of_areas = knx_config["number_of_areas"]
    # Parsing of the World config to create the room(s), and store corresponding devices
    simulation_speed_factor = check_simulation_speed_factor(world_config["simulation_speed_factor"])
    try:
        assert simulation_speed_factor
    except AssertionError:
        logging.error("Incorrect simulation speed factor, review the config file before launching the simulator")
        sys.exit()
    
    # Physical initial states indoor/outdoor
    temperature_out = world_config["outside_temperature"]
    temperature_in = world_config["inside_temperature"]
    # print(f"++++++++ config init temp in: {temperature_in}")
    humidity_out = world_config["outside_relativehumidity"]
    humidity_in = world_config["inside_relativehumidity"]
    co2_out = world_config["outside_co2"]
    co2_in = world_config["inside_co2"]
    datetime = world_config["datetime"]
    weather = world_config["weather"]
    system_dt = world_config["system_dt"]

    rooms_builders = [] # will contain list of list of room obj and device dict in the shape: [[room_object1, {'led1': [5, 5, 1], 'led2': [10, 19, 1], 'button': [0, 1, 1], 'bright1': [20, 20, 1]}], [room_object2, ]
    rooms = []
    ga_builders = []
    rooms_config = world_config["rooms"]
    for r in range(1,number_of_rooms+1):
        room_key = "room"+str(r) #room1, room2,...
        try:
            room_config = rooms_config[room_key]
        except (KeyError):
            logging.warning(f"'{room_key}' not defined in config file, or wrong number of rooms")
            continue # get out of the for loop iteratiom
        x, y, z = room_config["dimensions"]
        room_insulation = room_config["insulation"]
        # creation of a room of x*y*zm3, TODO: check coordinate and origin we suppose the origin of the room (right-bottom corner) is at (0, 0)
        room = Room(room_config["name"], x, y, z, simulation_speed_factor, group_address_encoding_style, system_dt, 
                    room_insulation, temperature_out, humidity_out, co2_out, temperature_in, humidity_in, co2_in, 
                    datetime, weather, test_mode=test_mode, svshi_mode=svshi_mode, telegram_logging=telegram_logging)
        windows = []
        for window in room_config["windows"]:
            wall = room_config["windows"][window]["wall"]
            location_offset = room_config["windows"][window]["location_offset"]
            size = room_config["windows"][window]["size"]
            try:
                window_object = Window(window, room, wall, location_offset, size)
                windows.append(window_object)
                room.add_window(window_object)
            except ValueError as msg:
                logging.error(msg)                
        # room.__.group_address_style = group_address_encoding_style
        # Store room object to return to main
        rooms.append(room)
        room_devices_config = room_config["room_devices"]
        # print(" ------- Room config dict -------")
        # print(room_devices_config)
        # Store temporarily the room object with devices and their physical position
        rooms_builders.append([room, room_devices_config])
    # Parsing of devices to add in the room
    print(" ------- Room devices from configuration file -------")
    for a in range(number_of_areas):
        area_key = "area"+str(a) #area0, area1,...
        number_of_lines = knx_config[area_key]["number_of_lines"]
        for l in range(number_of_lines):
            line_key = "line"+str(l) #line0, line1,...
            try:
                line_config = knx_config[area_key][line_key]
            except (KeyError):
                logging.warning(f"'{area_key}' and/or '{line_key}' not defined in config file. Check number of areas/lines and their names.")
                break # get out of the for loop
            line_device_keys = list(line_config["devices"].keys())
            line_devices_config = line_config["devices"]
            for dev_key in line_device_keys:
                try:
                    device_config = line_devices_config[dev_key]
                    dev_class = device_config["class"]
                    dev_refid = device_config["refid"]
                    dev_status = device_config["status"]
                except (KeyError):
                    logging.warning(f"'{dev_key}' configuration is incomplete on {area_key}.{line_key}")
                    continue # get out of the for loop iteration
                # print(f"{dev_key}, {dev_class}, {dev_refid}, loc = {device_config['location']}")
                _a, _l, _d = [int(loc) for loc in device_config["knx_location"].split(".")] # parse individual addresses 'area/line/device' in 3 variables
                if (_a != a or _l != l):
                    logging.warning(f"{dev_key} on {area_key}.{line_key} is wrongly configured with area{_a}.line{_l} ==> device is rejected")
                    continue # get out of the for loop iteration
                if (_a < 0 or _a > 15 or _l < 0 or _l > 15 or _d < 0 or _d > 255):
                    logging.warning(f"Individual address out of bounds, should be in 0.0.0 -> 15.15.255 ==> device is rejected")
                    continue # get out of the for loop iteration
                dev_status = device_config["status"]
                print(dev_key)
                for room_builder in rooms_builders: # list of [room_object, room_devices_config] for all rooms of the system
                    if dev_key in room_builder[1].keys():
                        dev_pos = room_builder[1][dev_key]
                        # Create the device object before adding it to the room
                        dev_object = DEV_CLASSES[dev_class](dev_key, dev_refid, IndividualAddress(_a, _l, _d), dev_status) # we don't set up the state, False(OFF) by default
                        room_builder[0].add_device(dev_object, dev_pos[0], dev_pos[1], dev_pos[2])
                    else:
                        logging.warning(f"{dev_key} is defined on KNX system but no physical location in the room was given ==> device is rejected")
                        continue # get out of the for loop iteration
    # print(" ----------------------------------------------------")
    # Parsing of group addresses to connect devices together
    #TODO: link GAs to interface IP SVSHI
    # print(" ------- KNX System Configuration -------")
    ga_style =  knx_config["group_address_style"]
    ga_builders = knx_config["group_addresses"]
    if len(ga_builders):
        for ga_builder in ga_builders:
            group_address = ga_builder["address"]
            group_devices = ga_builder["group_devices"]
            # Loop on devices connected to this ga
            for dev_name in group_devices:
                for room in rooms:
                    for in_room_device in room.devices:
                        # Find the device object
                        if in_room_device.name == dev_name:
                            dev_object = in_room_device.device
                            # Link the device to the ga (internal test to check Group Address format)
                            room.attach(dev_object, group_address)
    else:
        logging.info("No group address is defined in config file.")
    return rooms[0], system_dt # only one room