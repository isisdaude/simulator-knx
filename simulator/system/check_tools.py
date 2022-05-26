#pylint: disable=[W0223, C0301, C0114, C0115, C0116]

import logging, sys
import datetime as dt
import numbers


def check_simulation_speed_factor(simulation_speed_factor:str):
    try:
        speed_factor = float(simulation_speed_factor)
    except ValueError:
        logging.error(f"The simulation speed should be a decimal number, but '{simulation_speed_factor}' was given")
        return None
    except SyntaxError as msg:
        logging.error(f"Wrong Syntax: {msg}")
        return None
    try:
        assert speed_factor >= 1
    except AssertionError:
        logging.error(f"The simulation speed should be a positive number >=1, but '{simulation_speed_factor}' was given")
        return None
    return speed_factor

def check_individual_address(area, line, device):
    ia_assert_msg = ""
    try:
        assert isinstance(area, numbers.Number), f"area='{area}' is not a number, "
    except AssertionError as assert_msg:
        ia_assert_msg += str(assert_msg)
    else:
        try:
            assert isinstance(area, int), f"'area={area}' is not an int, "
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
    try:
        assert isinstance(line, numbers.Number), f"line='{line}' is not a number, "
    except AssertionError as assert_msg:
        ia_assert_msg += str(assert_msg)
    else:
        try:
            assert isinstance(line, int), f"'line={line}' is not an int, "
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
    try:
        assert isinstance(device, numbers.Number), f"device number='{device}' is not a number, "
    except AssertionError as assert_msg:
        ia_assert_msg += str(assert_msg)
    else:
        try:
            assert isinstance(device, int), f"'device number={device}' is not an int, "
        except AssertionError as assert_msg:
            ia_assert_msg += str(assert_msg)
    if len(ia_assert_msg) > 0:
        ia_assert_msg = ia_assert_msg[:-2]+'.'
        logging.error("Individual address should be numbers in 0.0.0 - 15.15.255, here : "+ia_assert_msg)
        return None, None, None
    try: # test if the indiv address has correct values
        assert (area >= 0 and area <= 15 and line >= 0 and line <= 15 and device >= 0 and device <= 255)
    except AssertionError:
        logging.error(f"Individual address is out of bounds, should be in 0.0.0 - 15.15.255, but '{area}.{line}.{device}' given")
        return None, None, None
    else:
        return area, line, device



def check_group_address(group_address_style, text='', style_check=False): ## TODO: verify if the group address entered in text box is correct
        from .tools import GroupAddress
        ''' Verify that the group address entered by the user is correct (2, 3-levels or free) '''
        if not style_check:
            text_split = text.split('/')
            for split in text_split:
                if not split.lstrip('-').isdecimal():
                    logging.warning(f"Group address '{group_address_style}':'{text}' has wrong value type, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255) with positive int characters only")
                    return None
                if int(split) == 0: # special case for -0
                    if not split.isdecimal():
                        logging.warning(f"Group address '{group_address_style}':'{text}' has wrong value type, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255) with positive int characters only")
                        return None
        if group_address_style == '3-levels':
            if style_check: # We just want to check if style exists
                return group_address_style
            if len(text_split) == 3:
                try:
                    main, middle, sub = int(text_split[0]), int(text_split[1]), int(text_split[2])
                except ValueError:
                    logging.warning(f"'3-levels' group address {text} has wrong value type, should be int: 0/0/0 -> 31/7/255")
                    return None
                try: # test if the group address has the correct format
                    assert (main >= 0 and main <= 31 and middle >= 0 and middle <= 7 and sub >= 0 and sub <= 255)
                    return GroupAddress('3-levels', main = main, middle = middle, sub = sub)
                except AssertionError:
                    logging.warning(f"'3-levels' group address {text} is out of bounds, should be in 0/0/0 -> 31/7/255")
                    return None
            else:
                logging.warning("'3-levels' style is not respected, possible addresses: 0/0/0 -> 31/7/255")
                return None
        elif group_address_style == '2-levels':
            if style_check: # We just want to check if style exists
                return group_address_style
            if len(text_split) == 2:
                try:
                    main, sub = int(text_split[0]), int(text_split[1])
                except ValueError:
                    logging.warning(f"'2-levels' group address {text} has wrong value type, should be int: 0/0 -> 31/2047")
                    return None
                try: # test if the group address has the correct format
                    assert (main >= 0 and main <= 31 and sub >= 0 and sub <= 2047)
                    return GroupAddress('2-levels', main = main, sub = sub)
                except AssertionError:
                    logging.warning(f"'2-levels' group address {text} is out of bounds, should be in 0/0 -> 31/2047")
                    return None
            else:
                logging.warning("'2-levels' style is not respected, possible addresses: 0/0 -> 31/2047")
                return None
        elif group_address_style == 'free':
            if style_check: # We just want to check if style exists
                return group_address_style
            if len(text_split) == 1:
                try:
                    main = int(text_split[0])
                except ValueError:
                    logging.warning(f"'free' group address {text} has wrong value type, should be int: 0 -> 65535")
                    return None
                try: # test if the group address has the correct format
                    assert (main >= 0 and main <= 65535)
                    return GroupAddress('free', main = main)
                except AssertionError:
                    logging.warning(f"'free' group address {text} is out of bounds, should be in 0 -> 65535")
                    return None
            else:
                logging.warning("'free' style is not respected, possible addresses: 0 -> 65535")
                return None
        else: # not a correct group address style
            logging.error(f"Group address style '{group_address_style}' unknown, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255)")
            return None

