"""
Module that implement verification function to check correctness of variables, attributes or classes.
"""

import logging
import numbers
import sys
import traceback
from datetime import datetime, timedelta
from typing import Union, Tuple

from system.system_tools import IndividualAddress, GroupAddress


def check_simulation_speed_factor(simulation_speed_factor: str) -> Union[None, float]:
    """Check that the simulation factor has a suitable value."""
    try:
        speed_factor = float(simulation_speed_factor)
    except ValueError:
        logging.error(
            f"The simulation speed should be a decimal number, but '{simulation_speed_factor}' was given."
        )
        return None
    except SyntaxError as msg:
        logging.error(f"Wrong Syntax: {msg}")
        return None
    try:
        assert speed_factor >= 1
    except AssertionError:
        logging.error(
            f"The simulation speed should be a positive number >=1, but '{simulation_speed_factor}' was given."
        )
        return None
    return speed_factor


def check_individual_address(
    area: Union[str, int], line: Union[str, int], device: Union[str, int]
) -> Union[Tuple[None, None, None], Tuple[float, float, float]]:
    """Check that the individual address has the correct format and values."""
    ia_assert_msg = ""
    if type(area) == str:
        try:
            assert area.isnumeric(), f"area='{area}' is not a number, "
            area_check = int(area)
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
    else:
        try:
            assert isinstance(area, numbers.Number), f"area='{area}' is not a number, "
            area_check = int(area)
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
        else:  # if no exceptions
            try:
                assert isinstance(area, int), f"'area={area}' is not an int, "
            except AssertionError as assert_msg:
                ia_assert_msg += str(assert_msg)

    if type(line) == str:
        try:
            assert line.isnumeric(), f"line='{line}' is not a number, "
            area_check = int(line)
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
    else:
        try:
            assert isinstance(line, numbers.Number), f"line='{line}' is not a number, "
            line_check = int(line)
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
        else:
            try:
                assert isinstance(line, int), f"'line={line}' is not an int, "
            except AssertionError as assert_msg:
                ia_assert_msg += str(assert_msg)

    if type(device) == str:
        try:
            assert device.isnumeric(), f"device number='{device}' is not a number, "
            area_check = int(device)
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
    else:
        try:
            assert isinstance(
                device, numbers.Number
            ), f"device number='{device}' is not a number, "
            device_check = int(device)
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
        else:
            try:
                assert isinstance(
                    device, int
                ), f"'device number={device}' is not an int, "
            except AssertionError as assert_msg:
                ia_assert_msg += str(assert_msg)
    if len(ia_assert_msg) > 0:
        ia_assert_msg = ia_assert_msg[:-2] + "."
        logging.error(
            f"Individual address should be numbers in 0.0.0 - 15.15.255, here : {ia_assert_msg}."
        )
        return None, None, None
    try:  # test if the indiv address has correct values
        assert (
            area_check >= 0
            and area_check <= 15
            and line_check >= 0
            and line_check <= 15
            and device_check >= 0
            and device_check <= 255
        )
    except AssertionError:
        logging.error(
            f"Individual address is out of bounds, should be in 0.0.0 - 15.15.255, but  given."
        )
        return None, None, None
    except:
        exc = sys.exc_info()[0]
        trace = traceback.format_exc()
        logging.warning(
            f"Individual address creation with '{area_check}.{line_check}.{device_check}' failed: {exc} with trace \n{trace}."
        )
        return None, None, None
    else:
        return area_check, line_check, device_check


# Constants for Group Addresses check
MAX_MAIN = 31
MAX_MIDDLE = 7
MAX_SUB_LONG = 255
MAX_SUB_SHORT = 2047
MAX_FREE = 65535


