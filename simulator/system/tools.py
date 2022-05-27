
import logging, sys
from  datetime import datetime, timezone, timedelta
# import astral
from astral import LocationInfo
from astral.sun import sun
import asyncio
import math
import json
import devices as dev
import pprint
pp=pprint.PrettyPrinter(compact=True)

#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
#from .room import InRoomDevice not useful, but if used, put it on the class / function directly # to avoid circular import room <-> tools
COMMAND_HELP = "Command Syntax: \n"\
                "- switch state: 'set [device_name]'\n"\
                "- read state: 'get [device_name]'\n"\
                "- API: 'getinfo [device_name]' or 'getinfo world [ambient]'\n"\
                "- exit: 'q'\n"\
                "- help: 'h' for help"
# dict to link string to devices constructor object
DEV_CLASSES = { "LED": dev.LED, "Heater":dev.Heater, "AC":dev.AC, "Switch": dev.Switch,
                "Button": dev.Button, "Dimmer": dev.Dimmer, #"TemperatureController": dev.TemperatureController,  #"Switch": dev.Switch,
                "Brightness": dev.Brightness, "Thermometer": dev.Thermometer, "HumiditySoil":dev.HumiditySoil, "HumidityAir":dev.HumidityAir,
                "CO2Sensor": dev.CO2Sensor, "PresenceSensor": dev.PresenceSensor, "AirSensor": dev.AirSensor}
# Situation of the insulation of the room associated to the correction factor for the heating
# INSULATION_TO_CORRECTION_FACTOR = {"average": 0, "good": -10/100, "bad": 15/100}
# Influence of outdoor temp
INSULATION_TO_TEMPERATURE_FACTOR = {"perfect": 0, "good": 10/100, "average": 20/100, "bad":40/100}
# Influence of outdoor humidity
INSULATION_TO_HUMIDITY_FACTOR = {"perfect": 0, "good": 20/100, "average": 45/100, "bad":75/100}
# Influence of outdoor co2
INSULATION_TO_CO2_FACTOR = {"perfect": 0, "good": 10/100, "average": 25/100, "bad":50/100}


# TODO: should check that individuql addr in the right boundaries!!!
MAX_MAIN = 31
MAX_MIDDLE = 7
MAX_SUB_LONG = 255
MAX_SUB_SHORT = 2047
MAX_FREE = 65535

""" Class tools """

class Window:
    """Class to represent windows"""
    def __init__(self, window_name, room, wall, location_offset_ratio, size):
        from .check_tools import check_window
        ## window img size is 300p wide, for a room of 12.5m=1000p, it corresponds to 3.75m
        ## must scale the window if different size, e.g. if window size = 1m, scale factor x(horizontal) ou y(vertical) = 1/3.75``
        self.WINDOW_PIXEL_SIZE = 300
        ROOM_PIXEL_WIDTH = 1000 ## TODO: take this constant from a config file
        self.initial_size = room.width * self.WINDOW_PIXEL_SIZE / ROOM_PIXEL_WIDTH # 3.75m if room width=12.5 for 1000 pixels
        self.name = window_name
        self.class_name = 'Window'
        self.wall, self.window_loc, self.size  = check_window(wall, location_offset_ratio, size, room)   # size[width, height] in meters
        # self.window_loc = (x, y, z) for 
        # self.wall in north', 'south', 'east' or 'west'
        # self.size = [width/lengh, height]
        if self.wall is None: # failed check
            raise ValueError("Window objec cannot be created, check the error logs")

        self.beam_angle = 180 # arbitrary  but realistic
        self.state = True # state to be compliant with LighActuator's attributes
        self.state_ratio = 100 # change if blinds implemented

        # for the GUI display
        if self.wall in ['north', 'south']:
            self.scale_x = self.size[0] / self.initial_size
        if self.wall in ['east', 'west']:
            self.scale_y = self.size[0] / self.initial_size
        # self.location_out_offset =  # offset for location to consider light source point outside of room, so that with a certain beamangle, all light is considered

    def max_lumen_from_out_lux(self, out_lux):
        self.max_lumen = out_lux * math.prod(self.size) # out_lux*window_area
    
    def effective_lumen(self):
        # Lumen quantity rationized with the state ratio (% of source's max lumens)
        return self.max_lumen*(self.state_ratio/100)



