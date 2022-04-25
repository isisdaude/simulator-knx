"""
Simple simulator prototype.
"""

import functools
import asyncio, aioconsole
import time, datetime, sys
import pyglet
import json
import logging
import aioreactive as rx
from pynput import keyboard
from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import system
import gui
import devices as dev
import simulation as sim
import user_interface as ui
from system import IndividualAddress, Telegram, GroupAddress, configure_system, configure_system_from_file, user_command_parser


CONFIG_PATH = "simulation_config.json"
# Configure logging messages format
LOGGING_LEVEL = logging.INFO



async def user_input_loop(room):
    while True:
        command = await aioconsole.ainput(">>> What do you want to do?\n")
        if not (user_command_parser(command, room)):
            break

async def async_main(loop, room):
    ui_task = loop.create_task(user_input_loop(room))
    await asyncio.wait([ui_task])


if __name__ == "__main__":
    GUI_MODE = True
    FILE_CONFIG_MODE = True
    DEV_CONFIG = False
    CONFIG_PATH = "simulation_config.json"
    config_file_path = CONFIG_PATH
    logging.basicConfig(level=LOGGING_LEVEL, format='%(asctime)s |%(name)s| [%(levelname)s] -- %(message)s') #%(name)s : username (e.g. root)

    # System configuration based on a JSON config file
    if FILE_CONFIG_MODE:
        rooms = configure_system_from_file(config_file_path)

    # System configuration from function configure_system
    elif DEV_CONFIG:
        while(True): # Waits for the input to be a correct speed factor, before starting the simulation
            try:
                simulation_speed_factor = float(input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n"))
                break
            except ValueError:
                logging.warning("The simulation speed should be a number")
                continue
        rooms = configure_system(simulation_speed_factor)

    else:
        while(True): # Waits for the input to be a correct speed factor, before starting the simulation
            try:
                simulation_speed_factor = float(input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n"))
                break
            except ValueError:
                logging.warning("The simulation speed should be a number")
                continue
        rooms = [system.Room("bedroom1", 20, 20, 3, simulation_speed_factor)]

    room1 = rooms[0] # for now only one room

    # GUI interface with the user
    if GUI_MODE: #########TODO: setup devices on the GUI ##########
                ##########TODO: and parser of command through gui ######
        window = gui.GUIWindow(room1)###
        window.initialize_system()
        start_time = time.time()
        for room in rooms:
            room.world.time.start_time = start_time
        # TODO: implement for multiple rooms
        room1.window = window # same for the GUi window object, but to room1 object
        pyglet.clock.schedule_interval(room1.update_world, interval=1, gui_mode=True) # update every 1seconds, corresponding to 1 * speed_factor real seconds
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