def check_group_address(
    group_address_style: str, text: str = "", style_check: bool = False
) -> Union[None, GroupAddress]:
    """
    Check that the group address entered by the user is correct.

    style_check : indicate that only the endocing style and format should be checked,
    group_address_style : should be 2-levels, 3-levels or free.
    """
    if not style_check:
        text_split = text.split("/")
        for split in text_split:
            if not split.lstrip("-").isdecimal():
                logging.warning(
                    f"Group address '{group_address_style}':'{text}' has wrong value type, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255) with positive int characters only."
                )
                return None
            if int(split) == 0:
                if not split.isdecimal():
                    logging.warning(
                        f"Group address '{group_address_style}':'{text}' has wrong value type, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255) with positive int characters only."
                    )
                    return None
    if group_address_style == "3-levels":
        if style_check:
            return group_address_style
        if len(text_split) == 3:
            try:
                main, middle, sub = (
                    int(text_split[0]),
                    int(text_split[1]),
                    int(text_split[2]),
                )
            except ValueError:
                logging.warning(
                    f"'3-levels' group address {text} has wrong value type, should be int: 0/0/0 -> 31/7/255."
                )
                return None
            try:  # test if the group address has the correct format
                assert (
                    main >= 0
                    and main <= MAX_MAIN
                    and middle >= 0
                    and middle <= MAX_MIDDLE
                    and sub >= 0
                    and sub <= MAX_SUB_LONG
                )
                return GroupAddress("3-levels", main=main, middle=middle, sub=sub)
            except AssertionError:
                logging.warning(
                    f"'3-levels' group address {text} is out of bounds, should be in 0/0/0 -> 31/7/255."
                )
                return None
        else:
            logging.warning(
                "'3-levels' style is not respected, possible addresses: 0/0/0 -> 31/7/255."
            )
            return None
    elif group_address_style == "2-levels":
        if style_check:
            return group_address_style
        if len(text_split) == 2:
            try:
                main, sub = int(text_split[0]), int(text_split[1])
            except ValueError:
                logging.warning(
                    f"'2-levels' group address {text} has wrong value type, should be int: 0/0 -> 31/2047."
                )
                return None
            try:  # test if the group address has the correct format
                assert (
                    main >= 0 and main <= MAX_MAIN and sub >= 0 and sub <= MAX_SUB_SHORT
                )
                return GroupAddress("2-levels", main=main, sub=sub)
            except AssertionError:
                logging.warning(
                    f"'2-levels' group address {text} is out of bounds, should be in 0/0 -> 31/2047."
                )
                return None
        else:
            logging.warning(
                "'2-levels' style is not respected, possible addresses: 0/0 -> 31/2047."
            )
            return None
    elif group_address_style == "free":
        if style_check:
            return group_address_style
        if len(text_split) == 1:
            try:
                main = int(text_split[0])
            except ValueError:
                logging.warning(
                    f"'free' group address {text} has wrong value type, should be int: 0 -> 65535."
                )
                return None
            try:
                assert main >= 0 and main <= MAX_FREE
                return GroupAddress("free", main=main)
            except AssertionError:
                logging.warning(
                    f"'free' group address {text} is out of bounds, should be in 0 -> 65535."
                )
                return None
        else:
            logging.warning(
                "'free' style is not respected, possible addresses: 0 -> 65535."
            )
            return None
    else:  # not a correct group address style
        logging.error(
            f"Group address style '{group_address_style}' unknown, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255)."
        )
        return None


def check_room_config(
    name: str,
    width: float,
    length: float,
    height: float,
    speed_factor: float,
    ga_style: str,
    insulation: str,
) -> Tuple[str, float, float, float, float, str, str]:
    """Check Room configuration attributes."""
    try:
        assert isinstance(name, str)
    except AssertionError:
        logging.error(
            f"A non-empty alphanumeric string name is required to create the room, but '{name}' was given -> program terminated."
        )
        sys.exit(1)
    try:
        assert len(name) > 0
        assert name.isalnum()  # alphanumeric check
    except AssertionError:
        logging.error(
            f"A non-empty alphanumeric string name is required to create the room, but '{name}' was given -> program terminated."
        )
        sys.exit(1)
    # Room dimensions check
    dim_assert_msgs = ""
    try:
        assert isinstance(width, numbers.Number), f"width='{width}' is not a number"
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg) + ", "
    try:
        assert isinstance(length, numbers.Number), f"length='{length}' is not a number"
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg) + ", "
    try:
        assert isinstance(height, numbers.Number), f"height='{height}' is not a number"
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg) + ", "
    if len(dim_assert_msgs) > 0:
        dim_assert_msgs = dim_assert_msgs[:-2]
        logging.error(
            "Room's dimensions are expected to be stricly positive numbers, here : "
            + dim_assert_msgs
            + " -> program terminated."
        )
        sys.exit(1)
    try:
        assert width > 0, f"width={width} is not positive"
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg) + ", "
    try:
        assert length > 0, f"length={length} is not positive"
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg) + ", "
    try:
        assert height > 0, f"height={height} is not positive"
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg) + ", "
    if len(dim_assert_msgs) > 0:
        dim_assert_msgs = dim_assert_msgs[:-2]  # Replace last coma by a dot
        logging.error(
            "Room's dimensions are expected to be stricly positive numbers, here : "
            + dim_assert_msgs
            + " -> program terminated."
        )
        sys.exit(1)
    # Room simulation speed factor check
    try:
        assert speed_factor == check_simulation_speed_factor(speed_factor)
    except AssertionError:
        logging.error(
            f"The simulation speed factor {speed_factor} is incorrect -> program terminated."
        )
        sys.exit(1)
    # Room group address style check
    try:
        assert ga_style == check_group_address(ga_style, style_check=True)
    except AssertionError:
        logging.error(
            f"The room's group address encoding style '{ga_style}' is not recognized -> program terminated."
        )
        sys.exit(1)
    # Room insulation type check
    try:
        assert insulation in ["perfect", "good", "average", "bad"]
    except AssertionError:
        logging.error(
            f"The insulation type {insulation} is not recognised, should be 'perfect', 'average', 'good' or 'bad'. 'average' is considered by default."
        )
        insulation = "average"

    return name, width, length, height, speed_factor, ga_style, insulation


