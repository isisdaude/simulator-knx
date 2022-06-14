"""
Main module, managing start of simulator in selected or default mode, launch of scheduler and GUI, and initialization of system through room.
"""

# Standard library imports
import logging
import sys
import time

# Third party imports
import aioconsole
import asyncio
import pprint
import pyglet
from contextlib import suppress

# Local application imports
import gui
import tools
import tools.config_tools as ct
from system.room import Room

pp = pprint.PrettyPrinter(compact=True)


def launch_simulation(argv) -> None:
    """Launch simulation with the correct modes of configuration, command and interface."""
    # Parsed CLI arguments given by the user when launching the program
    (
        INTERFACE_MODE,
        COMMAND_MODE,
        SCRIPT_PATH,
        CONFIG_MODE,
        CONFIG_PATH,
        SVSHI_MODE,
        TELEGRAM_LOGGING,
    ) = tools.arguments_parser(argv)

    # System configuration from function configure_system()
    if CONFIG_MODE == ct.DEV_CONFIG:
        while True:
            simulation_speed_factor = input(
                ">>> What speed would you like to set for the simulation?  [simulated_time = speed * system_dt]\n"
            )
            if tools.check_simulation_speed_factor(simulation_speed_factor):
                break
        room1, system_dt = tools.configure_system(
            simulation_speed_factor,
            svshi_mode=SVSHI_MODE,
            telegram_logging=TELEGRAM_LOGGING,
        )
    # Default, empty or file config from function congirue_system_from_file()
    else:
        CONFIG_PATH = (
            ct.DEFAULT_CONFIG_PATH if CONFIG_MODE == ct.DEFAULT_CONFIG else CONFIG_PATH
        )
        CONFIG_PATH = (
            ct.EMPTY_CONFIG_PATH if CONFIG_MODE == ct.EMPTY_CONFIG else CONFIG_PATH
        )
        room1, system_dt = tools.configure_system_from_file(
            CONFIG_PATH, svshi_mode=SVSHI_MODE, telegram_logging=TELEGRAM_LOGGING
        )

    # GUI interface with the user
    if INTERFACE_MODE == ct.GUI_MODE:
        window = gui.GUIWindow(
            CONFIG_PATH,
            ct.DEFAULT_CONFIG_PATH,
            ct.EMPTY_CONFIG_PATH,
            ct.SAVED_CONFIG_PATH,
            room1,
            svshi_mode=SVSHI_MODE,
            telegram_logging=TELEGRAM_LOGGING,
        )  # CONFIG_PATH can be a normal file, default or empty
        window.initialize_system(
            save_config=True, system_dt=system_dt
        )  # system_dt is delta time for scheduling update_world
        print("\n>>> The simulation is started in Graphical User Interface Mode <<<\n")
        start_time = time.time()
        room1.world.time.start_time = start_time
        try:
            pyglet.app.run()
        except (KeyboardInterrupt, SystemExit):
            print("\nThe simulation program has been ended.")
            sys.exit()
        print("The GUI window has been closed and the simulation terminated.")

    # Terminal interface with the user (no visual feedback)
    elif INTERFACE_MODE == ct.CLI_INT_MODE:
        room1.world.time.scheduler_init()
        room1.world.time.scheduler_add_job(
            room1.update_world
        )  # we pass the update function as argument to the Time class object for scheduling
        room1.world.time.scheduler_start()  # set also start_time of world.time object

        try:
            loop = asyncio.get_event_loop()
            print(
                "\n>>> The simulation is started in Command Line Interface Mode (no visual feedback) <<<"
            )
            loop.run_until_complete(async_main(loop, room1, COMMAND_MODE, SCRIPT_PATH))
        except (KeyboardInterrupt, SystemExit):
            loop.run_until_complete(kill_tasks())
        finally:
            loop.run_until_complete(kill_tasks())
            loop.close()
            logging.info("Simulation Terminated.")
            print("\nThe simulation program has been ended.")
            sys.exit(1)


async def user_input_loop(room: Room) -> None:
    """Asyncio loop to await user command from terminal"""
    while True:
        message = ">>> What do you want to do?\n"
        command = await aioconsole.ainput(message)
        if tools.user_command_parser(command, room) is None:
            sys.exit(1)


async def simulator_script_loop(room: Room, file_path: str) -> int:
    """Asyncio loop to await user command from a .txt script"""
    script_parser = tools.ScriptParser()
    with open(file_path, "r") as f:
        commands = f.readlines()
        for command in commands:
            ret, assertions = await script_parser.script_command_parser(room, command)
            if ret is None:
                logging.warning("The script has failed.")
                print("Failed script recap:")
                pp.pprint(script_parser.stored_values)
                pp.pprint(assertions)
                return 0
            elif ret == 0:  # ret=0 is signal from end command to termninate script
                logging.info("The script has completed successfully.")
                print("Successful script recap:")
                pp.pprint(script_parser.stored_values)
                pp.pprint(assertions)
                return 1
        if (
            ret is not None
        ):  # if no end command, script ends when no more commands/lines
            logging.info("The script has completed successfully.")
            print("Successful script recap:")
            pp.pprint(script_parser.stored_values)
            pp.pprint(assertions)
            return 1


async def kill_tasks() -> None:
    """Function called to kill task when program ended"""
    try:
        pending = asyncio.Task.all_tasks()
        for task in pending:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
    except AttributeError:
        return None


async def async_main(loop, room: Room, command_mode: str, script_path: str) -> None:
    """Manager function of asyncio tasks

    loop : asyncio get event loop
    """
    tasks = []
    if command_mode == ct.CLI_COM_MODE:
        print(">>>>>> The Command mode is set to CLI (commands through terminal)")
        ui_task = loop.create_task(user_input_loop(room))
        tasks.append(ui_task)
    elif command_mode == ct.SCRIPT_MODE:
        print(
            ">>>>>> The Command mode is set to SCRIPT (commands from .txt script file)"
        )
        script_task = loop.create_task(simulator_script_loop(room, script_path))
        tasks.append(script_task)
    await asyncio.wait(tasks)


if __name__ == "__main__":
    launch_simulation()
