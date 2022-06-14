"""
Module that gather usefull functions and definitions for physical world states modeling and updates.
"""

import math
from datetime import datetime, timezone
from typing import Tuple

from astral import LocationInfo
from astral.sun import sun


SOIL_MOISTURE_MIN = 10
# Influence of outdoor temp
INSULATION_TO_TEMPERATURE_FACTOR = {
    "perfect": 0,
    "good": 10 / 100,
    "average": 20 / 100,
    "bad": 40 / 100,
}
# Influence of outdoor humidity
INSULATION_TO_HUMIDITY_FACTOR = {
    "perfect": 0,
    "good": 20 / 100,
    "average": 45 / 100,
    "bad": 75 / 100,
}
# Influence of outdoor co2
INSULATION_TO_CO2_FACTOR = {
    "perfect": 0,
    "good": 10 / 100,
    "average": 25 / 100,
    "bad": 50 / 100,
}

DATE_WEATHER_TO_LUX = {
    "clear_day": 10752,
    "overcast_day": 1075,
    "dark_day": 107,
    "clear_sunrise_sunset": 300,
    "overcast_sunrise_sunset": 100,
    "dark_sunrise_sunset": 10,
    "clear_twilight": 10.8,
    "overcast_twilight": 1,
    "clear_night": 0.108,
    "overcast_night": 0.0001,
    "dark_night": 0,
}


def outdoor_light(date_time: datetime, weather: str) -> Tuple[float, datetime]:
    """Return outdoor lux value from weather conditions and time of day in a certain location (e.g. Lausanne)"""
    city = LocationInfo("Lausanne", "Switzerland", "Europe", 46.516, 6.63282)
    date = date_time.date()
    date_time = date_time.replace(tzinfo=timezone.utc)
    sun_time = sun(city.observer, date=date)
    dawn_datetime, sunrise_datetime, noon_datetime, sunset_datetime, dusk_datetime = (
        sun_time["dawn"],
        sun_time["sunrise"],
        sun_time["noon"],
        sun_time["sunset"],
        sun_time["dusk"],
    )
    # Night
    if date_time < dawn_datetime or dusk_datetime < date_time:
        time_of_day = "moon"  # for gui time of day symbol
        if weather == "clear":
            lux_out = DATE_WEATHER_TO_LUX["clear_night"]
        elif weather == "overcast":
            lux_out = DATE_WEATHER_TO_LUX["overcast_night"]
        elif weather == "dark":
            lux_out = DATE_WEATHER_TO_LUX["dark_night"]
    # Day
    elif sunrise_datetime < date_time and date_time < sunset_datetime:
        time_of_day = "sun"  # for gui time of day symbol
        if (
            date_time < noon_datetime
        ):  # ratio of how close we are to ;id_morning/mid_afternoon, 1 if mid_morning < date_time < mid_afternoon
            mid_morning_offset = (noon_datetime - sunrise_datetime) / 2
            mid_morning_datetime = sunrise_datetime + mid_morning_offset
            ratio = min(
                (date_time - sunrise_datetime)
                / (mid_morning_datetime - sunrise_datetime),
                1,
            )
        elif noon_datetime < date_time:
            mid_afternoon_offset = (sunset_datetime - noon_datetime) / 2
            mid_afternoon_datetime = sunset_datetime - mid_afternoon_offset
            ratio = min(
                (sunset_datetime - date_time)
                / (sunset_datetime - mid_afternoon_datetime),
                1,
            )
        if weather == "clear":
            lux_out = max(
                ratio * DATE_WEATHER_TO_LUX["clear_day"],
                DATE_WEATHER_TO_LUX["clear_sunrise_sunset"],
            )
        elif weather == "overcast":
            lux_out = max(
                ratio * DATE_WEATHER_TO_LUX["overcast_day"],
                DATE_WEATHER_TO_LUX["overcast_sunrise_sunset"],
            )
        elif weather == "dark":
            lux_out = max(
                ratio * DATE_WEATHER_TO_LUX["dark_day"],
                DATE_WEATHER_TO_LUX["dark_sunrise_sunset"],
            )
    # Twilight
    else:  # ratio of how close we are to sunrise/sunset with regards to twilight
        if dawn_datetime < date_time and date_time < sunrise_datetime:
            time_of_day = "sunrise"  # for gui time of day symbol
            ratio = (date_time - dawn_datetime) / (sunrise_datetime - dawn_datetime)
        elif sunset_datetime < date_time and date_time < dusk_datetime:
            time_of_day = "sunset"  # for gui time of day symbol
            ratio = (dusk_datetime - date_time) / (dusk_datetime - sunset_datetime)

        if weather == "clear":
            lux_out = ratio * (
                DATE_WEATHER_TO_LUX["clear_sunrise_sunset"]
                - DATE_WEATHER_TO_LUX["clear_twilight"]
            )
        elif weather == "overcast":
            lux_out = ratio * (
                DATE_WEATHER_TO_LUX["overcast_sunrise_sunset"]
                - DATE_WEATHER_TO_LUX["overcast_twilight"]
            )
        elif weather == "dark":
            lux_out = ratio * (
                DATE_WEATHER_TO_LUX["dark_sunrise_sunset"]
                - DATE_WEATHER_TO_LUX["overcast_twilight"]
            )
    return lux_out, time_of_day


def compute_distance(source, sensor) -> float:
    """
    Computes euclidian distance between a sensor and a source (or simply two room devices).

    source : InRoomDevice
    sensor : InRoomDevice
    """
    delta_x = abs(source.location.x - sensor.location.x)
    delta_y = abs(source.location.y - sensor.location.y)
    delta_z = abs(source.location.z - sensor.location.z)
    dist = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
    return dist


def compute_distance_from_window(window, sensor) -> float:
    """
    Compute closest distace between window and brightness sensor (projection on window plane).

    window : Window
    sensor : InRoomDevice
    """
    from system.room import InRoomDevice
    from system.system_tools import Window

    window_copy = Window(
        "window_nearest",
        window.room,
        window.device.wall,
        window.device.location_offset,
        window.device.size,
    )
    window_nearest_point = InRoomDevice(
        window_copy,
        window.room,
        window_copy.window_loc[0],
        window_copy.window_loc[1],
        window_copy.window_loc[2],
    )
    if window.device.wall in ["north", "south"]:
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
    elif window.device.wall in ["west", "east"]:
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