class Location:
    """Class to represent location"""
    def __init__(self, room, x, y, z):
        from .check_tools import check_location
        self.room = room
        self.min_x, self.max_x = 0, self.room.width
        self.min_y, self.max_y = 0, self.room.length
        self.min_z, self.max_z = 0, self.room.height
        self.bounds = [[ self.min_x, self.max_x], [self.min_y, self.max_y], [self.min_z, self.max_z]]
        # Check that location is correct, replace in the room if out of bounds
        self.x, self.y, self.z = check_location(self.bounds, x, y, z)
        self.pos = (self.x, self.y, self.z)

    # def update_location(self, new_x=None, new_y=None, new_z=None):
    #     from .check_tools import check_location
    #     x = (new_x or self.x)
    #     y = (new_y or self.y)
    #     z = (new_z or self.z)
    #     self.x, self.y, self.z = check_location(self.bounds, x, y, z)
    #     self.pos = (self.x, self.y, self.z)

    def __str__(self):
        str_repr =  f"Location: {self.room.name}: {self.pos}\n"
        return str_repr

    def __repr__(self):
        return f"Location in {self.room.name} is {self.pos}\n"


class IndividualAddress:
    """Class to represent individual addresses (virtual location on the KNX Bus)"""
    ## Magic Number
    def __init__(self, area, main, line): # area[4bits], line[4bits], device[8bits]
        from .check_tools import check_individual_address
        self.area, self.line, self.device = check_individual_address(area, line, main)
        self.ia_str = '.'.join([str(self.area), str(self.device), str(self.line)])

    def __eq__(self, other):
        return (self.area == other.area and
                self.line == other.line and
                self.device == self.device)

    def __str__(self): # syntax when instance is called with print()
        return self.ia_str
        # return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"
    
    def __repr__(self): # syntax when instance is called in python interpreter
        return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"

    def __repr__(self) -> str:
        '''Following XKNX handling of individual addresses'''
        return f"{self.area}.{self.line}.{self.device}"


class GroupAddress:
    """Class to represent group addresses (devices gathered by functionality)"""
    ## Magic Number

    def __init__(self, encoding_style, main, middle=0, sub=0):
        self.encoding_style = encoding_style
        if self.encoding_style == '3-levels': # main[5bits], middle[3bits], sub[8bits]
            # try: # test if the group address has the correct format
            #     assert (main >= 0 and main <= 31 and middle >= 0 and middle <= 7 and sub >= 0 and sub <= 255)
            # except AssertionError:
            #     logging.warning("'3-levels' group address is out of bounds")
            self.main = main
            self.middle = middle
            self.sub = sub
            self.name = "/".join((str(main), str(middle), str(sub)))
        elif self.encoding_style == '2-levels': # main[5bits], sub[11bits]
            # try: # test if the group address has the correct format
            #     assert (main >= 0 and main <= 31 and sub >= 0 and sub <= 2047)
            # except AssertionError:
            #     logging.warning("'2-levels' group address is out of bounds")
            self.main = main
            self.sub = sub
            self.name = "/".join((str(main), str(sub)))
        elif self.encoding_style == 'free': # main[16bits]
            # try: # test if the group address has the correct format
            #     assert (main >= 0 and main <= 65535)
            # except AssertionError:
            #     logging.warning("'free' group address is out of bounds")
            self.main = main
            self.name = str(main)

    def __str__(self): # syntax when instance is called with print()
        return self.name
        # if self.encoding_style == '3-levels':
        #     return f"({self.main}/{self.middle}/{self.sub})"
        # elif self.encoding_style == '2-levels':
        #     return f"({self.main}/{self.sub})"
        # elif self.encoding_style == 'free':
        #     return f"({self.main})"

        # if self.encoding_style == '3-levels':
        #     return f" Group Address(main:{self.main}, middle:{self.middle}, sub:{self.sub})"
        # elif self.encoding_style == '2-levels':
        #     return f" Group Address(main:{self.main}, sub:{self.sub})"
        # elif self.encoding_style == 'free':
        #     return f" Group Address(main:{self.main}) "

    def __repr__(self): # syntax when instance is called with print()
        return self.name
        # if self.encoding_style == '3-levels':
        #     return f"({self.main}/{self.middle}/{self.sub})"
        # elif self.encoding_style == '2-levels':
        #     return f"({self.main}/{self.sub})"
        # elif self.encoding_style == 'free':
        #     return f"({self.main})"

