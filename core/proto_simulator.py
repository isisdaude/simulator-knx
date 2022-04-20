"""
Simple simulator prototype.
"""

import functools
import asyncio, aioconsole
import time, datetime
import aioreactive as rx
import pyglet
import json
from pynput import keyboard
from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import system
import gui
import devices as dev
import simulation as sim
import user_interface as ui
from system import IndividualAddress, Telegram, GroupAddress

COMMAND_HELP = "enter command: \n -FunctionalModules: 'set '+name to act on it\n -Sensors: 'get '+name to read sensor value\n>'q' to exit the simulation, 'h' for help<\n"
CONFIG_PATH = "simulation_config.json"
# dict to link string to devices constructor object
DEV_CLASSES = { "LED": dev.LED, "Heater":dev.Heater, "AC":dev.AC,
                "Button": dev.Button, "Switch": dev.Switch, "TemperatureController": dev.TemperatureController,
                "Brightness": dev.Brightness, "Thermometer": dev.Thermometer, "HumiditySensor":dev.HumiditySensor, "CO2Sensor": dev.CO2Sensor, "PresenceDetector": dev.PresenceDetector, "MovementDetector": dev.MovementDetector}

def configure_system(simulation_speed_factor):
    # Declaration of sensors and actuators
    led1 = dev.LED("led1", "M-0_L1", IndividualAddress(0,0,1), "enabled") #Area 0, Line 0, Device 0
    led2 = dev.LED("led2", "M-0_L1", IndividualAddress(0,0,2), "enabled")

    heater1 = dev.Heater("heater1", "M-0_T1", IndividualAddress(0,0,11), "enabled", 400) #400W max power
    cooler1 = dev.AC("cooler1", "M-0_T2", IndividualAddress(0,0,12), "enabled", 400)

    switch1 = dev.Switch("switch1", "M-0_B1", IndividualAddress(0,0,20), "enabled")
    switch2 = dev.Switch("switch2", "M-0_B2", IndividualAddress(0,0,21), "enabled")
    bright1 = dev.Brightness("bright1", "M-0_L3", IndividualAddress(0,0,5), "enabled")

    # Declaration of the physical system
    room1 = system.Room("bedroom1", 20, 20, 3, simulation_speed_factor) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
    room1.add_device(led1, 5, 5, 1)
    room1.add_device(led2, 10, 19, 1)
    room1.add_device(switch1, 0, 0, 1)
    room1.add_device(switch2, 0, 1, 1)
    room1.add_device(bright1, 20, 20, 1)

    room1.add_device(heater1, 0, 5, 1)
    room1.add_device(cooler1, 20, 5, 1)
    print(room1)

    # Group addresses # '3-levels', '2-levels' or 'free'
    ga1 = GroupAddress('3-levels', main = 1, middle = 1, sub = 1)
    room1.knxbus.attach(led1, ga1) # Actuator is linked to the group address ga1 through the KNXBus
    room1.knxbus.attach(switch1, ga1)
    # return the room object to access all elements of the room (world included)
    return [room1]