def check_device_config(
    class_name: str, name: str, individual_addr: IndividualAddress
) -> Tuple[str, IndividualAddress]:
    """Check device config attributes."""
    try:
        assert isinstance(name, str)
    except AssertionError:
        logging.error(
            f"A non-empty alphanumeric string name is required to create the device, but '{name}' was given -> program terminated."
        )
        sys.exit(1)
    try:
        assert len(name) > 0
        assert name.isalnum()  # alphanumeric
        assert name.islower()
    except AssertionError:
        logging.error(
            f"A non-empty alphanumeric string name is required to create the device, but '{name}' was given -> program terminated."
        )
        sys.exit(1)
    try:
        assert class_name.lower() in name
    except AssertionError:
        logging.error(
            f"The lower-case class name '{class_name.lower()}' should be in name, but '{name}' was given -> program terminated."
        )
        sys.exit(1)
    # Device Individual address check
    try:
        assert (
            individual_addr.area is not None
            and individual_addr.line is not None
            and individual_addr.device is not None
        )
    except AssertionError:
        logging.error(
            f"Wrong individual address for device {name} -> program terminated."
        )
        sys.exit(1)

    return name, individual_addr


def check_location(
    bounds: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
    x: float,
    y: float,
    z: float,
) -> Tuple[float, float, float]:
    """Check that Location coordinates are within bounds, sys.exit if wrong coordinates."""
    loc_assert_msg = ""
    try:
        assert isinstance(x, numbers.Number), f"x='{x}' is not a number, "
    except AssertionError as assert_msg:
        loc_assert_msg += str(assert_msg)
    try:
        assert isinstance(y, numbers.Number), f"y='{y}' is not a number, "
    except AssertionError as assert_msg:
        loc_assert_msg += str(assert_msg)
    try:
        assert isinstance(z, numbers.Number), f"z='{z}' is not a number, "
    except AssertionError as assert_msg:
        loc_assert_msg += str(assert_msg)
    if len(loc_assert_msg) > 0:
        loc_assert_msg = loc_assert_msg[:-2] + " -> program terminated."
        logging.error(f"The given coordinates are not correct: {loc_assert_msg}.")
        sys.exit(1)

    # Replace location in Room if out-of-bounds
    min_x, max_x = bounds[0]
    min_y, max_y = bounds[1]
    min_z, max_z = bounds[2]
    try:
        assert min_x <= x and x <= max_x
        assert min_y <= y and y <= max_y
        assert min_z <= z and z <= max_z
    except AssertionError:
        logging.warning(
            f"The location is out of room's bounds: '({x},{y},{z})' given while room's dimensions are '({max_x},{max_y},{max_z})'."
        )
        new_x = min_x if x < min_x else x
        new_x = max_x if max_x < new_x else new_x
        new_y = min_y if y < min_y else y
        new_y = max_y if max_y < new_y else new_y
        new_z = min_z if z < min_z else z
        new_z = max_z if max_z < new_z else new_z
        logging.info(
            f"The device's location is replaced in the 's bounds: '({x},{y},{z})' -> '({new_x},{new_y},{new_z})'."
        )
        return new_x, new_y, new_z
    else:
        return x, y, z


def check_weather_date(date_time: str, weather: str) -> Tuple[datetime, str]:
    """Check weather and time of day string from config file."""
    TIME_OF_DAY = ["today", "yesterday", "one_week_ago", "one_month_ago"]
    WEATHER = ["clear", "overcast", "dark"]
    # datetime
    date_time = date_time.lower()
    if date_time in TIME_OF_DAY:  # today, yesterday,...
        if date_time == "today":
            sim_datetime = datetime.today()
        elif date_time == "yesterday":
            sim_datetime = datetime.today() - timedelta(days=1)
        elif date_time == "one_week_ago":
            sim_datetime = datetime.today() - timedelta(days=7)
        elif date_time == "one_month_ago":  # 4 weeks ago in reality
            sim_datetime = datetime.today() - timedelta(weeks=4)
    else:
        try:
            dt_split = date_time.split("/")
            for d in dt_split:
                assert d.isnumeric()
            if len(dt_split) > 3:
                assert len(dt_split) == 5  # hour and minute
                try:
                    sim_datetime = datetime(
                        year=int(dt_split[0]),
                        month=int(dt_split[1]),
                        day=int(dt_split[2]),
                        hour=int(dt_split[3]),
                        minute=int(dt_split[4]),
                    )
                except ValueError as msg:
                    logging.error(
                        f" The time_of_day '{date_time}' given is incorrect: '{msg}'."
                    )
            else:
                assert len(dt_split) == 3  # only date
                try:
                    sim_datetime = datetime(
                        year=int(dt_split[0]),
                        month=int(dt_split[1]),
                        day=int(dt_split[2]),
                    )
                except ValueError as msg:
                    logging.error(
                        f" The time_of_day '{date_time}' given is incorrect: '{msg}'."
                    )
        except AssertionError:
            logging.error(
                f"'date_time format should be 'YYYY/MM/DD/HH/MM' or 'YYYY/MM/DD', but '{date_time}' was given, today is considered as datetime simulation."
            )
            sim_datetime = datetime.today()
    # weather
    try:
        weather = weather.lower()
        assert weather in WEATHER
        sim_weather = weather
    except AssertionError:
        logging.error(
            f"'weather should be 'clear', 'overcast' or 'dark', but '{weather}' was given, 'clear' is considered as simulation outside weather."
        )
        sim_weather = "clear"
    return sim_datetime, sim_weather