# __eq__() or __lt__(), "is" operator to check if an instances are of the same type
    def __lt__(self, ga_to_compare): # self is the group addr ref, we want to check if self is smaller than the other ga
        if self.encoding_style == '3-levels':
            ga_ref = self.sub + self.middle<<8 + self.main<<11
            ga_test = ga_to_compare.sub + ga_to_compare.middle<<8 + ga_to_compare.main<<11
            return (ga_ref < ga_test)
        if self.encoding_style == '2-levels':
            ga_ref = self.sub + self.main<<11
            ga_test = ga_to_compare.sub + ga_to_compare.main<<11
            return (ga_ref < ga_test)
        if self.encoding_style == 'free':
            return (self.main < ga_to_compare.main)

    def __eq__(self, ga_to_compare):
        if self.main == ga_to_compare.main:
            if self.encoding_style == 'free':
                return True
            else: # if encoding style is 2 or 3-levels
                if self.sub == ga_to_compare.sub:
                    if self.encoding_style == '2-levels':
                        return True
                    else: # if encoding style is 3-levels
                        if self.middle == ga_to_compare.middle:
                            return True
                        else:
                            return False

""" Functions tools """

def configure_system(simulation_speed_factor, system_dt=1, test_mode=False):
    from .room import Room
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
                room_insulation, outside_temperature, humidity_out, outside_co2, test_mode=test_mode) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
    # room1.group_address_style = '3-levels'
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
    return [room1]

def configure_system_from_file(config_file_path, system_dt=1, test_mode=False):
    from .room import Room
    from .check_tools import check_group_address, check_simulation_speed_factor
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
    humidity_out = world_config["outside_relativehumidity"]
    humidity_in = world_config["inside_relativehumidity"]
    co2_out = world_config["outside_co2"]
    co2_in = world_config["inside_co2"]
    datetime = world_config["datetime"]
    weather = world_config["weather"]


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
                    datetime, weather, test_mode=test_mode)
        windows = []
        for window in room_config["windows"]:
            wall = room_config["windows"][window]["wall"]
            location_offset_ratio = room_config["windows"][window]["location_offset_ratio"]
            size = room_config["windows"][window]["size"]
            try:
                window_object = Window(window, room, wall, location_offset_ratio, size)
                windows.append(window_object)
                room.add_window(window_object)
            except ValueError as msg:
                logging.error(msg)
                
                
        # room.group_address_style = group_address_encoding_style
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
    print(" ----------------------------------------------------")
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
    return rooms


def user_command_parser(command, room):
    if command[:3] == 'set': #FunctionalModule
        name = command[4:]
        # print(f"name: {name}")
        for in_room_device in room.devices:
            # print(f"name:'{name}', ir_name:'{in_room_device.name}'")
            if in_room_device.name in name:
                if not isinstance(in_room_device.device, dev.FunctionalModule):
                    logging.warning("Users can only interact with a Functional Module")
                    return 1
                # print("user_input()")
                in_room_device.device.user_input()
                return 1
    elif command[:7] == 'getinfo':
        print("getinfo:> ", command[8:])
        if 'world' in command[8:13]: # user asks for world info
            ambient = command[14:].strip() # can be 'time', 'temperature', 'humidity', 'co2level', 'co2', 'brightness', 'all'
            if len(ambient) >= len('all'): # smallest str acceptable after 'getinfo world' command
                if 'time' in ambient:
                    world_dict = room.get_world_info('time')
                if 'temperature' in ambient:
                    world_dict = room.get_world_info('temperature')
                if 'humidity' in ambient:
                    world_dict = room.get_world_info('humidity')
                if 'co2' in ambient:
                    world_dict = room.get_world_info('co2level')
                    # brightness is a global average from edge location in room, or average of sensors
                if 'brightness' in ambient: 
                    world_dict = room.get_world_info('brightness')
                if 'all' in ambient:
                    world_dict = room.get_world_info('all')
            else: # if nothing detailed, just get all world info
                world_dict = room.get_world_info('all')
            ## TODO check some stuff with info, write some kind of API
            pp.pprint(world_dict)
            return world_dict
        elif 'room' in command[8:12]: # user asks for info on the room
            room_dict = room.get_room_info()
            pp.pprint(room_dict)
            return room_dict
        elif 'bus' in command[8:11]:
            bus_dict = room.get_bus_info()
            pp.pprint(bus_dict)
            return bus_dict
        else:
            if 'dev' in command[8:11]: # user ask for info on a device
                name = command[12:].strip() # strip to remove spaces
            else:
                name = command[8:].strip() # user ask for info on a device without using the dev keyword
            device_dict = room.get_device_info(name)
            ## TODO check some stuff with info, write some kind of API
            pp.pprint(device_dict)
            return device_dict
            
    elif command[:3] == 'get': #Sensor
        name = command[4:]
        if "bright" in name: # brightness sensor
            for in_room_device in room.devices:
                if in_room_device.name in name:
                    print("=> The brightness received on sensor %s located at (%d,%d) is %.2f\n" % (name, in_room_device.get_x(), in_room_device.get_y(), room.world.ambient_light.read_brightness(in_room_device)))
                    return 1
    elif command in ('h', 'H','help','HELP'):
        print(COMMAND_HELP)
        return 1
    elif command in ('q','Q','quit','QUIT'):
        return None
    else:
        logging.warning("Unknown input")
        print(COMMAND_HELP)
    return 1


