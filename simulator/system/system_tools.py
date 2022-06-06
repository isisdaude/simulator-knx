
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import math
from datetime import datetime, timezone, timedelta
from astral import LocationInfo
from astral.sun import sun

import system
import devices as dev


# Influence of outdoor temp
INSULATION_TO_TEMPERATURE_FACTOR = {"perfect": 0, "good": 10/100, "average": 20/100, "bad":40/100}
# Influence of outdoor humidity
INSULATION_TO_HUMIDITY_FACTOR = {"perfect": 0, "good": 20/100, "average": 45/100, "bad":75/100}
# Influence of outdoor co2
INSULATION_TO_CO2_FACTOR = {"perfect": 0, "good": 10/100, "average": 25/100, "bad":50/100}

class Location:
    """Class to represent location"""
    def __init__(self, room, x, y, z):
        from tools import check_location
        self.room = room
        self.min_x, self.max_x = 0, self.room.width
        self.min_y, self.max_y = 0, self.room.length
        self.min_z, self.max_z = 0, self.room.height
        self.bounds = [[ self.min_x, self.max_x], [self.min_y, self.max_y], [self.min_z, self.max_z]]
        # Check that location is correct, replace in the room if out of bounds
        self.x, self.y, self.z = check_location(self.bounds, x, y, z)
        self.pos = (self.x, self.y, self.z)

    # def update_location(self, new_x=None, new_y=None, new_z=None):
    #     from .check_tools import check_location
    #     x = (new_x or self.x)
    #     y = (new_y or self.y)
    #     z = (new_z or self.z)
    #     self.x, self.y, self.z = check_location(self.bounds, x, y, z)
    #     self.pos = (self.x, self.y, self.z)

    def __str__(self):
        str_repr =  f"Location: {self.room.name}: {self.pos}\n"
        return str_repr

    def __repr__(self):
        return f"Location in {self.room.name} is {self.pos}\n"


class IndividualAddress:
    """Class to represent individual addresses (virtual location on the KNX Bus)"""
    ## Magic Number
    def __init__(self, area, line, main): # area[4bits],  device[8bits], line[4bits]
        from tools import check_individual_address
        self.area, self.line, self.device = check_individual_address(area, line, main)
        self.ia_str = '.'.join([str(self.area), str(self.line), str(self.device)])

    def __eq__(self, other):
        return (self.area == other.area and
                self.line == other.line and
                self.device == self.device)

    def __str__(self): 
        return self.ia_str

    def __repr__(self):
        return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"

    def __repr__(self) -> str:
        '''Following XKNX handling of individual addresses'''
        return f"{self.area}.{self.line}.{self.device}"


class GroupAddress:
    """Class to represent group addresses (devices gathered by functionality)"""
    ## Magic Number

    def __init__(self, encoding_style, main, middle=0, sub=0):
        self.encoding_style = encoding_style
        if self.encoding_style == '3-levels': # main[5bits], middle[3bits], sub[8bits]
            
            self.main = main
            self.middle = middle
            self.sub = sub
            self.name = "/".join((str(main), str(middle), str(sub)))
        elif self.encoding_style == '2-levels': # main[5bits], sub[11bits]
            
            self.main = main
            self.sub = sub
            self.name = "/".join((str(main), str(sub)))
        elif self.encoding_style == 'free': # main[16bits]
            
            self.main = main
            self.name = str(main)

    def __str__(self): 
        return self.name
        

    def __repr__(self): 
        return self.name
        

# __eq__() or __lt__(), "is" operator to check if an instances are of the same type
    def __lt__(self, ga_to_compare): # self is the group addr ref, we want to check if self is smaller than the other ga
        if self.encoding_style == '3-levels':
            ga_ref = self.sub + self.middle<<8 + self.main<<11
            ga_test = ga_to_compare.sub + ga_to_compare.middle<<8 + ga_to_compare.main<<11
            return (ga_ref < ga_test)
        if self.encoding_style == '2-levels':
            ga_ref = self.sub + self.main<<11
            ga_test = ga_to_compare.sub + ga_to_compare.main<<11
            return (ga_ref < ga_test)
        if self.encoding_style == 'free':
            return (self.main < ga_to_compare.main)

    def __eq__(self, ga_to_compare):
        if self.main == ga_to_compare.main:
            if self.encoding_style == 'free':
                return True
            else: # if encoding style is 2 or 3-levels
                if self.sub == ga_to_compare.sub:
                    if self.encoding_style == '2-levels':
                        return True
                    else: # if encoding style is 3-levels
                        if self.middle == ga_to_compare.middle:
                            return True
                        else:
                            return False




