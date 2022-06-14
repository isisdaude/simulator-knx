"""
Module that define functions for parsing user commands, CLI arguments or API scripts.
"""

import logging
import numbers
import pprint
from typing import Tuple, Union, Dict

import argparse
import asyncio

import devices as dev

pp = pprint.PrettyPrinter(compact=True)


COMMAND_HELP = (
    "Command Syntax: \n"
    "- switch state: 'set [device_name] [ON/OFF] [value]'\n"
    "- read state: 'getvalue [device_name]'\n"
    "- system info: 'getinfo [device_name]' or 'getinfo world [ambient]'\n"
    "- exit: 'q' to quit the program\n"
    "- help: 'h' for help"
)


def arguments_parser(argv) -> Tuple[str, str, str, str, str, bool, bool]:
    """Function to parse CLI arguments given by the user when launching the program"""
    parser = argparse.ArgumentParser(
        description="Process Interface, Command, Config and Logging modes.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Logging argument definition
    parser.add_argument(
        "-l",
        "--log",
        action="store",
        default="WARNING",
        type=str.upper,
        choices=logging._nameToLevel.keys(),
        help=(
            "Provide logging level.\nExample '-l debug' or '--log=DEBUG'\n-> default='WARNING'."
        ),
    )
    ## TODO, add log file destination option
    # Interface argument definition
    parser.add_argument(
        "-i",
        "--interface",
        action="store",
        default="gui",
        type=str.lower,
        choices=["gui", "cli"],
        help=(
            "Provide user interface mode.\nExample '-i cli' or '--interface=cli'\n-> default='gui'."
        ),
    )
    # Command argument definition
    parser.add_argument(
        "-c",
        "--command-mode",
        action="store",
        default="cli",
        type=str.lower,
        choices=["script", "cli"],
        help=(
            "Provide command mode (only if interface mode is CLI).\nExample '-c script' or '--command-mode=script'\n-> default='cli'"
        ),
    )
    # Config File Name argument definition
    parser.add_argument(
        "-f",
        "--filescript-name",
        action="store",
        default="full_script",
        type=str.lower,
        help=(
            "Provide script file name (without .txt extension).\nExample '-F full_script' or '--file-name=full_script'\n-> default='full_script'"
        ),
    )
    # Config argument definition
    parser.add_argument(
        "-C",
        "--config-mode",
        action="store",
        default="file",
        type=str.lower,
        choices=["file", "default", "empty", "dev"],
        help=(
            "Provide configuration mode.\nExample '-C file' or '--command-mode=empty'\n-> default='file'"
        ),
    )
    # Config File Name argument definition
    parser.add_argument(
        "-F",
        "--fileconfig-name",
        action="store",
        default="sim_config_bedroom",
        type=str.lower,
        help=(
            "Provide configuration file name (without .json extension).\nExample '-F sim_config_bedroom' or '--file-name=sim_config_bedroom'\n-> default='sim_config_bedroom'"
        ),
    )
    # SVSHI mode argument definition
    parser.add_argument(
        "-s",
        "--svshi-mode",
        action="store_true",  # svshi_mode=True if option, False if no -s option
        help=(
            "Specifies that SVSHI program will be used, start a thread to communicate with it."
        ),
    )
    # Telegram logging mode argument definition
    parser.add_argument(
        "-t",
        "--telegram-logging",
        action="store_true",  # telegram_logging=True if option, False if no -t option
        help=(
            "Specifies that the telegrams sent and received should be logged in a file located in logs/ folder"
        ),
    )

    # Get the arguments from command line
    options = parser.parse_args()
    config = vars(options)
    # logging.info(f"CLI arguments config: {config}")
    print(f"CLI arguments config: {config}")

    # Logging level argument parser
    logging.basicConfig(
        level=options.log.upper(), format="%(asctime)s | [%(levelname)s] -- %(message)s"
    )  #%(name)s : username (e.g. root)
    # Interface mode argument parser
    INTERFACE_MODE = options.interface.lower()
    # Command mode argument parser
    COMMAND_MODE = options.command_mode.lower()
    # Script File Name argument parser
    FILESCRIPT_NAME = options.filescript_name
    SCRIPT_PATH = "./scripts/" + FILESCRIPT_NAME + ".txt"
    # Config mode argument parser
    CONFIG_MODE = options.config_mode.lower()
    # Config File Name argument parser
    FILECONFIG_NAME = options.fileconfig_name
    CONFIG_PATH = "./config/" + FILECONFIG_NAME + ".json"
    # SVSHI mode argument parser
    SVSHI_MODE = options.svshi_mode
    # TELEGRAM_LOGGING mode argument parser
    TELEGRAM_LOGGING = options.telegram_logging

    return (
        INTERFACE_MODE,
        COMMAND_MODE,
        SCRIPT_PATH,
        CONFIG_MODE,
        CONFIG_PATH,
        SVSHI_MODE,
        TELEGRAM_LOGGING,
    )


def user_command_parser(command: str, room) -> Union[int, None]:  # room : Room
    """
    Parser function for CLI commands with the user through the terminal or GUI command box.

    Simulator terminates if return None,
    Return 0 or 1: indicates that a problem occured and the command was not considered,
    script_command_parser uses it to return None or 1 and propagated the error.
    """
    command = command.strip()  # remove start and end spaces
    command_split = command.split(" ")
    if (
        command.isspace() or len(command) == 0
    ):  # if user pressed enter without any command
        return 1
    if len(command):
        print(f"\nCommand >>>'{command}'<<<", flush=True)
    # User action on Functional Module
    if command_split[0] == "set":
        print(f"\set:> {command[4:]}")
        name = command_split[1]
        # If no ON/OFF state or value specified, we simply switch the state of the device
        if len(command_split) == 2:
            for in_room_device in room.devices:
                if in_room_device.name in name:
                    if not isinstance(in_room_device.device, dev.FunctionalModule):
                        logging.warning(
                            "Users can only interact with a Functional Module."
                        )
                        return 0
                    in_room_device.device.user_input()
                    return 1
            # If device not found
            logging.warning(f"The device {name} is not found in room's devices list.")
            return 0
        # If user gives ON/OFF state and/or value
        elif len(command_split) >= 3:
            if command_split[2].lower() not in ["on", "off"]:
                logging.warning(
                    "The command is not recognized by the parser: either wrong or incomplete."
                )
                print(COMMAND_HELP)
                return 0
            state = True if command_split[2].lower() == "on" else False
            for in_room_device in room.devices:
                if in_room_device.name in name:
                    if not isinstance(in_room_device.device, dev.FunctionalModule):
                        logging.warning(
                            "Users can only interact with a Functional Module."
                        )
                        return 0
                    # User gives ON/OFF state and value (e.g. for dimmer)
                    if len(command_split) == 4:
                        state_ratio = int(command_split[3])
                        if state_ratio < 0 or 100 < state_ratio:
                            logging.warning(
                                f"The value '{state_ratio}' given should be a ratio (0-100), the command is incorrect."
                            )
                            return 0
                        in_room_device.device.user_input(
                            state=state, state_ratio=state_ratio
                        )
                    # User gives only ON/OFF state
                    else:
                        in_room_device.device.user_input(state=state)
                    return 1
            # If device not found
            logging.warning(f"The device {name} is not found in room's devices list.")
            return 0
    # System information asked by the user
    elif command_split[0] == "getinfo" or command.strip() == "getinfo":
        # Global info info asked by user
        if (
            command.strip() == "getinfo"
        ):  # only 'getinfo' keyword -> we give all info to user (exceot device specific info)
            world_dict = room.get_world_info("all")

            print("> World information:")
            pp.pprint(world_dict)
            room_dict = room.get_room_info()

            print("> Room information:")
            pp.pprint(room_dict)
            bus_dict = room.get_bus_info()

            print("> Bus information:")
            pp.pprint(bus_dict)
            return 1
        print(f"\getinfo:> {command[8:]}")
        # World info asked by user
        if "world" in command_split[1]:
            if len(command_split) > 2:
                ambient = command_split[
                    2
                ]  # can be 'time', 'temperature', 'humidity', 'co2', 'co2', 'brightness', 'all'
                if len(ambient) >= len(
                    "all"
                ):  # smallest str acceptable after 'getinfo world' command
                    if "time" in ambient:
                        world_dict = room.get_world_info("time")
                    elif "weather" in ambient:
                        world_dict = room.get_world_info("weather")
                    elif "temperature" in ambient:
                        world_dict = room.get_world_info("temperature")
                    elif "humidity" in ambient:
                        world_dict = room.get_world_info("humidity")
                    elif "co2" in ambient:
                        world_dict = room.get_world_info("co2")
                    elif (
                        "brightness" in ambient
                    ):  # brightness is a global brightness from room's ground perspective
                        world_dict = room.get_world_info("brightness")
                    elif "out" in ambient:
                        world_dict = room.get_world_info("out")
                    elif "all" in ambient:
                        world_dict = room.get_world_info("all")
                    else:
                        logging.warning(
                            f"The option {ambient} is not supported with 'getinfo world' command"
                        )
                        return 0
            else:  # if nothing specified, just get all world info
                world_dict = room.get_world_info("all")
            pp.pprint(world_dict)
            return 1
        # Room info asked by user
        elif "room" in command_split[1]:
            if len(command_split) > 2:
                logging.warning(
                    f"'getinfo room' command expect no arguments, but {command_split[2]} was given."
                )
                return 0
            room_dict = room.get_room_info()
            pp.pprint(room_dict)
            return 1
        # Bus info asked by user
        elif "bus" in command_split[1]:
            if len(command_split) > 2:
                logging.warning(
                    f"'getinfo bus' command expect no arguments, but {command_split[2]} was given."
                )
                return 0
            bus_dict = room.get_bus_info()
            pp.pprint(bus_dict)
            return 1
        # Device specific info asked by user
        elif (
            len(command_split) > 1
        ):  # at least one keyword after 'getinfo' but None of the above
            if "dev" in command_split[1]:  # user ask for info on a device
                if len(command_split) > 2:
                    name = command_split[2]
                else:
                    logging.warning(
                        "The command is not recognized by the parser: either wrong or incomplete."
                    )
                    print(COMMAND_HELP)
                    return 0
            else:
                name = command_split[
                    1
                ]  # user ask for info on a device without using the dev keyword
            device_dict = room.get_device_info(name)
            if device_dict is not None:
                pp.pprint(device_dict)
            else:
                logging.warning(
                    f"Device {name} not found in Room or antoher problem occured when getting information on this device."
                )
                return 0
            return 1
        else:
            logging.warning(
                "The command is not recognized by the parser: either wrong or incomplete."
            )
            print(COMMAND_HELP)
            return 0
    elif command_split[0] == "getvalue":  # Sensor
        print(f"\getvalue:> {command[9:]}")
        name = command_split[1]
        for in_room_device in room.devices:
            if in_room_device.name in name:
                if not isinstance(in_room_device.device, dev.Sensor):
                    logging.warning(
                        "Users can only get the value read by a Sensor with 'getvalue' command."
                    )
                    return 0
                pp.pprint(in_room_device.device.get_dev_info(value=True))
                return 1
    elif command in ("h", "H", "help", "HELP"):
        print(COMMAND_HELP)
        return 1
    elif command in ("q", "Q", "quit", "QUIT"):
        return None
    else:
        logging.warning(
            "The command is not recognized by the parser: either wrong or incomplete."
        )
        print(COMMAND_HELP)
        return 0
    return 1


class ScriptParser:
    """Class to handle the parsing of script API commands from a txt file."""

    def __init__(self):
        """
        Initialization of a script parser object.

        stored_values : dict of variable stored during script
        assertions: dict of assertions that passed during script
        """
        self.stored_values = {}
        self.assertions = {}
        self.assert_counter = 0

    async def script_command_parser(
        self, room, command: str
    ) -> Tuple[Union[None, int], Dict[str, str]]:
        """Method handling parsing of commands from txt API script."""
        command = (
            command.strip().lower()
        )  # remove new line symbol and put in lower case
        if command.startswith("#") or len(command) == 0:  # comment line or empty line
            return 1, self.assertions
        print(f"Command >>> '{command}' <<<")
        command_split = command.split(" ")
        # 'wait' command
        if command.startswith("wait"):
            if len(command_split) == 3:
                if command_split[2] in [
                    "h",
                    "hour",
                    "hours",
                ]:  # time to wait in simulated hours, not computer seconds
                    speed_factor = room.world.time.speed_factor
                    sleep_time = int(
                        float(command_split[1]) * 3600 / speed_factor
                    )  # time to wait in computer system seconds
                elif command_split[2] in [
                    "m",
                    "minute",
                    "minutes",
                ]:  # time to wait in simulated minutes, not computer seconds
                    speed_factor = room.world.time.speed_factor
                    sleep_time = int(
                        float(command_split[1]) / 60 * 3600 / speed_factor
                    )  # time to wait in computer system seconds
                elif command_split[2] in [
                    "s",
                    "second",
                    "seconds",
                ]:  # time to wait in simulated seconds, not computer seconds
                    speed_factor = room.world.time.speed_factor
                    sleep_time = int(
                        float(command_split[1]) / 3600 * 3600 / speed_factor
                    )  # time to wait in computer system seconds
                else:
                    logging.error(
                        f"'wait' command expect 'h', 'm' or 's' as second argument, but {command_split[2]} was given."
                    )
                    return None, self.assertions
            elif len(command_split) == 2:
                try:
                    sleep_time = int(command_split[1])
                except (NameError, ValueError):
                    logging.error(
                        f"A number was excpected for the time to wait, but {command_split[1]} was given."
                    )
                    return None, self.assertions
            else:
                logging.warning(
                    f"'wait' command expect 1 or 2 arguments, but {len(command_split)-1} was given."
                )
                return None, self.assertions
            logging.info(f"[SCRIPT] Wait for {sleep_time} sec")
            await asyncio.sleep(sleep_time)
            return 1, self.assertions
        # 'store' command to keep one current system value in memory
        elif command.startswith("store"):
            if len(command_split) != 4:
                logging.error(
                    f"The 'store' command requires 3 arguments, but only {len(command_split)-1} were given."
                )
                return None, self.assertions
            if command_split[1] == "world":
                var_name = command_split[3]
                ambient = command_split[2].lower()
                try:
                    assert ambient in [
                        "simtime",
                        "temperature",
                        "humidity",
                        "co2",
                        "brightness",
                        "weather",
                    ]
                except AssertionError:
                    logging.error(
                        f"'store world' command expect ambient argument in ['simtime', 'temperature', 'humidity', 'co2', 'brightness', 'weather'], but {ambient} was given."
                    )
                    return None, self.assertions
                if ambient == "weather" or ambient == "simtime":
                    self.stored_values[var_name] = room.get_world_info(ambient=ambient)[
                        ambient
                    ]
                else:
                    self.stored_values[var_name] = round(
                        room.get_world_info(ambient=ambient, str_mode=False)[
                            ambient + "_in"
                        ],
                        2,
                    )
                if self.stored_values[var_name] is None:
                    return None, self.assertions
                logging.info(
                    f"[SCRIPT] The world {ambient} is stored in variable {var_name}={self.stored_values[var_name]}."
                )
                return 1, self.assertions
            else:  # store a device attribute/method result
                device_name = command_split[1]
                var_name = command_split[3]
                attribute = command_split[2].lower()
                self.stored_values[var_name] = room.get_device_info(
                    device_name, attribute=attribute
                )
                if self.stored_values[var_name] is None:
                    return None, self.assertions
                logging.info(
                    f"[SCRIPT] The device {attribute} is stored in variable {var_name}={self.stored_values[var_name]}."
                )
                return 1, self.assertions
        # 'assert' command
        elif command.startswith("assert"):
            if len(command_split) != 4:
                logging.error(
                    f"The 'assert' command requires 3 arguments, but only {len(command_split)-1} were given."
                )
                return None, self.assertions
            var_name = command_split[1]
            value = None
            if (
                command_split[3] in self.stored_values
            ):  # if we compare to a stored variable
                var = str(self.stored_values[command_split[3]])
                var_to_compare = command_split[3]
            else:  # if we compare to a value
                var = str(
                    command_split[3]
                )  # can be a bool, or a str for weather (e.g. 'clear')
                var_to_compare = "new_var"
            try:
                if "false" in var:
                    var = False
                elif "true" in var:
                    var = True
                elif var in ["clear", "overcast", "dark"]:
                    pass
                else:
                    var = float(var)
                    value = float(self.stored_values[var_name])
                if value is None:
                    value = self.stored_values[var_name]
                if command_split[2] == "==":
                    if type(value) == float:
                        var, value = str(var), str(value)
                    assert value == var
                elif command_split[2] == "!=":
                    assert value != var
                elif command_split[2] == "<=":
                    if type(var) == float:
                        assert value <= var
                    else:
                        logging.warning(
                            f"Cannot compare string or bool with inequality symbols."
                        )
                        return None, self.assertions
                elif command_split[2] == ">=":
                    if type(var) == float:
                        assert value >= var
                    else:
                        logging.warning(
                            f"Cannot compare string or bool with inequality symbols."
                        )
                        return None, self.assertions
                else:
                    logging.error(
                        f"The comparison sign should be in ['=='/'!='/'<='/'>='], but {command_split[2]} was given."
                    )
                    return None, self.assertions
                recap_str = (
                    f"({value}) {var_name} {command_split[2]} {var_to_compare} ({var})"
                )
                logging.info(f"[SCRIPT] The comparison '{recap_str}' is correct.")
                print(f"Assertion True")
                simtime = room.world.time.simulation_time(str_mode=True)
                self.assertions[
                    "Assertion True"
                    + str(self.assert_counter)
                    + " at simtime "
                    + str(simtime)
                ] = recap_str
                self.assert_counter += 1
                return 1, self.assertions
            except AssertionError:
                recap_str = f"({value}) {var_name} {command_split[2]} {var_to_compare} ({value})"
                logging.info(f"[SCRIPT] The comparison '{recap_str}' is not correct.")
                print(f"Assertion False")
                simtime = room.world.time.simulation_time(str_mode=True)
                self.assertions[
                    "Assertion False"
                    + str(self.assert_counter)
                    + " FAILED at simtime "
                    + str(simtime)
                ] = recap_str
                self.assert_counter += 1
                return None, self.assertions
        # 'set' command
        elif command.startswith("set"):
            if len(command_split) in [3, 4]:
                if command_split[1] in [
                    "temperature",
                    "humidity",
                    "co2",
                    "presence",
                    "weather",
                ]:  # set ambient state
                    value = command_split[2]
                    if command_split[1] == "presence":
                        if len(command_split) == 4:
                            logging.warning(
                                f" 'set presence' command accepts only 1 additional argument, but '{command_split[3]}' was given."
                            )
                            return None, self.assertions
                        ret = room.world.set_ambient_value("presence", value)
                    elif command_split[1] == "weather":
                        if len(command_split) == 4:
                            logging.warning(
                                f" 'set weather' command accepts only 1 additional argument, but '{command_split[3]}' was given."
                            )
                            return None, self.assertions
                        ret = room.world.set_ambient_value("weather", value)
                    else:
                        if len(command_split) == 4:
                            try:
                                assert value.isnumeric()
                                value = float(value)
                            except AssertionError:
                                logging.warning(
                                    f"The value should be a number, but '{value}' was given."
                                )
                                return None, self.assertions
                            ambient = (
                                command_split[1] + "_" + command_split[3]
                            )  # we add '_in' or '_out'
                            ret = room.world.set_ambient_value(ambient, value)
                        else:
                            logging.warning(
                                f"No specification of indoor/outdoor ambient to set, the third argument of 'set' command should be 'in' or 'out' with temperature, humidity and co2."
                            )
                            return None, self.assertions
                    return ret, self.assertions  # ret is None or 1
                else:
                    # Sensors humiditysoil and presence or ON/OFF a functional module -> user command parser
                    if len(command_split) >= 3:
                        # set sensor value
                        if (
                            "humiditysoil" in command_split[1]
                            or "presencesensor" in command_split[1]
                        ):
                            if "humiditysoil" in command_split[1]:
                                try:
                                    assert command_split[2].isnumeric()
                                except AssertionError:
                                    logging.warning(
                                        f"The value {command_split[2]} given to set {command_split[1]} is not a number."
                                    )
                                    return None, self.assertions
                                value = float(command_split[2])
                            elif "presencesensor" in command_split[1]:
                                try:
                                    assert command_split[2].lower() in (
                                        "true",
                                        "on",
                                        "false",
                                        "off",
                                    )
                                except AssertionError:
                                    logging.warning(
                                        f"The value {command_split[2]} given to set {command_split[1]} is not a boolean."
                                    )
                                    return None, self.assertions
                                value = (
                                    True
                                    if command_split[2].lower() in ("true", "on")
                                    else False
                                )
                            for ir_device in room.devices:
                                if command_split[1] == ir_device.name:
                                    ret = ir_device.device.set_value(value)
                                    return ret, self.assertions  # ret is None or 1
                            # If device not found
                            logging.warning(
                                f"The device {command_split[1]} is not found in room's devices list."
                            )
                            return None, self.assertions

                        # set functional module on or off, with possible value for state_ratio
                        elif (
                            "button" in command_split[1] or "dimmer" in command_split[1]
                        ):
                            if not user_command_parser(command, room):  # return 0
                                return None, self.assertions
                            else:  # return 1
                                return 1, self.assertions
                        else:
                            logging.warning(
                                f"Device {command_split[1]} cannot be set with 'set' API command, or does not exist."
                            )
                            return None, self.assertions
            else:
                logging.error(
                    f"'set' command requires 2 or 3 arguments, but {len(command_split)-1} was provided."
                )
                return None, self.assertions
        # 'show' command
        elif command.startswith("show"):
            if len(command_split) == 1 or command_split[1].lower() == "all":
                pp.pprint(self.stored_values)
            elif len(command_split) == 2:
                if command_split[1] in self.stored_values:
                    print(
                        f"{command_split[1]} = {self.stored_values[command_split[1]]}"
                    )
            else:
                logging.warning(f"'show' command requires 0 or 1 argument.")
                return None, self.assertions
            return 1, self.assertions
        # 'end' command
        elif command.startswith("end"):
            print("End of script")
            return 0, self.assertions