class ScriptParser():
    def __init__(self):
        self.stored_values = {}
    
    async def script_command_parser(self, room, command):
        command_split = command.split(' ')
        if command.startswith('wait'):
            sleep_time = int(command_split[1])
            logging.info(f"[VERIF] Wait for {sleep_time} sec")
            await asyncio.sleep(sleep_time)
            return 1
        elif command.startswith('store'):
            if command_split[1] == 'world':
                if len(command_split) > 2: # ambient to store is precised by the user
                    for ambient in command_split[2:]:
                        self.stored_values[ambient] = room.get_world_info(ambient, str_mode=False)[ambient+'_in']
                        logging.info(f"[VERIF] The world {ambient} is stored.")
                        return 1
                else: # No ambient precised, we store all
                    for ambient in ['simtime', 'brightness', 'temperature', 'humidity', 'co2']:
                        self.stored_values[ambient] = room.get_world_info(ambient, str_mode=False)[ambient+'_in']
                        logging.info(f"[VERIF] The world {ambient} is stored.")
                        return 1

        elif command.startswith('assert'):
            if command_split[1] == 'world':
                if len(command_split) >= 4: # assert, world, ambient, up/down/=
                    ambient = command_split[2]
                    if ambient in self.stored_values:
                        old_ambient = self.stored_values[ambient]
                        new_ambient = room.get_world_info(ambient, str_mode=False)[ambient+'_in']
                        if command_split[3] == 'up':
                            assert new_ambient > old_ambient
                            logging.info(f"[VERIF] The {ambient} has increased.")
                            print(f"Assertion True")
                            return 1
                        elif command_split[3] == 'down':
                            assert new_ambient < old_ambient
                            logging.info(f"[VERIF] The {ambient} has decreased.")
                            print(f"Assertion True")
                            return 1
                        elif command_split[3] == '=':
                            assert new_ambient == old_ambient
                            logging.info(f"[VERIF] The {ambient} didn't change.")
                            print(f"Assertion True")
                            return 1
        elif command.startswith('end'):
            print("End of verification")
            print(COMMAND_HELP)
            return None

        else:
            # print(f"command parser with '{command}'")
            return user_command_parser(command, room) 
  



"""Tools for physical world updates"""
def compute_distance(source, sensor) -> float:
    """ Computes euclidian distance between a sensor and a actuator"""
    delta_x = abs(source.location.x - sensor.location.x)
    delta_y = abs(source.location.y - sensor.location.y)
    delta_z = abs(source.location.z - sensor.location.z)
    dist = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2) # distance between light sources and brightness sensor
    return dist