class Window:
    """Class to represent windows"""
    def __init__(self, window_name, room, wall, location_offset, size):
        from tools import check_window
        ## window img size is 300p wide, for a room of 12.5m=1000p, it corresponds to 3.75m
        ## must scale the window if different size, e.g. if window size = 1m, scale factor x(horizontal) ou y(vertical) = 1/3.75``
        self.WINDOW_PIXEL_SIZE = 300
        ROOM_PIXEL_WIDTH = 1000 ## TODO: take this constant from a config file
        # to copy window instance in compute_distance_from_window()
        self.location_offset = location_offset

        self.initial_size = room.width * self.WINDOW_PIXEL_SIZE / ROOM_PIXEL_WIDTH # 3.75m if room width=12.5 for 1000 pixels
        self.name = window_name
        self.class_name = 'Window'
        self.wall, self.window_loc, self.size  = check_window(wall, location_offset, size, room)   # size[width, height] in meters
        if self.wall is None: # failed check
            raise ValueError("Window object cannot be created, check the error logs")

        self.beam_angle = 180 # arbitrary  but realistic
        self.state = True # state to be compliant with LighActuator's attributes
        self.state_ratio = 100 # change if blinds implemented

        # for the GUI display
        if self.wall in ['north', 'south']:
            self.scale_x = self.size[0] / self.initial_size
        if self.wall in ['east', 'west']:
            self.scale_y = self.size[0] / self.initial_size
        # self.location_out_offset =  # offset for location to consider light source point outside of room, so that with a certain beamangle, all light is considered

    def max_lumen_from_out_lux(self, out_lux):
        self.max_lumen = out_lux * math.prod(self.size) # out_lux*window_area
    
    def effective_lumen(self):
        # Lumen quantity rationized with the state ratio (% of source's max lumens)
        return 0.2*self.max_lumen + 0.8*self.max_lumen*(self.state_ratio/100) # 20% of outdoor light will pass even with blinds closed


"""Tools for physical world updates"""
def compute_distance(source, sensor) -> float: # in_room_devices
    """ Computes euclidian distance between a sensor and a actuator"""
    delta_x = abs(source.location.x - sensor.location.x)
    delta_y = abs(source.location.y - sensor.location.y)
    delta_z = abs(source.location.z - sensor.location.z)
    dist = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2) # distance between light sources and brightness sensor
    return dist

def compute_distance_from_window(window, sensor) -> float:   # wndow and sensor is in room device
    """Compute closest distace between window and brightness sensor"""
    # window_nearest_point = copy.deepcopy(window)
    window_copy = Window("window_nearest", window.room, window.device.wall,window.device.location_offset, window.device.size)
    window_nearest_point = system.InRoomDevice(window_copy, window.room, window_copy.window_loc[0], window_copy.window_loc[1], window_copy.window_loc[2])
    if window.device.wall in ['north', 'south']:
        win_left_x = window.location.x
        win_right_x = win_left_x + window.device.size[0]
        # Test if sensor if in the same axe than window, on left or on right
        if sensor.location.x < win_left_x: 
            window_nearest_point.location.x = win_left_x
            return compute_distance(window_nearest_point, sensor)
        elif win_right_x < sensor.location.x:
            window_nearest_point.location.x = win_right_x
            return compute_distance(window_nearest_point, sensor)
        else: 
            window_nearest_point.location.x = sensor.location.x
            return compute_distance(window_nearest_point, sensor)
    elif window.device.wall in ['west', 'east']:
        win_bottom_y = window.location.y
        win_top_y = win_bottom_y + window.device.size[0]
        # Test if sensor if in the same axe than window, on bottom or on top
        if sensor.location.y < win_bottom_y:
            window_nearest_point.location.y = win_bottom_y
            return compute_distance(window_nearest_point, sensor)
        elif win_top_y < sensor.location.y:
            window_nearest_point.location.y = win_top_y
            return compute_distance(window_nearest_point, sensor)
        else:
            window_nearest_point.location.y = sensor.location.y
            return compute_distance(window_nearest_point, sensor)
    