def check_window(
    wall: str, location_offset: float, size: Tuple[float, float], room
) -> Union[Tuple[None, None, None], Tuple[str, float, Tuple[float, float]]]:
    """
    Check window object creation.

    room : Room
    location offset is location in meters from strat of wall (left side of north/south walls, bottom side of east/west walls
    """
    # wall str check
    try:
        assert wall in ["north", "south", "east", "west"]
    except AssertionError:
        logging.error(
            f"The window's wall '{wall}' is incorrect, should be in 'north', 'south', 'east', 'west'] -> we do not consider this window in the simulation."
        )
        return None, None, None
    # size (width/length, height) in m
    size_height = size[1]
    size_width = size[0]  # width or length depending on orientation
    try:
        assert size_width > 0 and size_height > 0
    except AssertionError:
        logging.error(
            f"The window's size '{size}' is incorrect, should be > 0 -> we do not consider this window in the simulation."
        )
        return None, None, None
    # window height
    try:
        assert size_height <= room.height
    except AssertionError:
        logging.error(
            f"The window's height '{size_height}' is too large, should be lower than room's height = '{room.height} -> we do not consider this window in the simulation.'"
        )
        return None, None, None
    # window width/length, window loc
    if wall in ["north", "south"]:  # Horizontal window
        try:
            log_bounds = ("width", room.width)
            assert size_width <= room.width
        except AssertionError:
            logging.error(
                f"The window's size '{size_width}' is incorrect, should be lower than room's {log_bounds[0]} = '{log_bounds[1]}' -> we do not consider this window in the simulation."
            )
            return None, None, None
        window_loc = location_offset  # concret location of window center
        try:  # check if left side in the room's bounds
            assert (window_loc - size_width / 2) > 0
        except AssertionError:
            logging.error(
                f"The window is too large for its location, its left side is out of room's bounds ({(window_loc-size/2)} < 0) -> we do not consider this window in the simulation."
            )
            return None, None, None
        try:  # check if right side in the room's bounds
            assert (window_loc + size_width / 2) < room.width
        except AssertionError:
            logging.error(
                f"The window is too large for its location, its right side is out of room's bounds ({(window_loc+size/2)} > {room.width}) -> we do not consider this window in the simulation."
            )
            return None, None, None
        # definition of window location to create Location instance
        if wall == "north":
            loc_y = room.length
        elif wall == "south":
            loc_y = 0
        window_location = (window_loc, loc_y, room.height / 2)
    if wall in ["east", "west"]:  # Vertical Window
        try:
            log_bounds = ("length", room.length)
            assert size_width <= room.length
        except AssertionError:
            logging.error(
                f"The window's size '{size_width}' is incorrect, should be lower than room's {log_bounds[0]} = '{log_bounds[1]}' -> we do not consider this window in the simulation."
            )
            return None, None, None
        window_loc = location_offset  # concrete location of window center
        try:  # check if bottom side in the room's bounds
            assert (window_loc - size_width / 2) > 0
        except AssertionError:
            logging.error(
                f"The window is too large for its location, its bottom side is out of room's bounds ({(window_loc-size/2)} < 0) -> we do not consider this window in the simulation."
            )
            return None, None, None
        try:  # check if top side in the room's bounds
            assert (window_loc + size_width / 2) < room.length
        except AssertionError:
            logging.error(
                f"The window is too large for its location, its top side is out of room's bounds ({(window_loc+size/2)} > {room.length}) -> we do not consider this window in the simulation."
            )
            return None, None, None
        # definition of window location to create Location instance
        if wall == "east":
            loc_x = room.width
        elif wall == "west":
            loc_x = 0
        window_location = (loc_x, window_loc, room.height / 2)
    return wall, window_location, size
