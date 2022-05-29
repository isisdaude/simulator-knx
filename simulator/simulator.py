"""
Simple simulator prototype.
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]

# Standard library imports
#sys, os, io, time, datetime, ast, abc, dataclasses, json, copy, typing, math, logging, shutil, itertools, functools, numbers, collections, enum
import functools
import asyncio, aioconsole, signal
import time, datetime, sys, os
import pyglet
import json
import logging, threading
import aioreactive as rx

# Third party imports
from pathlib import Path
from pynput import keyboard
from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler




# Local application imports
# import devices as dev
# import simulation as sim
import gui
import system
from interface.main import Interface

# SCRIPT_DIR = os.path.dirname(__file__)
# SAVED_CONFIG_PATH = os.path.join(SCRIPT_DIR,"/docs/config/")

SAVED_CONFIG_PATH = os.path.abspath("docs/config/") + '/'
# print(SAVED_CONFIG_PATH)
CONFIG_PATH = "./docs/config/sim_config_bedroom.json"
# CONFIG_PATH = "./docs/config/saved_config_09052022_042903"
DEFAULT_CONFIG_PATH = "./docs/config/default_config.json"
EMPTY_CONFIG_PATH = "./docs/config/empty_config.json"

SCRIPT = "FullScript"
SCRIPT_FILE_PATH = "./docs/scripts/" + SCRIPT + ".txt" 
# Configure logging messages format
LOGGING_LEVEL = logging.WARNING


## User command mode (script or CLI)
GUI_MODE = 0
TERMINAL_MODE = 1
INTERFACE_MODE = TERMINAL_MODE # or TERMINAL_MODE
## User interface mode
SCRIPT_MODE = 0
CLI_MODE = 1
COMMAND_MODE = SCRIPT_MODE # only if  INTERFACE_MODE = TERMINAL_MODE
## Configuration mode
FILE_CONFIG = 0   # configuration from json file
DEFAULT_CONFIG = 1 # configuration from default json file (~3devices)
EMPTY_CONFIG = 2 # configuration with no devices
DEV_CONFIG = 3 # configuration from python function
CONFIG_MODE = FILE_CONFIG

def launch_simulation():
    GUI_MODE = True 
    ## TODO implement  kind of a switch for config (flag config_mode that wan be equak tto DEFAUK, FILE, or EMPTY)
    default_mode = False
    empty_mode = False
    SYSTEM_DT = 1
    logging.basicConfig(level=LOGGING_LEVEL, format='%(asctime)s | [%(levelname)s] -- %(message)s') #%(name)s : username (e.g. root)

    # System configuration based on a JSON config file
    if CONFIG_MODE == FILE_CONFIG:
        rooms = system.configure_system_from_file(CONFIG_PATH, SYSTEM_DT)

    # System configuration from function configure_system
    elif CONFIG_MODE == DEV_CONFIG:
        while(True): # Waits for the input to be a correct speed factor, before starting the simulation
            simulation_speed_factor = input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n")
            if system.check_simulation_speed_factor(simulation_speed_factor):
                break
        rooms = system.configure_system(simulation_speed_factor, SYSTEM_DT)

    # System configuration based on a default JSON config file
    elif CONFIG_MODE == DEFAULT_CONFIG:
        default_mode = True
        rooms = system.configure_system_from_file(DEFAULT_CONFIG_PATH, SYSTEM_DT)
    
    # System configuration based on a default JSON config file
    elif CONFIG_MODE  == EMPTY_CONFIG:
        empty_mode = True
        rooms = system.configure_system_from_file(EMPTY_CONFIG_PATH, SYSTEM_DT)

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

    # # We save the config path to further reload the simulation
    # for room in rooms:
    #     room.SAVED_CONFIG_PATH = SAVED_CONFIG_PATH
    # room1 = rooms[0] # for now only one room

    # GUI interface with the user
    if INTERFACE_MODE == GUI_MODE:
        if default_mode:
            config_path = DEFAULT_CONFIG_PATH
        elif empty_mode:
            config_path = EMPTY_CONFIG_PATH
        else:
            config_path = CONFIG_PATH
        window = gui.GUIWindow(config_path, DEFAULT_CONFIG_PATH, EMPTY_CONFIG_PATH, SAVED_CONFIG_PATH, rooms)###
        window.initialize_system(save_config=True, system_dt=SYSTEM_DT) #system_dt is delta time for scheduling update_world
        start_time = time.time()
        for room in rooms:
            room.world.time.start_time = start_time
        room1 = rooms[0] # NOTE: implementation for multiple rooms using the rooms list
        try:
            i = Interface()
            loop = asyncio.new_event_loop()
            interface_thread = threading.Thread(target=background_loop, args=(loop,), daemon=True)
            interface_thread.start()
            interface_task = asyncio.run_coroutine_threadsafe(i.main(room1), loop)
            pyglet.app.run()
        except (KeyboardInterrupt, SystemExit):
            print("\nThe simulation program has been ended.")
            interface_task.cancel()
            sys.exit()
        print("The GUI window has been closed and the simulation terminated.")

    # Terminal interface with the user (no visual feedback)
    elif INTERFACE_MODE == CLI_MODE: # run the simulation without the GUI window
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
            i = Interface()
            loop = asyncio.get_event_loop()
            interface_thread = threading.Thread(target=background_loop, args=(loop,), daemon=True)
            interface_thread.start()
            interface_task = asyncio.run_coroutine_threadsafe(i.main(room1), loop)
            # signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
            # for s in signals:
            #     loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))
            #app = ui.GraphicalUserInterface(loop)
            #app.mainloop()
            # TODO: implement for multiple rooms
            loop.run_until_complete(async_main(loop, room1))
        except (KeyboardInterrupt, SystemExit):
            loop.run_until_complete(kill_tasks())
        finally:
            loop.run_until_complete(kill_tasks())
            loop.close()
            logging.info("Simulation Terminated")
            print("\nThe simulation program has been ended.")
            sys.exit(1)


def background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def user_input_loop(room):
    while True:
        # global script_mode
        # if verif_mode:
        #     message = ''
        # else:
        message = ">>> What do you want to do?\n"
        command = await aioconsole.ainput(message)
        if system.user_command_parser(command, room) is None:
            # await kill_tasks()
            return None
            # sys.exit(1)

async def simulator_script_loop(room, file_path):
    script_parser = system.ScriptParser()
    # global script_mode
    with open(file_path, "r") as f:
        commands = f.readlines()
        for command in commands:
            if SCRIPT_MODE:
                print("\n>>> Next command?")
            command = command.strip().lower() # remove new line symbol and put in lower case
            print(f"Command >>> '{command}' <<<")
            await script_parser.script_command_parser(room, command)
            # script_state = 
            # if script_state is None:
            #     # await kill_tasks()
            #     script_mode = False
            #     return None
                # sys.exit(1)

async def kill_tasks():
    try:
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task 
    except AttributeError:
        return None

async def async_main(loop, room):
    tasks = []
    if COMMAND_MODE == CLI_MODE:
        ui_task = loop.create_task(user_input_loop(room))
        tasks.append(ui_task) 
    if COMMAND_MODE == SCRIPT_MODE:
        script_task = loop.create_task(simulator_script_loop(room, SCRIPT_FILE_PATH))
        tasks.append(script_task) 

    await asyncio.wait(tasks)


if __name__ == "__main__":
    launch_simulation()

# async def shutdown(signal, loop):
#     """Cleanup tasks tied to the service's shutdown."""
#     logging.info(f"Received exit signal {signal.name}...")
#     tasks = [t for t in asyncio.all_tasks() if t is not
#              asyncio.current_task()]

#     [task.cancel() for task in tasks]

#     logging.info(f"Cancelling {len(tasks)} outstanding tasks")
#     await asyncio.gather(*taskss, return_exceptions=True)
#     logging.info(f"Flushing metrics")
#     loop.stop()
#     print("\nThe simulation program has been ended.")
#     sys.exit(1)
        