DATE_WEATHER_TO_LUX = {"clear_day":10752, "overcast_day":1075, "dark_day":107, "clear_sunrise_sunset":300, "overcast_sunrise_sunset":100, "dark_sunrise_sunset":10,  "clear_twilight":10.8, "overcast_twilight":1, "clear_night":0.108, "overcast_night":0.0001, "dark_night":0}
def outdoor_light(date_time:datetime, weather:str):
    city = LocationInfo("Lausanne", "Switzerland", "Europe", 46.516, 6.63282)
    date = date_time.date()
    date_time = date_time.replace(tzinfo=timezone.utc)
    sun_time = sun(city.observer, date=date)
    dawn_datetime, sunrise_datetime, noon_datetime, sunset_datetime, dusk_datetime = sun_time["dawn"], sun_time["sunrise"], sun_time["noon"], sun_time["sunset"], sun_time["dusk"]
    # Night
    if date_time < dawn_datetime or dusk_datetime < date_time:
        time_of_day = 'moon' # for gui time of day symbol
        if weather == "clear":
            lux_out = DATE_WEATHER_TO_LUX["clear_night"]
        elif weather == "overcast":
            lux_out = DATE_WEATHER_TO_LUX["overcast_night"]
        elif weather == "dark":
            lux_out = DATE_WEATHER_TO_LUX["dark_night"]
    # Day
    elif sunrise_datetime < date_time and date_time < sunset_datetime:
        time_of_day = 'sun' # for gui time of day symbol
        if date_time < noon_datetime: # ratio of how close we are to ;id_morning/mid_afternoon, 1 if mid_morning < date_time < mid_afternoon
            mid_morning_offset = (noon_datetime - sunrise_datetime) / 2
            mid_morning_datetime = sunrise_datetime + mid_morning_offset
            ratio = min((date_time - sunrise_datetime) / (mid_morning_datetime - sunrise_datetime), 1)
        elif noon_datetime < date_time:
            mid_afternoon_offset = (sunset_datetime - noon_datetime) / 2
            mid_afternoon_datetime = sunset_datetime - mid_afternoon_offset
            ratio = min((sunset_datetime - date_time ) / (sunset_datetime - mid_afternoon_datetime), 1)
        if weather == "clear":
            lux_out = max(ratio * DATE_WEATHER_TO_LUX["clear_day"], DATE_WEATHER_TO_LUX["clear_sunrise_sunset"])
        elif weather == "overcast":
            lux_out = max(ratio * DATE_WEATHER_TO_LUX["overcast_day"], DATE_WEATHER_TO_LUX["overcast_sunrise_sunset"])
        elif weather == "dark":
            lux_out = max(ratio * DATE_WEATHER_TO_LUX["dark_day"], DATE_WEATHER_TO_LUX["dark_sunrise_sunset"])
    # Twilight
    else: # ratio of how close we are to sunrise/sunset with regards to twilight
        if dawn_datetime < date_time and date_time < sunrise_datetime:
            time_of_day = 'sunrise' # for gui time of day symbol
            ratio = (date_time - dawn_datetime) / (sunrise_datetime - dawn_datetime) 
        elif sunset_datetime < date_time and date_time < dusk_datetime:
            time_of_day = 'sunset' # for gui time of day symbol
            ratio = (dusk_datetime - date_time) / (dusk_datetime - sunset_datetime)
            
        if weather == "clear":
            lux_out = ratio * (DATE_WEATHER_TO_LUX["clear_sunrise_sunset"] - DATE_WEATHER_TO_LUX["clear_twilight"])
        elif weather == "overcast":
            lux_out = ratio * (DATE_WEATHER_TO_LUX["overcast_sunrise_sunset"] - DATE_WEATHER_TO_LUX["overcast_twilight"])
        elif weather == "dark":
            lux_out = ratio * (DATE_WEATHER_TO_LUX["dark_sunrise_sunset"] - DATE_WEATHER_TO_LUX["overcast_twilight"])
    # print(f"-- lux_out : {lux_out}")
    # print(f" ------ {date_time}")
    # print(f"{dawn_datetime}:dawn_datetime, \n{sunrise_datetime}:sunrise_datetime, \n{noon_datetime}:noon_datetime, \n{sunset_datetime}:sunset_datetime, \n{dusk_datetime}:dusk_datetime")
    return lux_out, time_of_day







# """Tools used by the devices to perform update calculations"""
# # def required_power(desired_temperature=20, volume=1, insulation_state="good"):
# #     def temp_to_watts(temp):  # Useful watts required to heat 1m3 to temp
# #         dist = 18 - temp
# #         return 70 - (dist * 7)/2
# #     desired_wattage = volume*temp_to_watts(desired_temperature)
# #     desired_wattage += desired_wattage * \
# #         INSULATION_TO_CORRECTION_FACTOR[insulation_state]
# #     return desired_wattage


# # def max_temperature_in_room(power, volume=1.0, insulation_state="good"):
# #     """Maximum reachable temperature for this heater in the specified room"""

# #     def watts_to_temp(watts):
# #         return ((watts - 70)*2)/7 + 18

# #     watts = power / ((1+INSULATION_TO_CORRECTION_FACTOR[insulation_state])*volume)
# #     return watts_to_temp(watts)