def configure_system_from_file(config_file_path):
    with open(config_file_path, "r") as file:
        #s = [int(x) for x in a.split(".")]
        config_dict = json.load(file) ###
        knx_config = config_dict["knx"]
        world_config = config_dict["world"]
        # Store number of elements to check that the config file is correct
        number_of_rooms = world_config["number_of_rooms"]
        number_of_areas, number_of_lines = knx_config["number_of_areas"], knx_config["number_of_lines"]

        # Parsing of the World config to create the room(s), and store corresponding devices
        simulation_speed_factor = world_config["simulation_speed_factor"]
        rooms_builders = [] # will contain list of list of room obj and device dict in the shape: [[room_object1, {'led1': [5, 5, 1], 'led2': [10, 19, 1], 'switch': [0, 1, 1], 'bright1': [20, 20, 1]}], [room_object2, ]
        rooms = []
        for r in range(1,number_of_rooms+1):
            room_key = "room"+str(r) #room1, room2,...
            try:
                room_config = world_config[room_key]
            except (KeyError):
                print(f"[ERROR] '{room_key}' not defined in config file, or wrong number of rooms")
                continue # get out of the for loop iteratio

            x, y, z = room_config["dimensions"]
            # creation of a room of x*y*zm3, TODO: check coordinate and origin we suppose the origin of the room (right-bottom corner) is at (0, 0)
            room = system.Room(room_config["name"], x, y, z, simulation_speed_factor)
            # Store room object to return to main
            rooms.append(room)
            room_devices_config = room_config["room_devices"]
            print(room_devices_config)
            # Store temporarily the room object with devices and their physical position
            rooms_builders.append([room, room_devices_config])

        # Parsing of devices to add in the room
        for a in range(number_of_areas):
            area_key = "area"+str(a) #area0, area1,...
            for l in range(number_of_lines):
                line_key = "line"+str(l) #line0, line1,...
                try:
                    line_config = knx_config[area_key][line_key]
                except (KeyError):
                    print(f"[ERROR] '{area_key}' or '{line_key}' not defined in config file, or wrong number of areas/lines")
                    break # get out of the for loop
                number_of_devices = line_config["number_of_devices"]
                dc = 0 # counter to check number of devices in the room
                line_device_keys = list(line_config["devices"].keys())
                line_devices_config = line_config["devices"]
                for dev_key in line_device_keys:
                    dc += 1
                    if dc > number_of_devices:
                        print(f"[ERROR] Wrong number of devices, {number_of_devices} announced on {area_key}/{line_key} but {dev_key} is the {dc}")
                        continue
                    try:
                        device_config = line_devices_config[dev_key]
                    except (KeyError):
                        print(f"[ERROR] '{dev_key}' not defined in config file on {area_key}/{line_key}")
                        continue # get out of the for loop iteration
                    dev_class = device_config["class"]
                    dev_refid = device_config["refid"]
                    dev_status = device_config["status"]
                    # print(f"{dev_key}, {dev_class}, {dev_refid}, loc = {device_config['location']}")
                    _a, _l, _d = [int(loc) for loc in device_config["location"].split(".")] # parse individual addresses 'area/line/device' in 3 variables
                    if (_a != a or _l != l):
                        print(f"[ERROR] {dev_key} on {area_key}/{line_key} is wrongly configured with area{_a}/line{_l}")
                    dev_status = device_config["status"]
                    print(dev_key)

                    # Create the device object before adding it to the room
                    dev_object = DEV_CLASSES[dev_class](dev_key, dev_refid, IndividualAddress(_a, _l, _d), dev_status) # we don't set up the state, False(OFF) by default
                    for room_builder in rooms_builders: # list of [room_object, room_devices_config] for all rooms of the system
                        if dev_key in room_builder[1].keys():
                            dev_pos = room_builder[1][dev_key]
                            room_builder[0].add_device(dev_object, dev_pos[0], dev_pos[1], dev_pos[2])
                            # print(room_builder[0])
                        # print("room_builder")
                        # print(room_builder[1].keys())

        # Parsing of group addresses to connect devices together
        ga_style =  knx_config["group_address_style"]
        number_of_ga = knx_config["number_of_group_addresses"]
        ga_builders = knx_config["group_addresses"]
        if len(ga_builders) != number_of_ga:
            print(f"[ERROR] Wrong number of group addresses, {number_of_ga} announced but {len(ga_builders)} defined")
        else:
            for ga_index in range(number_of_ga):
                ga_builder = ga_builders[ga_index] #dict with address and devices to connect together
                main, middle, sub = [int(loc) for loc in ga_builder["address"].split("/")]
                ga_object = GroupAddress(ga_style, main=main, middle=middle, sub=sub)
                group_devices = ga_builder["group_devices"]
                # Loop on devices connected to this ga
                for dev_name in group_devices:
                    for room in rooms:
                        for in_room_device in room.devices:
                            # Find the device object
                            if in_room_device.name == dev_name:
                                dev_object = in_room_device.device
                                # Link the device to the ga
                                room.knxbus.attach(dev_object, ga_object)

        # print(f"ga_style, number: {ga_style}, {number_of_ga}")
        # print(f"ga_builders: {ga_builders}")

        # for room_builder in rooms_builders:
        #     knx_config
                        # if dev_key in
        return rooms



