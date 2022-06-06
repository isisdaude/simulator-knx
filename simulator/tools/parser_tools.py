#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import asyncio
import logging, sys
import argparse
import pprint
pp=pprint.PrettyPrinter(compact=True)

import devices as dev
from .config_tools import * # GUI_MODE, CLI_INT_MODE, ...


COMMAND_HELP = "Command Syntax: \n"\
                "- switch state: 'set [device_name] [ON/OFF] [value]'\n"\
                "- read state: 'getvalue [device_name]'\n"\
                "- system info: 'getinfo [device_name]' or 'getinfo world [ambient]'\n"\
                "- exit: 'q' to quit the program\n"\
                "- help: 'h' for help"



def arguments_parser(argv):
    """FUcntion to parse CLI arguments given by the user when launching the program"""
    parser = argparse.ArgumentParser(description='Process Interface, Command, Config and Logging modes.')

    # Logging argument definition
    parser.add_argument("-l", "--log",  
                        action='store', 
                        default="WARNING",
                        type=str.upper,
                        choices=logging._nameToLevel.keys(), 
                        help=("Provide logging level. Example -l debug or --log=DEBUG', default='WARNING'."))
    # Interface argument definition
    parser.add_argument("-i", "--interface",
                        action='store',
                        default="gui",
                        type=str.lower,
                        choices=["gui", "cli"],
                        help=("Provide user interface mode. Example -i cli or --interface=cli, default='gui'."))
    # Command argument definition
    parser.add_argument("-c", "--command-mode",
                        action='store',
                        default="cli",
                        type=str.lower,
                        choices=["script", "cli"],
                        help=("Provide command mode. Example -c script or --command-mode=script, default='cli'"))
    # Config File Name argument definition 
    parser.add_argument("-f", "--filescript-name",
                        action='store',
                        default="full_script",
                        type=str.lower,
                        help=("Provide script file name (without .txt extension). Example -F full_script or --file-name=full_script, default='full_script'"))
    # Config argument definition
    parser.add_argument("-C", "--config-mode",
                        action='store',
                        default="file",
                        type=str.lower,
                        choices=["file", "default", "empty", "dev"],
                        help=("Provide configuration mode. Example -C file or --command-mode=empty, default='file'"))
    # Config File Name argument definition 
    parser.add_argument("-F", "--fileconfig-name",
                        action='store',
                        default="sim_config_bedroom",
                        type=str.lower,
                        help=("Provide configuration file name (without .json extension). Example -F sim_config_bedroom or --file-name=sim_config_bedroom, default='sim_config_bedroom'"))
    # SVSHI mode argument definition
    parser.add_argument("-s", "--svshi-mode",
                        action='store_true', # svshi_mode=True if option, False if no -s option
                        help=("Specifies that SVSHI will be used (-s option) or not (no option)."))
    # System dt argument definition
    parser.add_argument("-d", "--system-dt",
                        action='store',
                        default=1,
                        type=int,
                        help=("Provide the system dt, interval in seconds between two consecutive system updates. Example -d 2 or --system-dt=3, default=1"))

    # Get the arguments from command line
    options = parser.parse_args()
    config = vars(options)
    # logging.info(f"CLI arguments config: {config}")
    print(f"CLI arguments config: {config}")

    # Logging level argument parser
    logging.basicConfig(level=options.log.upper(), format='%(asctime)s | [%(levelname)s] -- %(message)s') #%(name)s : username (e.g. root)
    # Interface mode argument parser
    INTERFACE_MODE = options.interface.lower()
    # Command mode argument parser
    COMMAND_MODE = options.command_mode.lower()
    # Script File Name argument parser
    FILESCRIPT_NAME = options.filescript_name
    SCRIPT_PATH = "./docs/scripts/" + FILESCRIPT_NAME + ".txt"
    # Config mode argument parser
    CONFIG_MODE = options.config_mode.lower()
    # Config File Name argument parser
    FILECONFIG_NAME = options.fileconfig_name
    CONFIG_PATH = "./docs/config/" + FILECONFIG_NAME + ".json"
    # SVSHI mode argument parser
    SVSHI_MODE = options.svshi_mode
    # System dt argument parser
    SYSTEM_DT = options.system_dt

    return INTERFACE_MODE, COMMAND_MODE, SCRIPT_PATH, CONFIG_MODE, CONFIG_PATH, SVSHI_MODE, SYSTEM_DT