def check_room_config(name, width, length, height, speed_factor, ga_style, insulation):
    # Room name check
    try:
        assert isinstance(name, str)
    except AssertionError:
        logging.error(f"A non-empty alphanumeric string name is required to create the room, but '{name}' was given -> program terminated.")
        sys.exit(1)
    try:
        assert len(name) > 0
        assert name.isalnum() # check alphanumericness
    except AssertionError:
        logging.error(f"A non-empty alphanumeric string name is required to create the room, but '{name}' was given -> program terminated.")
        sys.exit(1)
    # Room dimensions check
    dim_assert_msgs = ""
    try:
        assert isinstance(width, numbers.Number), f"width='{width}' is not a number" # check not a string
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg)+', '
    try:
        assert isinstance(length, numbers.Number), f"length='{length}' is not a number" 
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg)+', '
    try:
        assert isinstance(height, numbers.Number), f"height='{height}' is not a number" 
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg)+', '
    if len(dim_assert_msgs) > 0:
        dim_assert_msgs = dim_assert_msgs[:-2]
        logging.error("Room's dimensions are expected to be stricly positive numbers, here : "+dim_assert_msgs+' -> program terminated.')
        sys.exit(1)
    try:
        assert width > 0, f"width={width} is not positive" # check positiveness
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg)+', '
    try:
        assert length > 0, f"length={length} is not positive" # check positiveness
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg)+', '
    try:
        assert height > 0, f"height={height} is not positive" # check positiveness
    except AssertionError as assert_msg:
        dim_assert_msgs += str(assert_msg)+', '
    if len(dim_assert_msgs) > 0:
        dim_assert_msgs = dim_assert_msgs[:-2] # Replace last coma by a dot
        logging.error("Room's dimensions are expected to be stricly positive numbers, here : "+dim_assert_msgs+' -> program terminated.')
        sys.exit(1)
    # Room simulation speed factor check 
    try:
        assert speed_factor == check_simulation_speed_factor(speed_factor)
    except AssertionError:
        logging.error(f"The simulation speed factor {speed_factor} is incorrect -> program terminated.")
        sys.exit(1)
    # Room group address style check
    try:
        assert ga_style == check_group_address(ga_style, style_check=True)
    except AssertionError:
        logging.error(f"The room's group address encoding style '{ga_style}' is not recognized -> program terminated.")
        sys.exit(1)
    # Room insulation type check
    try:
        assert insulation in ['perfect', 'good', 'average', 'bad']
    except AssertionError:
        logging.error(f"The insulation type {insulation} is not recognised, should be 'perfect', 'average', 'good' or 'bad'. 'average' is considered by default.")
        insulation = 'average'
    
    return name, width, length, height, speed_factor, ga_style, insulation