async def user_input_loop(room1):
    while True:
        command = await aioconsole.ainput(">>> What do you want to do?\n")
        if command[:3] == 'set': #FunctionalModule
            name = command[4:]
            for in_room_device in room1.devices:
                if in_room_device.name == name:
                    if not isinstance(in_room_device.device, dev.FunctionalModule):
                        print("[ERROR] Users can only act on a Functional Module")
                        break
                    in_room_device.device.user_input()
        elif command[:3] == 'get': #Sensor
            name = command[4:]
            if "bright" in name: # brightness sensor
                for in_room_device in room1.devices:
                    if in_room_device.name == name:
                        print("\n=> The brightness received on sensor %s located at (%d,%d) is %.2f\n" % (name, in_room_device.get_x(), in_room_device.get_y(), room1.world.ambient_light.read_brightness(in_room_device)))
        elif command in ('h', 'H'):
            print(COMMAND_HELP)
        elif command in ('q','Q'):
            break
        else:
            print("[ERROR] Unknown input, please " + COMMAND_HELP)


async def async_main(loop, room1):
    ui_task = loop.create_task(user_input_loop(room1))
    await asyncio.wait([ui_task])



if __name__ == "__main__":
    GUI_MODE = False
    FILE_CONFIG_MODE = True
    # CONFIG_PATH = "simulation_config.json"
    config_file_path = CONFIG_PATH

    # System configuration based on a JSON config file
    if FILE_CONFIG_MODE:
        rooms = configure_system_from_file(config_file_path)

    # Dynamic system configuration from user input
    else:
        while(True): # waits for the input to be a correct speed factor, before starting the simulation
            try:
                simulation_speed_factor = float(input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n"))
                break
            except ValueError:
                print("[ERROR] The simulation speed should be a number")
                continue

        print(COMMAND_HELP)
        rooms = configure_system(simulation_speed_factor)

    room1 = rooms[0] # for now only one room

    # GUI interface with the user
    if GUI_MODE: #########TODO: setup devices on the GUI ##########
        window = gui.GUIWindow()
        start_time = time.time()
        for room in rooms:
            room.world.time.start_time = start_time
        # sim.Time.start_time = time.time() # give the start time to Time object, avoid to pass it in the scheduler call
        # sim.Time.speed_factor = simulation_speed_factor # same for the speed factor
        # TODO: implement for multiple rooms
        room1.window = window # same for the GU window object, but to room1 object
        pyglet.clock.schedule_interval(room1.update_world, interval=1, gui_mode=True) # update every 1seconds, corresponding to 1 * speed_factor real seconds
        try:
            pyglet.app.run()
        except (KeyboardInterrupt, SystemExit):
            print("\nThe simulation program has been ended.")
            exit()
        print("The GUI window has been closed and the simulation terminated.")

    # Terminal interface with the user (no visual feedback)
    else: # run the simulation without the GUI window
        # Configure the start_time attribute of rooms' Time object
        start_time = time.time()
        for room in rooms:
            room.world.time.start_time = start_time
        # TODO: implement for multiple rooms
        room1.world.time.scheduler_init()
        room1.world.time.scheduler_add_job(room1.update_world) # we pass the update function as argument to the Time class object
        room1.world.time.scheduler_start()

        try:
            loop = asyncio.get_event_loop()
            #app = ui.GraphicalUserInterface(loop)
            #app.mainloop()
            # TODO: implement for multiple rooms
            loop.run_until_complete(async_main(loop, room1))
        except (KeyboardInterrupt, SystemExit):
            print("\nThe simulation program has been ended.")
