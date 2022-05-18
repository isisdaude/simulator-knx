"""
Simple simulator prototype.
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]

# Standard library imports
#sys, os, io, time, datetime, ast, abc, dataclasses, json, copy, typing, math, logging, shutil, itertools, functools, numbers, collections, enum
import functools
import asyncio, aioconsole
import time, datetime, sys, os
import pyglet
import json
import logging
import aioreactive as rx

# Third party imports
from pathlib import Path
from pynput import keyboard
# from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Local application imports
# import devices as dev
# import simulation as sim
import gui
import system

# SCRIPT_DIR = os.path.dirname(__file__)
# SAVED_CONFIG_PATH = os.path.join(SCRIPT_DIR,"/docs/config/")

SAVED_CONFIG_PATH = os.path.abspath("docs/config/") + '/'
# print(SAVED_CONFIG_PATH)
CONFIG_PATH = "./docs/config/simulation_config.json"
# CONFIG_PATH = "./docs/config/saved_config_09052022_042903"
DEFAULT_CONFIG_PATH = "./docs/config/default_config.json"
# Configure logging messages format
LOGGING_LEVEL = logging.INFO



async def user_input_loop(room):
    while True:
        command = await aioconsole.ainput(">>> What do you want to do?\n")
        if not (system.user_command_parser(command, room)):
            break

async def async_main(loop, room):
    ui_task = loop.create_task(user_input_loop(room))
    await asyncio.wait([ui_task])


def launch_simulation():
    GUI_MODE = True
    FILE_CONFIG_MODE = True
    DEV_CONFIG = False
    default_mode = False
    DEFAULT_CONFIG = True
    SYSTEM_DT = 1
    logging.basicConfig(level=LOGGING_LEVEL, format='%(asctime)s | [%(levelname)s] -- %(message)s') #%(name)s : username (e.g. root)

    # System configuration based on a JSON config file
    if FILE_CONFIG_MODE:
        rooms = system.configure_system_from_file(CONFIG_PATH, SYSTEM_DT)

    # System configuration from function configure_system
    elif DEV_CONFIG:
        while(True): # Waits for the input to be a correct speed factor, before starting the simulation
            simulation_speed_factor = input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n")
            if system.check_simulation_speed_factor(simulation_speed_factor):
                break
        rooms = system.configure_system(simulation_speed_factor, SYSTEM_DT)

    # System configuration based on a default JSON config file
    elif DEFAULT_CONFIG:
        default_mode = True
        rooms = system.configure_system_from_file(DEFAULT_CONFIG_PATH, SYSTEM_DT)

    # System configuration based on a simple Room with no devices
    else:
        while(True): # Waits for the input to be a correct speed factor, before starting the simulation
            try:
                simulation_speed_factor = float(input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n"))
                break
            except ValueError:
                logging.warning("The simulation speed should be a number")
                continue
        rooms = [system.Room("bedroom1", 20, 20, 3, simulation_speed_factor, '3-levels')]

    # We save the config path to further reload the simulation
    for room in rooms:
        room.SAVED_CONFIG_PATH = SAVED_CONFIG_PATH
    room1 = rooms[0] # for now only one room

    # GUI interface with the user
    if GUI_MODE:
        config_path = DEFAULT_CONFIG_PATH if default_mode else CONFIG_PATH
        window = gui.GUIWindow(config_path, DEFAULT_CONFIG_PATH, rooms)###
        window.initialize_system(SAVED_CONFIG_PATH, SYSTEM_DT) #system_dt is delta time for scheduling update_world
        start_time = time.time()
        for room in rooms:
            room.world.time.start_time = start_time
        # TODO: implement for multiple rooms
        try:
            pyglet.app.run()
        except (KeyboardInterrupt, SystemExit):
            print("\nThe simulation program has been ended.")
            sys.exit()
        print("The GUI window has been closed and the simulation terminated.")

    # Terminal interface with the user (no visual feedback)
    else: # run the simulation without the GUI window
        # Configure the start_time attribute of rooms' Time object
        start_time = time.time()
        for room in rooms:
            room.world.time.start_time = start_time
        # TODO: implement for multiple rooms
        room1 = rooms[0]
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


if __name__ == "__main__":
    launch_simulation()