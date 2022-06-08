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


import pprint
pp=pprint.PrettyPrinter(compact=True)

# Local application imports
import gui
import system
import tools
from svshi_interface.main import Interface
from tools.config_tools import * # GUI_MODE, CLI_INT_MODE, SAVED_CONFIG_PATH, ...



def launch_simulation(argv):
    # Parser CLI arguments given by the user when launching the program
    INTERFACE_MODE, COMMAND_MODE, SCRIPT_PATH, CONFIG_MODE, CONFIG_PATH, SVSHI_MODE, TELEGRAM_LOGGING = tools.arguments_parser(argv)
    
    # System configuration from function configure_system
    if CONFIG_MODE == DEV_CONFIG:
        while(True): # Waits for the input to be a correct speed factor, before starting the simulation
            simulation_speed_factor = input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n")
            if tools.check_simulation_speed_factor(simulation_speed_factor):
                break
        room1, system_dt = tools.configure_system(simulation_speed_factor, svshi_mode=SVSHI_MODE, telegram_logging=TELEGRAM_LOGGING)
    # Default, empty or file config
    else:
        CONFIG_PATH = DEFAULT_CONFIG_PATH if CONFIG_MODE == DEFAULT_CONFIG else CONFIG_PATH
        CONFIG_PATH = EMPTY_CONFIG_PATH if CONFIG_MODE == EMPTY_CONFIG else CONFIG_PATH
        room1, system_dt = tools.configure_system_from_file(CONFIG_PATH, svshi_mode=SVSHI_MODE, telegram_logging=TELEGRAM_LOGGING)


    # GUI interface with the user
    if INTERFACE_MODE == GUI_MODE:
        window = gui.GUIWindow(CONFIG_PATH, DEFAULT_CONFIG_PATH, EMPTY_CONFIG_PATH, SAVED_CONFIG_PATH, room1, svshi_mode=SVSHI_MODE, telegram_logging=TELEGRAM_LOGGING) #CONFIG_PATH can be a normal file, default or empty
        window.initialize_system(save_config=True, system_dt=system_dt) #system_dt is delta time for scheduling update_world
        print("\n>>> The simulation is started in Graphical User Interface Mode <<<\n")
        start_time = time.time()
        room1.world.time.start_time = start_time 
        try:
            #loop = asyncio.new_event_loop()
            pyglet.app.run()
        except (KeyboardInterrupt, SystemExit):
            print("\nThe simulation program has been ended.")
            sys.exit()
        print("The GUI window has been closed and the simulation terminated.")

    # Terminal interface with the user (no visual feedback)
    elif INTERFACE_MODE == CLI_INT_MODE: # run the simulation without the GUI window
        # Configure the start_time attribute of room's Time object
        start_time = time.time()
        room1.world.time.start_time = start_time
        room1.world.time.scheduler_init()
        room1.world.time.scheduler_add_job(room1.update_world) # we pass the update function as argument to the Time class object for scheduling
        room1.world.time.scheduler_start()

        try:
            loop = asyncio.get_event_loop()
            print("\n>>> The simulation is started in Command Line Interface Mode (no visual feedback) <<<")
            loop.run_until_complete(async_main(loop, room1, COMMAND_MODE, SCRIPT_PATH))
        except (KeyboardInterrupt, SystemExit):
            loop.run_until_complete(kill_tasks())
        finally:
            loop.run_until_complete(kill_tasks())
            loop.close()
            logging.info("Simulation Terminated")
            print("\nThe simulation program has been ended.")
            sys.exit(1)


async def user_input_loop(room):
    """Asyncio loop to await user command from terminal"""
    while True:
        message = ">>> What do you want to do?\n"
        command = await aioconsole.ainput(message)
        if tools.user_command_parser(command, room) is None:
            # # await kill_tasks()
            # return None
            sys.exit(1)

async def simulator_script_loop(room, file_path):
    """Asyncio loop to await user command from a .txt script"""
    script_parser = tools.ScriptParser()
    with open(file_path, "r") as f:
        commands = f.readlines()
        for command in commands: 
            ret, assertions = await script_parser.script_command_parser(room, command)
            if ret is None:
                logging.warning("The script has failed.")
                print("Failed script recap:")
                pp.pprint(assertions)
                return 0
            elif ret == 0: # ret=0 is signal from end command to termninate script
                logging.info("The script has completed successfully.")
                print("Successful script recap:")
                pp.pprint(assertions)
                return 1
        if ret is not None: # of no end command, script ends when no more commands/lines
            logging.info("The script has completed successfully.")
            print("Successful script recap:")
            pp.pprint(assertions)
            return 1

async def kill_tasks():
    """Function called to kill task when program ended"""
    try:
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task 
    except AttributeError:
        return None


async def async_main(loop, room, command_mode, script_path):
    """ Manager function of asyncio tasks"""
    tasks = []
    if command_mode == CLI_COM_MODE:
        print(">>>>>> The Command mode is set to CLI (commands through terminal)")
        ui_task = loop.create_task(user_input_loop(room))
        tasks.append(ui_task) 
    elif command_mode == SCRIPT_MODE:
        print(">>>>>> The Command mode is set to SCRIPT (commands from .txt script file)")
        script_task = loop.create_task(simulator_script_loop(room, script_path))
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
        