def user_command_parser(command, room):
    """ Parser function for CLI communication with the user through the terminal or GUI command box"""
    command = command.strip() # remove start and end spaces
    command_split = command.split(' ')
    if len(command):
        print(f"\nCommand >>>'{command}'<<<", flush=True)
    # User action on Functional Module
    if command_split[0] == 'set': 
        print(f"\set:> {command[4:]}")
        name = command_split[1]
        # If no ON/OFF state or value specified, we simply switch the state of the device
        if len(command_split) == 2: 
            for in_room_device in room.devices:
                if in_room_device.name in name:
                    if not isinstance(in_room_device.device, dev.FunctionalModule):
                        logging.warning("Users can only interact with a Functional Module")
                        return 1
                    in_room_device.device.user_input()
                    return 1
        # If user gives ON/OFF state and/or value
        elif len(command_split) >= 3: 
            if command_split[2] not in ['ON', 'OFF']:
                logging.warning(f"Unrecognised/incomplete command")
                return 0
            state = True if command_split[2]=='ON' else False
            for in_room_device in room.devices:
                    if in_room_device.name in name:
                        if not isinstance(in_room_device.device, dev.FunctionalModule):
                            logging.warning("Users can only interact with a Functional Module")
                            return 0
                        # User gives ON/OFF state and value (e.g. for dimmer)
                        if len(command_split) == 4: 
                            state_ratio = int(command_split[3])
                            if state_ratio < 0 or 100 < state_ratio:
                                logging.warning(f"The value '{state_ratio}' given should be a ratio (0-100), the command is incorrect")
                                return 0
                            in_room_device.device.user_input(state=state, state_ratio=state_ratio)
                        # User gives only ON/OFF state
                        else:
                            in_room_device.device.user_input(state=state)
                        return 1
    # System information asked by the user
    elif command_split[0] == 'getinfo' or command.strip() == 'getinfo':
        # Global info info asked by user
        if command.strip() == 'getinfo': # only 'getinfo' keyword -> we give all info to user (exceot device specific info)
            world_dict = room.get_world_info('all')
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
        if 'world' in command_split[1]: 
            if len(command_split) > 2:
                ambient = command_split[2] # can be 'time', 'temperature', 'humidity', 'co2level', 'co2', 'brightness', 'all'
                if len(ambient) >= len('all'): # smallest str acceptable after 'getinfo world' command
                    if 'time' in ambient:
                        world_dict = room.get_world_info('time')
                    if 'temperature' in ambient:
                        world_dict = room.get_world_info('temperature')
                    if 'humidity' in ambient:
                        world_dict = room.get_world_info('humidity')
                    if 'co2' in ambient:
                        world_dict = room.get_world_info('co2level')
                    if 'brightness' in ambient: # brightness is a global brightness from room's ground perspective
                        world_dict = room.get_world_info('brightness')
                    if 'out' in ambient:
                        world_dict = room.get_world_info('out')
                    if 'all' in ambient:
                        world_dict = room.get_world_info('all')
            else: # if nothing specified, just get all world info
                world_dict = room.get_world_info('all')
            pp.pprint(world_dict)
            return world_dict
        # Room info asked by user
        elif 'room' in command_split[1]:
            room_dict = room.get_room_info()
            pp.pprint(room_dict)
            return room_dict
        # Bus info asked by user
        elif 'bus' in command_split[1]:
            bus_dict = room.get_bus_info()
            pp.pprint(bus_dict)
            return bus_dict
        # Device specific info asked by user
        elif len(command_split) > 1:  # at least one keyword after 'getinfo' but None of the above
            if 'dev' in command_split[1]: # user ask for info on a device
                if len(command_split) > 2:
                    name = command_split[2]
                else:
                    logging.warning("The command is not recognized by the parser: either wrong or incomplete")
                    return 0
            else:
                name = command_split[1] # user ask for info on a device without using the dev keyword
            device_dict = room.get_device_info(name)
            ## TODO check some stuff with info, write some kind of API
            pp.pprint(device_dict)
            return device_dict
        else:
            logging.warning("The command is not recognized by the parser: either wrong or incomplete")

    elif command_split[0] == 'getvalue': #Sensor
        print(f"\getvalue:> {command[9:]}")
        name = command_split[1]
        for in_room_device in room.devices:
            if in_room_device.name in name:
                if not isinstance(in_room_device.device, dev.Sensor):
                    logging.warning("Users can only get the value read by a Sensor with 'getvalue' command")
                    return 0
                pp.pprint(in_room_device.device.get_dev_info(value=True))
                # print("=> The brightness received on sensor %s located at (%d,%d) is %.2f\n" % (name, in_room_device.get_x(), in_room_device.get_y(), room.world.ambient_light.read_brightness(in_room_device)))
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
        command = command.strip().lower() # remove new line symbol and put in lower case
        print(f"Command >>> '{command}' <<<")
        command_split = command.split(' ')
        # wait command
        if command.startswith('wait'):
            if len(command_split) > 2 and 'h' in command_split[2]: # time to wait in simulated hours, not computer seconds
                speed_factor = room.world.time.speed_factor
                sleep_time = int(int(command_split[1])*3600/speed_factor) # time to wait in computer system seconds
            elif len(command_split) == 2: # if only 2 keywords
                sleep_time = int(command_split[1])
            else:
                logging.warning(f"The last command cannot be parsed, it is skipped.")
            logging.info(f"[SCRIPT] Wait for {sleep_time} sec")
            await asyncio.sleep(sleep_time)
            return 1
        # store command to keep one current system value
        elif command.startswith('store'):
            if len(command_split) < 4:
                logging.error(f"The 'store' command requires 3 argument, but only {len(command_split)-1} were given")
                sys.exit(1) ### TODO check for correct implementation
            if command_split[1] == 'world':
                if len(command_split) > 3: # ambient and var name should be given
                    var_name = command_split[3]
                    ambient = command_split[2]
                    self.stored_values[var_name] = room.get_world_info(ambient, str_mode=False)[ambient+'_in']
                    logging.info(f"[SCRIPT] The world {ambient} (indoor) is stored in variable {var_name}")
                    return 1
                # else: # No ambient precised, we store all
                #     for ambient in ['simtime', 'brightness', 'temperature', 'humidity', 'co2']:
                #         self.stored_values[ambient] = room.get_world_info(ambient, str_mode=False)[ambient+'_in']
                #         logging.info(f"[VERIF] The world {ambient} is stored.")
                #         return 1
            elif command_split[1] == 'device':
                if len(command_split) > 3: # attribute of device and var name should be given
                    var_name = command_split[3]
                    attribute = command_split[2]
                    # self.stored_values[var_name] = room.get_dev_info() 
                    ## TODO get correct dev info/attribute
                    logging.info(f"[SCRIPT] The device {attribute} is stored in variable {var_name}")
                    return 1

        elif command.startswith('assert'):
            if len(command_split) >= 4: # var name, math operation and value needed
                var_name = command_split[1]
                if command_split[3] in self.stored_values: # if we compare to a stored variable
                    value = self.stored_values[command_split[3]]
                else:
                    value = command_split[3]
                try:
                    if command_split[2] == '==':
                        assert self.stored_values[var_name] == value
                    elif command_split[2] == '!=':
                        assert self.stored_values[var_name] != value
                    elif command_split[2] == '<=':
                        assert self.stored_values[var_name] <= value
                    elif command_split[2] == '>=':
                        assert self.stored_values[var_name] >= value
                    logging.info(f"[SCRIPT] The comparison is correct")
                    print(f"Assertion True")
                except AssertionError:
                    logging.info(f"[SCRIPT] The comparison is not correct")
                    ## TODO: exception handling, terminate test
            else:
                ## TODO logging failure
                return 0

            # if command_split[1] == 'world':
            #     if len(command_split) >= 4: # assert, world, ambient, up/down/=
            #         ambient = command_split[2]
            #         if ambient in self.stored_values:
            #             old_ambient = self.stored_values[ambient]
            #             new_ambient = room.get_world_info(ambient, str_mode=False)[ambient+'_in']
            #             if command_split[3] == 'up':
            #                 assert new_ambient > old_ambient
            #                 logging.info(f"[VERIF] The {ambient} has increased.")
            #                 print(f"Assertion True")
            #                 return 1
            #             elif command_split[3] == 'down':
            #                 assert new_ambient < old_ambient
            #                 logging.info(f"[VERIF] The {ambient} has decreased.")
            #                 print(f"Assertion True")
            #                 return 1
            #             elif command_split[3] == '=':
            #                 assert new_ambient == old_ambient
            #                 logging.info(f"[VERIF] The {ambient} didn't change.")
            #                 print(f"Assertion True")
            #                 return 1
        elif command.startswith('end'):
            print("End of verification")
            # print(COMMAND_HELP)
            ## TODO, print recap of script test
            return None

        elif command.startswith('set') and len(command_split) >= 2 and command_split[1] in ['ON', 'OFF']: # turn on/off device through classcial knx bus way
            return user_command_parser(command, room)
        
        elif command.startswith('set') and len(command_split) >= 3 and command_split[1] in ['Temperature', 'Humidity', 'CO2', 'Brightness', 'Weather']:
            ## TODO set ambient in world directly
            pass
            # print(f"command parser with '{command}'")
            # set device