
import logging, sys
import math
import json
import devices as dev
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
#from .room import InRoomDevice not useful, but if used, put it on the class / function directly # to avoid circular import room <-> tools
COMMAND_HELP = "enter command: \n -FunctionalModules: 'set '+name to act on it\n -Sensors: 'get '+name to read sensor value\n>'q' to exit the simulation, 'h' for help<\n"
# dict to link string to devices constructor object
DEV_CLASSES = { "LED": dev.LED, "Heater":dev.Heater, "AC":dev.AC, "Switch": dev.Switch,
                "Button": dev.Button, "Dimmer": dev.Dimmer, "TemperatureController": dev.TemperatureController,  #"Switch": dev.Switch,
                "Brightness": dev.Brightness, "Thermometer": dev.Thermometer, "HumiditySensor":dev.HumiditySensor,
                "CO2Sensor": dev.CO2Sensor, "PresenceSensor": dev.PresenceSensor, "AirSensor": dev.AirSensor}
# Situation of the insulation of the room associated to the correction factor for the heating
# INSULATION_TO_CORRECTION_FACTOR = {"average": 0, "good": -10/100, "bad": 15/100}
# Influence of outdoor temp
INSULATION_TO_TEMPERATURE_FACTOR = {"perfect": 0, "good": 10/100, "average": 20/100, "bad":40/100}
# Influence of outdoor humidity
INSULATION_TO_HUMIDITY_FACTOR = {"perfect": 0, "good": 20/100, "average": 45/100, "bad":75/100}
# Influence of outdoor co2
INSULATION_TO_CO2_FACTOR = {"perfect": 0, "good": 10/100, "average": 25/100, "bad":50/100}

# TODO: should check that in the right boundaries!!!
MAX_MAIN = 31
MAX_MIDDLE = 7
MAX_SUB_LONG = 255
MAX_SUB_SHORT = 2047
MAX_FREE = 65535

""" Class tools """

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
    def __init__(self, area, line, device): # area[4bits], line[4bits], device[8bits]
        from .check_tools import check_individual_address
        self.area, self.line, self.device = check_individual_address(area, line, device)
        self.ia_string = '.'.join([str(self.area), str(self.line), str(self.device)])

    def __eq__(self, other):
        return (self.area == other.area and
                self.line == other.line and
                self.device == self.device)

    def __str__(self): # syntax when instance is called with print()
        return self.ia_string
        # return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"
    
    def __repr__(self): # syntax when instance is called in python interpreter
        return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"

    def __repr__(self) -> str:
        '''Following XKNX handling of individual addresses'''
        return f"{self.area}.{self.device}.{self.line}"


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

def configure_system(simulation_speed_factor, system_dt=1):
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
    outside_humidity = 50.0
    outside_co2 = 300
    room_insulation = 'good'
    # Declaration of the physical system
    room1 = Room("bedroom1", 20, 20, 3, simulation_speed_factor, '3-levels', system_dt,
                room_insulation, outside_temperature, outside_humidity, outside_co2) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
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

def configure_system_from_file(config_file_path, system_dt=1):
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
    # Store number of elements to check that the config file is correct
    number_of_rooms = world_config["number_of_rooms"]
    number_of_areas = knx_config["number_of_areas"]
    # Parsing of the World config to create the room(s), and store corresponding devices
    simulation_speed_factor = check_simulation_speed_factor(world_config["simulation_speed_factor"])
    try:
        assert simulation_speed_factor
    except AssertionError:
        logging.error("Incorrect simulation speed factor, review the config file before launching the simulator")
        sys.exit()
    
    outside_temperature = world_config["outside_temperature"]
    outside_humidity = world_config["outside_relativehumidity"]
    outside_co2 = world_config["outside_co2"]

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
                    room_insulation, outside_temperature, outside_humidity, outside_co2)
        # room.group_address_style = group_address_encoding_style
        # Store room object to return to main
        rooms.append(room)
        room_devices_config = room_config["room_devices"]
        print(" ------- Room config dict -------")
        print(room_devices_config)
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
    # Parsing of group addresses to connect devices together
    #TODO: link GAs to interface IP SVSHI
    print(" ------- KNX System Configuration -------")
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
        for in_room_device in room.devices:
            if in_room_device.name in name:
                if not isinstance(in_room_device.device, dev.FunctionalModule):
                    logging.warning("Users can only interact with a Functional Module")
                    break
                print("user_input()")
                in_room_device.device.user_input()
    elif command[:3] == 'get': #Sensor
        name = command[4:]
        if "bright" in name: # brightness sensor
            for in_room_device in room.devices:
                if in_room_device.name in name:
                    print("=> The brightness received on sensor %s located at (%d,%d) is %.2f\n" % (name, in_room_device.get_x(), in_room_device.get_y(), room.world.ambient_light.read_brightness(in_room_device)))
    elif command in ('h', 'H','help','HELP'):
        print(COMMAND_HELP)
    elif command in ('q','Q','quit','QUIT'):
        return False
    else:
        logging.warning("Unknown input")
        print(COMMAND_HELP)
    return True



"""Tools for physical world updates"""
def compute_distance(source, sensor) -> float:
    """ Computes euclidian distance between a sensor and a actuator"""
    delta_x = abs(source.location.x - sensor.location.x)
    delta_y = abs(source.location.y - sensor.location.y)
    delta_z = abs(source.location.z - sensor.location.z)
    dist = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2) # distance between light sources and brightness sensor
    return dist


"""Tools used by the devices to perform update calculations"""
def required_power(desired_temperature=20, volume=1, insulation_state="good"):
    def temp_to_watts(temp):  # Useful watts required to heat 1m3 to temp
        dist = 18 - temp
        return 70 - (dist * 7)/2
    desired_wattage = volume*temp_to_watts(desired_temperature)
    desired_wattage += desired_wattage * \
        INSULATION_TO_CORRECTION_FACTOR[insulation_state]
    return desired_wattage


def max_temperature_in_room(power, volume=1.0, insulation_state="good"):
    """Maximum reachable temperature for this heater in the specified room"""

    def watts_to_temp(watts):
        return ((watts - 70)*2)/7 + 18

    watts = power / ((1+INSULATION_TO_CORRECTION_FACTOR[insulation_state])*volume)
    return watts_to_temp(watts)