def check_device_config(class_name, name, refid, individual_addr, status):
    # Device name check
    try:
        assert isinstance(name, str)
    except AssertionError:
        logging.error(f"A non-empty alphanumeric string name is required to create the device, but '{name}' was given -> program terminated.")
        sys.exit(1)
    try:
        assert len(name) > 0
        assert name.isalnum() # check alphanumericness
        assert name.islower() # check lower case name
    except AssertionError:
        logging.error(f"A non-empty alphanumeric string name is required to create the device, but '{name}' was given -> program terminated.")
        sys.exit(1)
    try:
        assert class_name.lower() in name
    except AssertionError:
        logging.error(f"The lower-case class name '{class_name.lower()}' should be in name, but '{name}' was given -> program terminated.")
        sys.exit(1)
    # Device refid check
    try:
        assert isinstance(refid, str)
    except AssertionError:
        logging.error(f"A non-empty ascii string reference ID is required to create the device, but '{refid}' was given -> program terminated.")
        sys.exit(1)
    try:
        assert len(refid) > 5 # arbitrary 5, refid should be longer
        assert refid.isascii() # check alphanumericness
    except AssertionError:
        logging.error(f"A non-empty ascii string reference ID is required to create the device, but '{refid}' was given -> program terminated.")
        sys.exit(1)
    # Device Individual address check
    try:
        assert individual_addr.area is not None and individual_addr.line is not None and individual_addr.device is not None
    except AssertionError:
        logging.error(f"Wrong individual address for device {name} -> program terminated.")
        sys.exit(1)
    # Device status check
    try:
        assert status in ["enabled", "disabled"]
    except AssertionError:
        logging.error(f"Status of device {name} should be 'enabled' or 'disabled', but '{status}' was given -> program terminated.")
        sys.exit(1)

    return class_name, name, refid, individual_addr, status


def check_location(bounds, x, y, z):
    loc_assert_msg = ''
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
        loc_assert_msg = loc_assert_msg[:-2]+' -> program terminated.'
        logging.error(f"The given coordinates are not correct: "+loc_assert_msg)
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
        logging.warning(f"The location is out of room's bounds: '({x},{y},{z})' given while room's dimensions are '({max_x},{max_y},{max_z})'")
        new_x = (min_x if x<min_x else x)
        new_x = (max_x if max_x<new_x else new_x)
        new_y = (min_y if y<min_y else y)
        new_y = (max_y if max_y<new_y else new_y)
        new_z = (min_z if z<min_z else z)
        new_z = (max_z if max_z<new_z else new_z)
        logging.info(f"The device's location is replaced in the rooms's bounds: '({x},{y},{z})' -> '({new_x},{new_y},{new_z})'")
        return new_x, new_y, new_z
    else:
        return x, y, z

def check_wheater_date(date_time, weather):
    TIME_OF_DAY = ["today", "yesterday", "one_week_ago", "one_month_ago", "YYYY/MM/DD/HH/MM"]
    WEATHER = ["clear", "overcast", "dark"]
    # datetime
    date_time = date_time.lower()
    try:
        assert date_time in TIME_OF_DAY # today or yesterday
        if date_time == 'today':
            sim_datetime = dt.datetime.today()
        if date_time == 'yesterday':
            sim_datetime = dt.datetime.today() - dt.timedelta(days=1)
        if  date_time == 'one_week_ago':
            sim_datetime = dt.datetime.today() - dt.timedelta(days=7)
        if date_time == 'one_month_ago': # 4 weeks ago in reality
            sim_datetime = dt.datetime.today() - dt.timedelta(weeks=4)
    except AssertionError:
        try:
            dt_split = date_time.split('/')
            if len(dt_split) > 3:
                assert len(dt_split) == 5 # hour and minute
                try:
                    sim_datetime = dt.datetime(year=dt_split[0],month=dt_split[1],day=dt_split[2], hour=dt_split[3], minute=dt_split[4])
                except ValueError as msg:
                    logging.error(f" The time_of_day '{date_time}' given is incorrect: '{msg}'")
            else:
                assert len(dt_split) == 3 # only date
                try:
                    sim_datetime = dt.datetime(year=dt_split[0],month=dt_split[1],day=dt_split[2])
                except ValueError as msg:
                    logging.error(f" The time_of_day '{date_time}' given is incorrect: '{msg}'")
        except AssertionError:
            logging.error(f"'date_time format should be 'YYYY/MM/DD/HH/MM' or 'YYYY/MM/DD', but '{date_time}' was given, today is considered as datetime simulation")
            sim_datetime = dt.datetime.today()
    # weather
    try:
        weather = weather.lower()
        assert weather in WEATHER
        sim_weather = weather
    except AssertionError:
        logging.error(f"'weather should be 'clear', 'overcast' or 'dark', but '{weather}' was given, 'sunny' is considered as simulation outside weather ")
        sim_weather = 'clear'
    return sim_datetime, sim_weather


    