DATE_WEATHER_TO_LUX = {"clear_day":10752, "overcast_day":1075, "dark_day":107, "clear_sunrise_sunset":300, "overcast_sunrise_sunset":100, "dark_sunrise_sunset":10,  "clear_twilight":10.8, "overcast_twilight":1, "clear_night":0.108, "overcast_night":0.0001, "dark_night":0}
def outdoor_light(date_time:datetime, weather:str):
    city = LocationInfo("Lausanne", "Switzerland", "Europe", 46.516, 6.63282)
    date = date_time.date()
    date_time = date_time.replace(tzinfo=timezone.utc)
    sun_time = sun(city.observer, date=date)
    dawn_datetime, sunrise_datetime, noon_datetime, sunset_datetime, dusk_datetime = sun_time["dawn"], sun_time["sunrise"], sun_time["noon"], sun_time["sunset"], sun_time["dusk"]
    # Night
    if date_time < dawn_datetime or dusk_datetime < date_time:
        time_of_day = 'moon' # for gui time of day symbol
        if weather == "clear":
            lux_out = DATE_WEATHER_TO_LUX["clear_night"]
        elif weather == "overcast":
            lux_out = DATE_WEATHER_TO_LUX["overcast_night"]
        elif weather == "dark":
            lux_out = DATE_WEATHER_TO_LUX["dark_night"]
    # Day
    elif sunrise_datetime < date_time and date_time < sunset_datetime:
        time_of_day = 'sun' # for gui time of day symbol
        if date_time < noon_datetime: # ratio of how close we are to ;id_morning/mid_afternoon, 1 if mid_morning < date_time < mid_afternoon
            mid_morning_offset = (noon_datetime - sunrise_datetime) / 2
            mid_morning_datetime = sunrise_datetime + mid_morning_offset
            ratio = min((date_time - sunrise_datetime) / (mid_morning_datetime - sunrise_datetime), 1)
        elif noon_datetime < date_time:
            mid_afternoon_offset = (sunset_datetime - noon_datetime) / 2
            mid_afternoon_datetime = sunset_datetime - mid_afternoon_offset
            ratio = min((sunset_datetime - date_time ) / (sunset_datetime - mid_afternoon_datetime), 1)
        if weather == "clear":
            lux_out = max(ratio * DATE_WEATHER_TO_LUX["clear_day"], DATE_WEATHER_TO_LUX["clear_sunrise_sunset"])
        elif weather == "overcast":
            lux_out = max(ratio * DATE_WEATHER_TO_LUX["overcast_day"], DATE_WEATHER_TO_LUX["overcast_sunrise_sunset"])
        elif weather == "dark":
            lux_out = max(ratio * DATE_WEATHER_TO_LUX["dark_day"], DATE_WEATHER_TO_LUX["dark_sunrise_sunset"])
    # Twilight
    else: # ratio of how close we are to sunrise/sunset with regards to twilight
        if dawn_datetime < date_time and date_time < sunrise_datetime:
            time_of_day = 'sunrise' # for gui time of day symbol
            ratio = (date_time - dawn_datetime) / (sunrise_datetime - dawn_datetime) 
        elif sunset_datetime < date_time and date_time < dusk_datetime:
            time_of_day = 'sunset' # for gui time of day symbol
            ratio = (dusk_datetime - date_time) / (dusk_datetime - sunset_datetime)
            
        if weather == "clear":
            lux_out = ratio * (DATE_WEATHER_TO_LUX["clear_sunrise_sunset"] - DATE_WEATHER_TO_LUX["clear_twilight"])
        elif weather == "overcast":
            lux_out = ratio * (DATE_WEATHER_TO_LUX["overcast_sunrise_sunset"] - DATE_WEATHER_TO_LUX["overcast_twilight"])
        elif weather == "dark":
            lux_out = ratio * (DATE_WEATHER_TO_LUX["dark_sunrise_sunset"] - DATE_WEATHER_TO_LUX["overcast_twilight"])
    # print(f"-- lux_out : {lux_out}")
    # print(f" ------ {date_time}")
    # print(f"{dawn_datetime}:dawn_datetime, \n{sunrise_datetime}:sunrise_datetime, \n{noon_datetime}:noon_datetime, \n{sunset_datetime}:sunset_datetime, \n{dusk_datetime}:dusk_datetime")
    return lux_out, time_of_day



"""Tools used by the devices to perform update calculations"""
# def required_power(desired_temperature=20, volume=1, insulation_state="good"):
#     def temp_to_watts(temp):  # Useful watts required to heat 1m3 to temp
#         dist = 18 - temp
#         return 70 - (dist * 7)/2
#     desired_wattage = volume*temp_to_watts(desired_temperature)
#     desired_wattage += desired_wattage * \
#         INSULATION_TO_CORRECTION_FACTOR[insulation_state]
#     return desired_wattage


# def max_temperature_in_room(power, volume=1.0, insulation_state="good"):
#     """Maximum reachable temperature for this heater in the specified room"""

#     def watts_to_temp(watts):
#         return ((watts - 70)*2)/7 + 18

#     watts = power / ((1+INSULATION_TO_CORRECTION_FACTOR[insulation_state])*volume)
#     return watts_to_temp(watts)
