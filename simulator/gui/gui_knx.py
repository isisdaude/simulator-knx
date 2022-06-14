""" 
Module managing the pyglet GUI Window class and reacting to user's events (key press, mouse click,...)
"""

# Standard libraries
import sys
import json
import logging
import pyglet

# Thrid-party libraries
from time import time, sleep
from typing import List, Tuple
import numpy as np

# Application libraries
import gui.gui_tools as gt
import gui.gui_config as gc


class GUIWindow(pyglet.window.Window):
    """
    Class to define the GUI window, the widgets and text displayed in it 
    and the functions reacting to the user actions (mouse click, input text,...)
    """

    from system.room import Room

    def __init__(
        self,
        config_path: str,
        default_config_path: str,
        empty_config_path: str,
        saved_config_path: str,
        room: Room = None,
        svshi_mode: bool = False,
        telegram_logging: bool = False,
    ) -> None:
        """
        Initialization of pyglet GUI Window object.
        """
        super(GUIWindow, self).__init__(
            gc.WIN_WIDTH, gc.WIN_LENGTH, caption="KNX Simulator", resizable=False
        )
        from tools import configure_system_from_file

        # Configure batch of modules to draw on events (mouse click, moving,...)
        self.__batch = pyglet.graphics.Batch()
        # Create multiple layers to superpose the graphical elements
        self.__background = pyglet.graphics.OrderedGroup(0)
        self.__middlebackground = pyglet.graphics.OrderedGroup(1)
        self.__middleground = pyglet.graphics.OrderedGroup(2)
        self.__foreground = pyglet.graphics.OrderedGroup(3)
        # Store the initial configuration file path if the user wants to reload the simulation
        self.__CONFIG_PATH = config_path
        self.__DEFAULT_CONFIG_PATH = default_config_path
        self.__EMPTY_CONFIG_PATH = empty_config_path
        self.SAVED_CONFIG_PATH = (
            saved_config_path + "saved_config_"
        )  # used by Save Button
        # Flags for svshi mode
        self.__svshi_mode = svshi_mode
        self.__telegram_logging = telegram_logging
        # Room object to represent the KNX System
        try:
            self.room = room
        except TypeError:
            logging.info(
                "No room is defined, the room's default characteristics are applied."
            )
            self.room = configure_system_from_file(
                self.__DEFAULT_CONFIG_PATH,
                svshi_mode=self.__svshi_mode,
                telegram_logging=self.__telegram_logging,
            )

        # Array to store the devices added to the room (e.g., by dragging them in)
        self.__room_devices: List[gt.DeviceWidget] = []
        self.__gui_windows: List[gt.WindowWidget] = []
        self.__devices_scroll = 0  # Keep state of the scroll position of devices list
        # Default individual addresses when adding devices during simulation
        self.__individual_address_default = [
            0,
            0,
            100,
        ]  # we suppose no more than 99 devices on area0/line0, and no more than 155 new manually added devices
        # Initialize the room widget to draw in the window
        self.__room_widget = gt.RoomWidget(
            gc.ROOM_WIDTH,
            gc.ROOM_LENGTH,
            self.__batch,
            group_bg=self.__background,
            group_mg=self.__middlebackground,
            label=self.room.name,
            label_group=self.__middleground,
        )
        # Array to store labels to display in room devices list
        self.__room_devices_labels: List[pyglet.text.Label] = []
        # Array to store brightnesses & temperature in the room
        self.__room_brightness_labels: List[pyglet.text.Label] = []
        self.__room_brightness_levels: List[pyglet.text.Label] = []
        self.__room_temperature_labels: List[pyglet.text.Label] = []
        self.__room_temperature_levels: List[pyglet.text.Label] = []
        self.__room_airquality_labels: List[pyglet.text.Label] = []
        self.__room_airsensor_levels: List[pyglet.text.Label] = []

        # Initialize the Available devices widgets to draw them on the left side, that a user can drag them in the room
        self.__available_devices = gt.AvailableDevices(
            self.__batch, group_dev=self.__foreground, group_box=self.__background
        )

        # Create the text labels and the textbox to display to the user
        self.__command_label = pyglet.text.Label(
            "Enter your command",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=20,
            bold=True,
            x=gc.COMMANDLABEL_POS[0],
            y=gc.COMMANDLABEL_POS[1],
            anchor_x="right",
            anchor_y="bottom",
            batch=self.__batch,
            group=self.__foreground,
        )
        self.__text_box = pyglet.shapes.Rectangle(
            gc.TEXTBOX_POS[0],
            gc.TEXTBOX_POS[1],
            gc.WIN_WIDTH - gc.TEXTBOX_POS[0] - gc.WIN_BORDER,
            40,
            color=(255, 255, 255),
            batch=self.__batch,
            group=self.__background,
        )
        # Initialize the text box label to display the user input in the textbox
        self.__input_label = pyglet.text.Label(
            "",
            font_name=gc.FONT_USER_INPUT,
            font_size=15,
            color=(10, 10, 10, 255),
            x=(self.__text_box.x + 10),
            y=(self.__text_box.y + 20),
            anchor_x="left",
            anchor_y="center",
            batch=self.__batch,
            group=self.__foreground,
        )
        self.simtime_widget = gt.SimTimeWidget(
            gc.SIMTIME_POS[0],
            gc.SIMTIME_POS[1],
            self.__batch,
            group_box=self.__background,
            group_label=self.__foreground,
        )
        self.daytimeweather_widget = gt.DayTimeWeatherWidget(
            gc.TIMEWEATHER_POS[0],
            gc.TIMEWEATHER_POS[1],
            self.__batch,
            group_box=self.__background,
            group_daytime=self.__middleground,
            group_weather=self.__foreground,
            temp_out=self.room.world.ambient_temperature.temperature_out,
            hum_out=self.room.world.ambient_humidity.humidity_out,
            co2_out=self.room.world.ambient_co2.co2_out,
        )
        # Initialize the list of devices in the room
        self.__devicelist_widget = gt.DeviceListWidget(
            gc.DEVICELIST_POS[0],
            gc.DEVICELIST_POS[1],
            self.__batch,
            group_label=self.__foreground,
            group_box=self.__background,
        )
        self.__sensors_box_shape = pyglet.shapes.BorderedRectangle(
            gc.WIN_BORDER / 2,
            gc.OFFSET_SENSOR_LEVELS_BOX_Y_BOTTOM,
            gc.SENSOR_LEVELS_BOX_WIDTH,
            gc.SENSOR_LEVELS_BOX_LENGTH,
            border=gc.BOX_BORDER,
            color=gc.COLOR_BOX_SENSORS,
            border_color=gc.COLOR_BOX_SENSORS_BORDER,
            batch=self.__batch,
            group=self.__background,
        )
        self.__brightness_label = pyglet.text.Label(
            "Brightness (lux):",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=15,
            bold=True,
            color=gc.COLOR_FONT_SENSORS_TITLE,
            x=gc.BRIGHTNESS_LABEL_POS[0],
            y=gc.BRIGHTNESS_LABEL_POS[1],
            anchor_x="left",
            anchor_y="bottom",
            batch=self.__batch,
            group=self.__foreground,
        )
        self.__temperature_label = pyglet.text.Label(
            "Temperature (°C):",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=15,
            bold=True,
            color=gc.COLOR_FONT_SENSORS_TITLE,
            x=gc.TEMPERATURE_LABEL_POS[0],
            y=gc.TEMPERATURE_LABEL_POS[1],
            anchor_x="left",
            anchor_y="bottom",
            batch=self.__batch,
            group=self.__foreground,
        )
        self.__airquality_label = pyglet.text.Label(
            "Air quality - T(°C) / CO2(ppm) / RH(%):",  # 350-1,000 ppm,
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=15,
            bold=True,
            color=gc.COLOR_FONT_SENSORS_TITLE,
            x=gc.AIRSENSOR_LABEL_POS[0],
            y=gc.AIRSENSOR_LABEL_POS[1],
            anchor_x="left",
            anchor_y="bottom",
            batch=self.__batch,
            group=self.__foreground,
        )
        # GUI buttons
        self.__buttons = (
            []
        )  # List of Button instances (PAUSE, STOP, RELOAD, SAVE, DEFAULT)
        # Reload Button to re-initialize the simulation
        self.__button_pause = gt.ButtonPause(
            gc.BUTTON_PAUSE_POS[0],
            gc.BUTTON_PAUSE_POS[1],
            self.__batch,
            gc.BUTTON_PAUSE_PATH,
            gc.BUTTON_PLAY_PATH,
            group=self.__foreground,
        )
        self.__buttons.append(self.__button_pause)
        self.__button_stop = gt.ButtonStop(
            gc.BUTTON_STOP_POS[0],
            gc.BUTTON_STOP_POS[1],
            self.__batch,
            gc.BUTTON_STOP_PATH,
            group=self.__foreground,
        )
        self.__buttons.append(self.__button_stop)
        self.__button_reload = gt.ButtonReload(
            gc.BUTTON_RELOAD_POS[0],
            gc.BUTTON_RELOAD_POS[1],
            self.__batch,
            gc.BUTTON_RELOAD_PATH,
            group=self.__foreground,
        )
        self.__buttons.append(self.__button_reload)
        self.__button_save = gt.ButtonSave(
            gc.BUTTON_SAVE_POS[0],
            gc.BUTTON_SAVE_POS[1],
            self.__batch,
            gc.BUTTON_SAVE_PATH,
            group=self.__foreground,
        )
        self.__buttons.append(self.__button_save)
        self.__button_default = gt.ButtonDefault(
            gc.BUTTON_DEFAULT_POS[0],
            gc.BUTTON_DEFAULT_POS[1],
            self.__batch,
            gc.BUTTON_DEFAULT_PATH,
            group=self.__foreground,
        )
        self.__buttons.append(self.__button_default)

    ## Private methods ##
    ### Display methods ###
    def __display_devices_list(self, scroll: int = 0) -> None:
        """Display (or re-initialize) the room devices' list, potentially after a mouse scroll on the list"""
        for room_device_label in self.__room_devices_labels:
            room_device_label.delete()
        self.__room_devices_labels: List[pyglet.text.Label] = []
        room_devices_counter = 0
        list_x = self.__devicelist_widget.deviceslist_title.x
        list_y = (
            self.__devicelist_widget.deviceslist_title.y - gc.OFFSET_DEVICESLIST_TITLE
        )
        # To scroll in devices list
        self.__devices_scroll = max(0, self.__devices_scroll + scroll)
        # max scroll to limit how far a user can go down in the list, we keep MAX_SIZE_DEVICES_LIST devices visible at least
        max_scroll = (
            len(self.__room_devices) - self.__devicelist_widget.MAX_SIZE_DEVICES_LIST
        )
        if max_scroll > 0:
            self.__devices_scroll = int(min(self.__devices_scroll, max_scroll))
        # Display the current room devices name in list
        for room_device in self.__room_devices[self.__devices_scroll :]:
            room_dev_x = list_x
            room_dev_y = list_y - room_devices_counter * gc.OFFSET_LIST_DEVICE
            room_dev_ia_y = room_dev_y - gc.OFFSET_INDIVIDUAL_ADDR_LABEL
            ia_label = room_device.in_room_device.device.individual_addr.ia_str
            room_dev_gas = room_device.in_room_device.device.group_addresses
            ga_text = " -- (" + ", ".join([str(ga) for ga in room_dev_gas]) + ")"
            label_text = room_device.label.text + ga_text
            room_device_label = pyglet.text.Label(
                label_text,
                font_name=gc.FONT_SYSTEM_INFO,
                font_size=gc.FONT_SIZE_DEVICESLIST,
                color=gc.COLOR_FONT_DEVICESLIST_DEVICE,
                x=room_dev_x,
                y=room_dev_y,
                anchor_x="left",
                anchor_y="bottom",
                batch=self.__batch,
                group=self.__foreground,
            )
            room_device_ia_label = pyglet.text.Label(
                ia_label,
                font_name=gc.FONT_SYSTEM_INFO,
                font_size=gc.FONT_SIZE_INDIVIDUAL_ADDR,
                color=gc.COLOR_FONT_DEVICESLIST_DEVICE_IA,
                x=room_dev_x,
                y=room_dev_ia_y,
                anchor_x="left",
                anchor_y="bottom",
                batch=self.__batch,
                group=self.__foreground,
            )
            self.__room_devices_labels.append(room_device_label)
            self.__room_devices_labels.append(room_device_ia_label)
            room_devices_counter += 1
        self.__devicelist_widget.update_box(
            new_length=room_devices_counter * gc.OFFSET_LIST_DEVICE
        )

    def __display_brightness_labels(self) -> None:
        """Display (or re-initialize) of the room brightness sensors' labels"""
        for room_brightness_label in self.__room_brightness_labels:
            room_brightness_label.delete()
        self.__room_brightness_labels = []
        room_brightness_counter = 0
        bright_x = self.__brightness_label.x
        bright_y = self.__brightness_label.y - gc.OFFSET_TITLE
        for room_device in self.__room_devices:
            if "bright" in room_device.label.text.lower():
                room_bright_x = (
                    bright_x + room_brightness_counter * gc.OFFSET_SENSOR_LEVELS
                )
                room_bright_y = bright_y
                room_brightness_counter += 1
                room_brightness_label = pyglet.text.Label(
                    "bright" + room_device.label.text[-1],
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LABEL,
                    color=gc.COLOR_FONT_SENSORS_DEVICE,
                    x=room_bright_x,
                    y=room_bright_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_brightness_labels.append(room_brightness_label)

    def __display_temperature_labels(self) -> None:
        """Display (or re-initialize) the room temperature sensors' labels"""
        for room_temperature_label in self.__room_temperature_labels:
            room_temperature_label.delete()
        self.__room_temperature_labels = []
        room_temperature_counter = 0
        temp_x = self.__temperature_label.x
        temp_y = self.__temperature_label.y - gc.OFFSET_TITLE
        for room_device in self.__room_devices:
            if "thermometer" in room_device.label.text.lower():
                room_temp_x = (
                    temp_x + room_temperature_counter * gc.OFFSET_SENSOR_LEVELS
                )
                room_temp_y = temp_y
                room_temperature_counter += 1
                room_temperature_label = pyglet.text.Label(
                    "thermo" + room_device.label.text[-1],
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LABEL,
                    color=gc.COLOR_FONT_SENSORS_DEVICE,
                    x=room_temp_x,
                    y=room_temp_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_temperature_labels.append(room_temperature_label)

    def __display_airsensor_labels(self) -> None:
        """Display (or re-initialize) the room air quality sensors' labels"""
        for room_airquality_label in self.__room_airquality_labels:
            room_airquality_label.delete()
        self.__room_airquality_labels = []
        air_x = self.__airquality_label.x
        air_y = self.__airquality_label.y - gc.OFFSET_TITLE
        previous_airsensor_name = ""
        for room_device in self.__room_devices:
            if "airsensor" in room_device.label.text.lower():
                offset_x = (
                    gc.OFFSET_SENSOR_LEVELS if len(previous_airsensor_name) else 0
                )
                previous_airsensor_name = room_device.label.text.lower()
                room_air_x = air_x + offset_x
                air_x = room_air_x
                room_air_y = air_y
                room_airquality_label = pyglet.text.Label(
                    "airsensor" + room_device.label.text[-1],
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LABEL,
                    color=gc.COLOR_FONT_SENSORS_DEVICE,
                    x=room_air_x,
                    y=room_air_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_airquality_labels.append(room_airquality_label)
            elif "co2sensor" in room_device.label.text.lower():
                offset_x = (
                    gc.OFFSET_SENSOR_LEVELS if len(previous_airsensor_name) else 0
                )
                previous_airsensor_name = room_device.label.text.lower()
                room_air_x = air_x + offset_x
                air_x = room_air_x
                room_air_y = air_y
                room_airquality_label = pyglet.text.Label(
                    "co2sensor" + room_device.label.text[-1],
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LABEL,
                    color=gc.COLOR_FONT_SENSORS_DEVICE,
                    x=room_air_x,
                    y=room_air_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_airquality_labels.append(room_airquality_label)
            elif "humidityair" in room_device.label.text.lower():
                offset_x = (
                    gc.OFFSET_SENSOR_LEVELS if len(previous_airsensor_name) else 0
                )
                previous_airsensor_name = room_device.label.text.lower()
                room_air_x = air_x + offset_x
                air_x = room_air_x
                room_air_y = air_y
                room_airquality_label = pyglet.text.Label(
                    "humidityair" + room_device.label.text[-1],
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LABEL,
                    color=gc.COLOR_FONT_SENSORS_DEVICE,
                    x=room_air_x,
                    y=room_air_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_airquality_labels.append(room_airquality_label)

    def __display_airsensors_levels(self, airsensor_dict) -> None:
        """
        Display levels of air quality (T°, HR, CO2) for corresponding labels (sensors).
        airsensor_dict = dict[sensor_name][type][value], type can be 'temperature', 'humidity' or 'co2'.
        """
        for airsensor in airsensor_dict:  # AirSensor names are the keys
            temp = hum = co2 = None
            airquality_level_text = ""
            room_airquality_counter = 0
            for room_airquality_label in self.__room_airquality_labels:
                if "airsensor" in airsensor and airsensor == room_airquality_label.text:
                    air_level_x = (
                        room_airquality_label.x
                        + room_airquality_counter * gc.OFFSET_SENSOR_LEVELS
                    )
                    air_level_y = room_airquality_label.y - gc.OFFSET_SENSOR_TITLE
                    if "temperature" in airsensor_dict[airsensor]:
                        temp = airsensor_dict[airsensor]["temperature"]
                        airquality_level_text += str(temp) + " °C/"
                    else:
                        airquality_level_text += "-/"
                    if "co2" in airsensor_dict[airsensor]:
                        co2 = airsensor_dict[airsensor]["co2"]
                        airquality_level_text += str(co2) + " ppm/"
                    else:
                        airquality_level_text += "-/"
                    if "humidity" in airsensor_dict[airsensor]:
                        hum = airsensor_dict[airsensor]["humidity"]
                        airquality_level_text += str(hum) + " %"
                    else:
                        airquality_level_text += "-"
                    airquality_levels_split_text = airquality_level_text.split("/")
                    for air_value in airquality_levels_split_text:
                        if air_value != "-":
                            room_sensor_level = pyglet.text.Label(
                                air_value,
                                font_name=gc.FONT_SYSTEM_INFO,
                                font_size=gc.FONT_SIZE_SENSOR_LEVEL,
                                color=gc.COLOR_FONT_SENSORS_VALUE,
                                x=air_level_x,
                                y=air_level_y,
                                anchor_x="left",
                                anchor_y="bottom",
                                batch=self.__batch,
                                group=self.__foreground,
                            )
                            self.__room_airsensor_levels.append(room_sensor_level)
                            air_level_y -= gc.OFFSET_AIRQUALITY_LEVELS
                    air_level_y = room_airquality_label.y - gc.OFFSET_SENSOR_TITLE
                    room_airquality_counter += 1
                elif (
                    "co2sensor" in airsensor and airsensor == room_airquality_label.text
                ):
                    air_level_x = (
                        room_airquality_label.x
                        + room_airquality_counter * gc.OFFSET_SENSOR_LEVELS
                    )
                    air_level_y = room_airquality_label.y - gc.OFFSET_SENSOR_TITLE
                    co2 = str(airsensor_dict[airsensor]["co2"]) + " ppm"
                    room_sensor_level = pyglet.text.Label(
                        co2,
                        font_name=gc.FONT_SYSTEM_INFO,
                        font_size=gc.FONT_SIZE_SENSOR_LEVEL,
                        color=gc.COLOR_FONT_SENSORS_VALUE,
                        x=air_level_x,
                        y=air_level_y,
                        anchor_x="left",
                        anchor_y="bottom",
                        batch=self.__batch,
                        group=self.__foreground,
                    )
                    self.__room_airsensor_levels.append(room_sensor_level)
                    room_airquality_counter += 1
                elif (
                    "humidityair" in airsensor
                    and airsensor == room_airquality_label.text
                ):
                    air_level_x = (
                        room_airquality_label.x
                        + room_airquality_counter * gc.OFFSET_SENSOR_LEVELS
                    )
                    air_level_y = room_airquality_label.y - gc.OFFSET_SENSOR_TITLE
                    co2 = str(airsensor_dict[airsensor]["humidity"]) + " %"
                    room_sensor_level = pyglet.text.Label(
                        co2,
                        font_name=gc.FONT_SYSTEM_INFO,
                        font_size=gc.FONT_SIZE_SENSOR_LEVEL,
                        color=gc.COLOR_FONT_SENSORS_VALUE,
                        x=air_level_x,
                        y=air_level_y,
                        anchor_x="left",
                        anchor_y="bottom",
                        batch=self.__batch,
                        group=self.__foreground,
                    )
                    self.__room_airsensor_levels.append(room_sensor_level)
                    room_airquality_counter += 1

    def __display_brightness_level(self, bright_name: str, brightness: float) -> None:
        """Display levels of brightness for corresponding label (sensor)"""
        room_brightness_counter = 0
        for room_brightness_label in self.__room_brightness_labels:
            if bright_name[-1] == room_brightness_label.text[-1]:  # digit id of sensor
                bright_level_x = room_brightness_label.x
                bright_level_y = room_brightness_label.y - gc.OFFSET_SENSOR_TITLE
                bright_level_text = str(brightness)
                room_brightness_level = pyglet.text.Label(
                    bright_level_text + " lux",
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LEVEL,
                    color=gc.COLOR_FONT_SENSORS_VALUE,
                    x=bright_level_x,
                    y=bright_level_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_brightness_levels.append(room_brightness_level)
            room_brightness_counter += 1

    def __display_temperature_level(self, temp_name: str, temperature: float) -> None:
        """Display levels of temperature for corresponding label (sensor)"""
        room_temperature_counter = 0
        for room_temperature_label in self.__room_temperature_labels:
            if temp_name[-1] == room_temperature_label.text[-1]:  # digit id of sensor
                temp_level_x = room_temperature_label.x
                temp_level_y = room_temperature_label.y - gc.OFFSET_SENSOR_TITLE
                temp_level_text = str(temperature)
                room_temperature_level = pyglet.text.Label(
                    temp_level_text + " °C",
                    font_name=gc.FONT_SYSTEM_INFO,
                    font_size=gc.FONT_SIZE_SENSOR_LEVEL,
                    color=gc.COLOR_FONT_SENSORS_VALUE,
                    x=temp_level_x,
                    y=temp_level_y,
                    anchor_x="left",
                    anchor_y="bottom",
                    batch=self.__batch,
                    group=self.__foreground,
                )
                self.__room_temperature_levels.append(room_temperature_level)
            room_temperature_counter += 1

    def __display_windows(self) -> None:
        """Display windows on room's walls, with correct size and position."""
        for gui_window in self.__gui_windows:
            gui_window.delete()
        self.__gui_windows: List[gt.WindowWidget] = []
        for window in self.room.windows:
            if window.device.wall in ["north", "south"]:
                window_widget = gt.WindowWidget(
                    window.device,
                    gc.WINDOW_HORIZONTAL_PATH,
                    self.__batch,
                    self.__foreground,
                    self.__room_width_ratio,
                    self.__room_length_ratio,
                    self.__room_widget.origin_x,
                    self.__room_widget.origin_y,
                )
            elif window.device.wall in ["east", "west"]:
                window_widget = gt.WindowWidget(
                    window.device,
                    gc.WINDOW_VERTICAL_PATH,
                    self.__batch,
                    self.__foreground,
                    self.__room_width_ratio,
                    self.__room_length_ratio,
                    self.__room_widget.origin_x,
                    self.__room_widget.origin_y,
                )
            self.__gui_windows.append(window_widget)

    def __switch_sprite(self) -> None:
        """Switch devices' sprite (image) if their state has changed."""
        for room_device in self.__room_devices:
            try:
                if (
                    room_device.sprite_state != room_device.in_room_device.device.state
                ):  # GUI device sprite state is not the same as KNX device state
                    room_device.sprite_state = room_device.in_room_device.device.state
                    room_device.sprite.delete()
                    if room_device.sprite_state:  # device turned ON
                        room_device.sprite = pyglet.sprite.Sprite(
                            room_device.img_ON,
                            x=room_device.origin_x,
                            y=room_device.origin_y,
                            batch=self.__batch,
                            group=self.__foreground,
                        )
                    else:  # device turned OFF
                        room_device.sprite = pyglet.sprite.Sprite(
                            room_device.img_OFF,
                            x=room_device.origin_x,
                            y=room_device.origin_y,
                            batch=self.__batch,
                            group=self.__foreground,
                        )
                if (
                    room_device.sprite_state
                    and room_device.sprite_state_ratio
                    != room_device.in_room_device.device.state_ratio
                ):
                    room_device.sprite_state_ratio = (
                        room_device.in_room_device.device.state_ratio
                    )
                    new_opacity = (
                        gc.OPACITY_MIN
                        + (gc.OPACITY_DEFAULT - gc.OPACITY_MIN)
                        * room_device.sprite_state_ratio
                        / 100
                    )
                    room_device.sprite.opacity = new_opacity
            except AttributeError:  # e.g. sensor have no 'state' attribute
                pass
            except:
                logging.warning(
                    f"Unable to switch sprite of {room_device.label_name} : '{sys.exc_info()[0]}'."
                )

    ### Devices and configuration file management methods ###
    def __add_device_to_simulation(
        self, room: Room, pos_x: float, pos_y: float
    ) -> None:
        """Add a device to the KNX system after user added it via the GUI (drag and drop)"""
        from system import IndividualAddress
        from tools import DEV_CLASSES

        new_device_class = self._moving_device.device_class
        # Set up dummy Individual Address
        area, line, dev_number = [
            self.__individual_address_default[i] for i in range(3)
        ]
        individual_address = IndividualAddress(area, line, dev_number)
        self.__individual_address_default[2] += 1
        if self.__individual_address_default[2] > 255:
            self.__individual_address_default[2] = 0
            self.__individual_address_default[1] += 1
            if self.__individual_address_default[1] > 15:
                self.__individual_address_default[1] = 0
                self.__individual_address_default[0] = max(
                    self.__individual_address_default[0] + 1, 15
                )
        similar_devices_counter = 1
        for device in self.__room_devices:
            if new_device_class.lower() in device.device_class.lower():
                similar_devices_counter += 1
        new_device_name = new_device_class.lower() + str(similar_devices_counter)
        # Creation of the device object
        device = DEV_CLASSES[new_device_class](
            new_device_name, individual_address
        )  # TODO#
        loc_x, loc_y = gt.gui_pos_to_system_loc(
            pos_x,
            pos_y,
            self.__room_width_ratio,
            self.__room_length_ratio,
            self.__room_widget.origin_x,
            self.__room_widget.origin_y,
        )
        loc_z = 1.0  # 1 is default height z
        self._moving_device.in_room_device = room.add_device(
            device, loc_x, loc_y, loc_z
        )
        self._moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
        self.__room_devices.append(self._moving_device)
        self.__add_device_to_config(
            new_device_name,
            new_device_class,
            str(area),
            str(line),
            str(dev_number),
            loc_x,
            loc_y,
            loc_z,
            room.name,
        )
        self.__display_brightness_labels()
        self.__display_temperature_labels()
        self.__display_airsensor_labels()

    def __update_device_location(self, pos_x: float, pos_y: float) -> None:
        """Update the device location in the GUI Window"""
        loc_x, loc_y = gt.gui_pos_to_system_loc(
            pos_x,
            pos_y,
            self.__room_width_ratio,
            self.__room_width_ratio,
            self.__room_widget.origin_x,
            self.__room_widget.origin_y,
        )
        self._moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
        self.__update_config_loc(loc_x, loc_y, self.room.name)

    def __replace_moving_device_in_room(self, x: float, y: float) -> None:
        """Replace the device at the closest point in the room if user drops it outside the GUI room widget box"""
        from system import Location

        x_min = self.__room_widget.origin_x
        x_max = self.__room_widget.origin_x + self.__room_widget.width
        y_min = self.__room_widget.origin_y
        y_max = self.__room_widget.origin_y + self.__room_widget.length
        new_x = x_min if x < x_min else x
        new_x = x_max if x_max < new_x else new_x
        new_y = y_min if y < y_min else y
        new_y = y_max if y_max < new_y else new_y
        loc_x, loc_y = gt.gui_pos_to_system_loc(
            new_x,
            new_y,
            self.__room_width_ratio,
            self.__room_width_ratio,
            self.__room_widget.origin_x,
            self.__room_widget.origin_y,
        )
        self._moving_device.update_position(new_x, new_y, loc_x, loc_y, update_loc=True)
        self.__update_config_loc(loc_x, loc_y, self.room.name)

    def __add_device_to_config(
        self,
        dev_name: str,
        dev_class: str,
        area: str,
        line: str,
        dev_number: str,
        loc_x: float,
        loc_y: float,
        loc_z: float,
        room_name: str,
    ) -> None:  # TODO#
        """Update with a new device the configuration dict respresenting the current GUI system"""
        knx_config = self.system_config_dict["knx"]
        area_key = "area" + area
        line_key = "line" + line
        knx_loc = ".".join([area, line, dev_number])
        line_devices = knx_config[area_key][line_key]["devices"]
        line_devices[dev_name] = {"class": dev_class, "knx_location": knx_loc}
        world_config = self.system_config_dict["world"]
        for room in world_config["rooms"]:
            if world_config["rooms"][room]["name"] == room_name:
                world_config["rooms"][room]["room_devices"][dev_name] = [
                    loc_x,
                    loc_y,
                    loc_z,
                ]

    def __update_config_loc(self, loc_x: float, loc_y: float, room_name: str) -> None:
        """Update the moving device's location in the system configuration dict"""
        loc_z = 1.0
        dev_name = self._moving_device.in_room_device.device.name
        world_config = self.system_config_dict["world"]
        for room in world_config["rooms"]:
            if world_config["rooms"][room]["name"] == room_name:
                world_config["rooms"][room]["room_devices"][dev_name] = [
                    loc_x,
                    loc_y,
                    loc_z,
                ]

    def __update_config_ga(
        self, room_device: gt.DeviceWidget, group_address: str, detach: bool = False
    ) -> int:
        """Update the configuration file with new group address and/or new device members"""
        dev_name = room_device.in_room_device.device.name
        gas_config = self.system_config_dict["knx"]["group_addresses"]
        for g in range(len(gas_config)):  # gas_config is a list of dict: [{},{}]
            ga = gas_config[g]
            if group_address == ga["address"]:
                if dev_name not in ga["group_devices"]:
                    ga["group_devices"].append(dev_name)
                    logging.info(
                        f"The {dev_name} is added to device list of group address {group_address} in temporary config dict."
                    )
                    return 1
                else:  # If device already assigned to this group address
                    if detach:
                        ga["group_devices"].remove(dev_name)
                        logging.info(
                            f"The {dev_name} is removed from device list of group address {group_address} in temporary config dict."
                        )
                        if (
                            len(ga["group_devices"]) < 1
                        ):  # If no more devices are linked to this ga
                            del gas_config[g]
                            logging.info(
                                f"The group address {group_address} is removed from temporary config dict because no device is attached to it."
                            )
                            return 0
                    return 1
        # If this group address does not exist yet
        new_ga = {"address": group_address, "group_devices": [dev_name]}
        gas_config.append(new_ga)
        logging.info(
            f"The group address {group_address} is added with {dev_name} attached to it in temporary config dict."
        )

    def __launch_vacuum(self) -> None:
        """Launch vacuum cleaner animation"""
        if not hasattr(self, "vacuum_widget"):
            self.vacuum_widget = gt.VacuumWidget(
                gc.VACUUM_PATH, 1400, 650, self.__batch, self.__middleground
            )

    ## Public methods ##
    def initialize_system(
        self, save_config: bool = False, config_path: str = "", system_dt: float = 1
    ):
        """Initialize gui system from room configuration file (empty, default or other JSON file)"""
        self.room.gui_window = self
        if save_config:
            if len(config_path) == 0:
                config_path = self.__CONFIG_PATH
                self.__SYSTEM_DT = system_dt
            with open(config_path, "r") as config_file:
                self.system_config_dict = json.load(config_file)
        pyglet.clock.schedule_interval(
            self.room.update_world, interval=system_dt, gui_mode=True
        )
        # Ratio to translate room physical (simulated) size from meters to pixels
        self.__room_width_ratio = gc.ROOM_WIDTH / self.room.width
        self.__room_length_ratio = gc.ROOM_LENGTH / self.room.length

        logging.info(
            " ------- Initialization of the KNX System's GUI representation ------- "
        )
        for in_room_device in self.room.devices:
            gui_device = getattr(
                self.__available_devices, type(in_room_device.device).__name__.lower()
            )
            pos_x, pos_y = gt.system_loc_to_gui_pos(
                in_room_device.location.x,
                in_room_device.location.y,
                self.__room_width_ratio,
                self.__room_length_ratio,
                self.__room_widget.origin_x,
                self.__room_widget.origin_y,
            )
            logging.info(
                f"{in_room_device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}."
            )
            if "thermometer" in gui_device.label_name:
                img_neutral = gc.DEVICE_THERMO_NEUTRAL_PATH
            else:
                img_neutral = None
            device_widget = gt.DeviceWidget(
                pos_x,
                pos_y,
                self.__batch,
                gui_device.file_ON,
                gui_device.file_OFF,
                group=self.__foreground,
                device_class=in_room_device.name[:-1],
                device_number=in_room_device.name[-1],
                img_neutral=img_neutral,
            )
            device_widget.in_room_device = in_room_device
            self.__room_devices.append(device_widget)
        self.__display_devices_list()
        self.__display_brightness_labels()
        self.__display_temperature_labels()
        self.__display_airsensor_labels()
        self.__display_windows()

    def update_sensors(
        self,
        brightness_levels: List[Tuple[str, float]],
        temperature_levels: List[Tuple[str, float]],
        rising_temp: bool,
        humidity_levels: List[Tuple[str, float]],
        co2_levels: List[Tuple[str, float]],
        humiditysoil_levels: List[Tuple[str, float]],
        presence_sensors_states: List[Tuple[str, bool]],
    ) -> None:
        """Display (re-Initialisation) of the room sensors list with updated values"""
        for room_brightness_level in self.__room_brightness_levels:
            room_brightness_level.delete()
        self.__room_brightness_levels = []
        for room_temperature_level in self.__room_temperature_levels:
            room_temperature_level.delete()
        self.__room_temperature_levels = []
        for room_sensor_level in self.__room_airsensor_levels:
            room_sensor_level.delete()
        self.__room_airsensor_levels = []
        airsensor_dict = {}

        for bright in brightness_levels:
            bright_name, brightness = bright[0], round(bright[1], 1)
            self.__display_brightness_level(bright_name, brightness)
        for temp in temperature_levels:
            temp_name, temperature = temp[0], round(temp[1], 2)
            self.__display_temperature_level(temp_name, temperature)
            for room_device in self.__room_devices:
                if "thermometer" in room_device.label_name:
                    room_device.update_thermometer_sprite(rising_temp)
            if "air" in temp_name:
                try:
                    airsensor_dict[temp_name]["temperature"] = temperature
                except KeyError:
                    airsensor_dict[temp_name] = {}
                    airsensor_dict[temp_name]["temperature"] = temperature
        for hum in humidity_levels:
            hum_name, humidity = hum[0], hum[1]
            if "air" or "humidityair" in hum_name:
                try:
                    airsensor_dict[hum_name]["humidity"] = humidity
                except KeyError:
                    airsensor_dict[hum_name] = {}
                    airsensor_dict[hum_name]["humidity"] = humidity
        for co2 in co2_levels:
            co2_name, co2 = co2[0], co2[1]
            if "air" or "co2" in co2_name:
                try:
                    airsensor_dict[co2_name]["co2"] = co2
                except KeyError:
                    airsensor_dict[co2_name] = {}
                    airsensor_dict[co2_name]["co2"] = co2

        if len(airsensor_dict) > 0:
            self.__display_airsensors_levels(airsensor_dict)

        for humsoil in humiditysoil_levels:
            humsoil_name, humiditysoil = humsoil[0], humsoil[1]
            for room_device in self.__room_devices:
                if humsoil_name == room_device.label_name:
                    if hasattr(room_device, "humiditysoil"):
                        room_device.humiditysoil = humiditysoil
                        room_device.update_drop_sprite()
        for presence in presence_sensors_states:
            pres_name, _ = presence[0], presence[1]
            for room_device in self.__room_devices:
                if pres_name == room_device.label_name:
                    self.__switch_sprite()

    def reload_simulation(
        self, default_config: bool = False, empty_config: bool = False
    ) -> None:
        """Reload the simulation with initial configuration file"""
        from tools import configure_system_from_file

        pyglet.clock.unschedule(self.room.update_world)
        for (
            room_device
        ) in self.__room_devices:  # Re-Initialisation of the room devices list
            room_device.delete()
        self.__room_devices = []
        if hasattr(self, "person_sitting"):  # Removal of person img
            self.person_sitting.delete()
        if hasattr(self, "person_child"):
            self.person_child.delete()
        for (
            room_brightness_label
        ) in (
            self.__room_brightness_labels
        ):  # Re-Initialisation of the room brightness labels list
            room_brightness_label.delete()
        self.__room_brightness_labels = []
        for (
            room_device_label
        ) in (
            self.__room_devices_labels
        ):  # Re-Initialisation of the room device labels list
            room_device_label.delete()
        self.__room_devices_labels = []
        self.__button_pause.update_sprite(
            reload=True
        )  # Re-initialization of Pause button
        if default_config:  # Re-configuration of the room and simulation time
            config_path = self.__DEFAULT_CONFIG_PATH
        elif empty_config:
            config_path = self.__EMPTY_CONFIG_PATH
        else:
            config_path = self.__CONFIG_PATH
        self.room, self.__SYSTEM_DT = configure_system_from_file(
            config_path,
            svshi_mode=self.__svshi_mode,
            telegram_logging=self.__telegram_logging,
        )
        # Re-initialization of day time and weather
        self.daytimeweather_widget.delete()
        self.daytimeweather_widget = gt.DayTimeWeatherWidget(
            gc.TIMEWEATHER_POS[0],
            gc.TIMEWEATHER_POS[1],
            self.__batch,
            group_box=self.__background,
            group_daytime=self.__middleground,
            group_weather=self.__foreground,
            temp_out=self.room.world.ambient_temperature.temperature_out,
            hum_out=self.room.world.ambient_humidity.humidity_out,
            co2_out=self.room.world.ambient_co2.co2_out,
        )
        self.room.world.time.start_time = time()
        self.initialize_system(
            save_config=True, config_path=config_path, system_dt=self.__SYSTEM_DT
        )

    def pause_simulation(self) -> None:
        """Method called when pressing pause button, stores the time of the pause to resume with the correct simtime"""
        self.room.simulation_status = not self.room.simulation_status
        if not self.room.simulation_status:
            logging.info("The simulation is paused...")
            self.__sleep_time_till_next_update = pyglet.clock.get_sleep_time(True)
        else:
            if self.__sleep_time_till_next_update:
                sleep(self.__sleep_time_till_next_update)
            logging.info("The simulation is resumed !")

    def redraw(self) -> None:
        """When SVSHI_MODE, redraw device sprites, in case telegrams have delay from svshi program"""
        self.__switch_sprite()
        self.clear()
        self.__batch.draw()

    ## Pyglet 'on-event' methods ##
    def on_draw(self) -> None:
        """Called when the window is redrawn (at every pyglet event):
        Draw all the elements added to the batch in the window on each event (mouse click, drag,...)"""
        self.clear()
        self.__batch.draw()

    def on_text(self, text: str) -> None:
        """Called when the user press a keyboard symbol (all keys except modifiers):
        Add the text input by the user to the text label displayed in the text box"""
        self.__input_label.text += text

    ### Key events ###
    def on_key_press(self, symbol, modifiers) -> None:
        """Called when any key is pressed:
        Define special action to modify text, save input text or end the simulation"""
        # BACKSPACE to erase a character from the user input textbox
        if symbol == pyglet.window.key.BACKSPACE:
            self.__input_label.text = self.__input_label.text[
                :-1
            ]  # Remove last character
        # ENTER to parse the command input by the user and erase it from the text box
        elif symbol == pyglet.window.key.ENTER:
            from tools import user_command_parser

            if user_command_parser(self.__input_label.text, self.room) is None:
                pyglet.app.exit()  # If user quit the simulation through CLI (q or quit)
            self.__switch_sprite()
            self.__input_label.text = ""
        # CTRL-ESCAPE to end the simulation
        elif symbol == pyglet.window.key.ESCAPE:
            if modifiers and pyglet.window.key.MOD_CTRL:
                pyglet.app.exit()
        # CTRL-P to Pause/Play simulation
        elif symbol == pyglet.window.key.P:
            if modifiers and pyglet.window.key.MOD_CTRL:
                self.__button_pause.activate(self)
                self.__button_pause.update_sprite()
        # CTRL-R to reload simulation from start
        elif symbol == pyglet.window.key.R:
            if modifiers and pyglet.window.key.MOD_CTRL:
                self.reload_simulation()
        # CTRL-SPACE to add the vacuum robot
        elif symbol == pyglet.window.key.SPACE:
            if modifiers and pyglet.window.key.MOD_OPTION:
                if hasattr(self, "vacuum_widget"):
                    self.vacuum_widget.delete()
                    delattr(self, "vacuum_widget")
                else:
                    self.__launch_vacuum()

    def on_key_release(self, symbol, modifiers) -> None:
        """Called when a key is released:
        Define actions to take when specific keys are released"""
        # Cancel the Group Adddress linking if CRTL key is released
        if symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL:
            for room_device in self.__room_devices:
                room_device.sprite.opacity = gc.OPACITY_DEFAULT
            for button in self.__buttons:
                button.widget.sprite.opacity = gc.OPACITY_DEFAULT
        # Cancel the Dimmer ratio setting if SHIFT key is released before the mouse is released to validate the value
        if symbol == pyglet.window.key.LSHIFT or symbol == pyglet.window.key.RSHIFT:
            if hasattr(self, "_dimmer_being_set"):
                self._dimmer_being_set.delete()
                delattr(self, "_dimmer_being_set")

    ### Mouse events ###
    def on_mouse_press(self, x, y, button, modifiers) -> None:
        """Called when a mouse button is pressed (LEFT, RIGHT or MIDDLE):
        Defines multiple action to do when one of the mouse button is pressed"""
        if button == pyglet.window.mouse.LEFT:
            # LEFT click + SHIFT : activate functional module (e.g. turn button ON/OFF)
            if modifiers & pyglet.window.key.MOD_SHIFT:
                from devices import HumiditySoil, FunctionalModule, Button, Dimmer

                for room_device in self.__room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if isinstance(
                            room_device.in_room_device.device, FunctionalModule
                        ):
                            if isinstance(room_device.in_room_device.device, Dimmer):
                                # Create an object to set the dimmer value, and validate by releasing the mouse with SHIFT pressed
                                self._dimmer_being_set = gt.DimmerSetterWidget(
                                    room_device
                                )
                                return
                            elif isinstance(room_device.in_room_device.device, Button):
                                room_device.in_room_device.device.user_input()
                                self.__switch_sprite()
                        if isinstance(room_device.in_room_device.device, HumiditySoil):
                            if hasattr(room_device, "humiditysoil"):
                                room_device.humiditysoil = (
                                    room_device.in_room_device.device.humiditysoil
                                ) = 90  # Fully wet loam soil
                                room_device.update_drop_sprite()
            # LEFT click + CTRL : assign a group address to a device
            elif modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.__room_devices:
                    if room_device.hit_test(x, y):
                        if self.room.attach(
                            room_device.in_room_device.device, self.__input_label.text
                        ):
                            self.__update_config_ga(
                                room_device, self.__input_label.text
                            )
                        self.__display_devices_list()
            # LEFT click + OPTION : add/remove persons
            elif modifiers & pyglet.window.key.MOD_OPTION:
                if hasattr(self, "person_child"):
                    child = True
                else:
                    child = False
                if hasattr(self, "person_sitting"):
                    sitting = True
                else:
                    sitting = False
                if child and sitting:
                    if self.person_child.hit_test(x, y):
                        self.person_moving = self.person_child
                    elif self.person_sitting.hit_test(x, y):
                        self.person_moving = self.person_sitting
                if child and not sitting:
                    if self.person_child.hit_test(x, y):
                        self.person_moving = self.person_child
                    else:
                        self.person_moving = self.person_sitting = gt.PersonWidget(
                            gc.PERSON_SITTING_PATH,
                            x,
                            y,
                            self.__batch,
                            self.__foreground,
                        )
                        self.room.world.presence.add_entity("person_sitting")
                        self.__switch_sprite()
                if sitting and not child:
                    if self.person_sitting.hit_test(x, y):
                        self.person_moving = self.person_sitting
                    else:
                        self.person_moving = self.person_child = gt.PersonWidget(
                            gc.PERSON_CHILD_PATH, x, y, self.__batch, self.__foreground
                        )
                        self.room.world.presence.add_entity("person_child")
                        self.__switch_sprite()
                if not child and not sitting:
                    self.person_moving = self.person_sitting = gt.PersonWidget(
                        gc.PERSON_SITTING_PATH, x, y, self.__batch, self.__foreground
                    )
                    self.room.world.presence.add_entity("person_sitting")
                    self.__switch_sprite()
            # LEFT click on device w/o modifiers : click on GUI Buttons or move/add devices in room
            else:
                if not hasattr(self, "_moving_device"):
                    for device in self.__available_devices.devices:
                        if device.hit_test(x, y):
                            device_class = device.device_class
                            similar_dev_counter = 1
                            for room_device in self.__room_devices:
                                if (
                                    room_device.device_class.lower()
                                    in device_class.lower()
                                ):
                                    similar_dev_counter += 1
                            self._moving_device = gt.DeviceWidget(
                                x,
                                y,
                                self.__batch,
                                device.file_ON,
                                device.file_OFF,
                                group=self.__foreground,
                                device_class=device_class,
                                device_number=str(similar_dev_counter),
                            )
                            return
                    for room_device in self.__room_devices:
                        if room_device.hit_test(x, y):
                            self._moving_device = room_device
                            self._moving_device.update_position(new_x=x, new_y=y)
                # Click on GUI Buttons
                for button in self.__buttons:
                    if button.widget.hit_test(x, y):
                        button.widget.sprite.opacity = gc.OPACITY_CLICKED
                        button.activate(self)
        if button == pyglet.window.mouse.RIGHT:
            # RIGHT click + CTRL : Remove device from group address entered in the command box
            if modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.__room_devices:
                    if room_device.hit_test(x, y):
                        if self.room.detach(
                            room_device.in_room_device.device, self.__input_label.text
                        ):
                            self.__update_config_ga(
                                room_device, self.__input_label.text, detach=True
                            )
                        self.__display_devices_list()
            # RIGHT click + OPTION : Remove person img
            elif modifiers & pyglet.window.key.MOD_OPTION:
                if hasattr(self, "person_sitting"):
                    if self.person_sitting.hit_test(x, y):
                        self.person_sitting.delete()
                        delattr(self, "person_sitting")
                        self.room.world.presence.remove_entity("person_sitting")
                        self.__switch_sprite()
                if hasattr(self, "person_child"):
                    if self.person_child.hit_test(x, y):
                        self.person_child.delete()
                        delattr(self, "person_child")
                        self.room.world.presence.remove_entity("person_child")
                        self.__switch_sprite()
            # RIGHT click : Empty config from default Button
            else:
                for button in self.__buttons:
                    if button.widget.hit_test(x, y) and isinstance(
                        button, gt.ButtonDefault
                    ):
                        self.reload_simulation(empty_config=True)

    def on_mouse_release(self, x, y, button, modifiers) -> None:
        """Called when a mouse button is released (LEFT, RIGHT or MIDDLE):
        Define multiple action to do when one of the mouse button is released"""
        # The LEFT button is used to select and manage devices  (position, group addresses, activation,...)
        if button == pyglet.window.mouse.LEFT:
            # LEFT + SHIFT
            if modifiers & pyglet.window.key.MOD_SHIFT:
                if hasattr(self, "_dimmer_being_set"):
                    # If mouse was not dragged but only pressed (to turn ON/OFF dimmer)
                    if not self._dimmer_being_set.being_set:
                        self._dimmer_being_set.room_dimmer_widget.in_room_device.device.user_input()
                    else:  # If mouse was dragged while pressing left button to set dimmer ratio
                        new_ratio = gt.dimmer_ratio_from_mouse_pos(
                            y, self._dimmer_being_set.center_y
                        )
                        if new_ratio == 0:
                            new_state = False
                        else:
                            new_state = True
                        self._dimmer_being_set.room_dimmer_widget.in_room_device.device.user_input(
                            state=new_state, state_ratio=new_ratio
                        )
                    self.__switch_sprite()
                    self._dimmer_being_set.delete()
                    delattr(self, "_dimmer_being_set")
            # LEFT + OPTION : stop moving person_child
            if modifiers & pyglet.window.key.MOD_OPTION:
                if hasattr(self, "person_moving"):
                    if self.person_moving.hit_test(x, y):
                        self.person_moving.update_position(x, y)
                        delattr(self, "person_moving")
            # If there is a moving device, the release of LEFT button places the device in the room
            elif hasattr(self, "_moving_device"):
                if self.__room_widget.hit_test(x, y):
                    pos_x, pos_y = x, y
                    if self._moving_device not in self.__room_devices:
                        self.__add_device_to_simulation(self.room, pos_x, pos_y)
                    else:  # New device
                        if not (modifiers & pyglet.window.key.MOD_SHIFT):
                            self.__update_device_location(pos_x, pos_y)
                    self.__display_devices_list()
                    delattr(self, "_moving_device")
                else:  # Device dropped out of room widget
                    if self._moving_device in self.__room_devices:
                        self.__replace_moving_device_in_room(x, y)
                    else:
                        self._moving_device.delete()
                    delattr(self, "_moving_device")
            # Mouse released after clicked on GUI Buttons
            for button in self.__buttons:
                if button == self.__button_pause and hasattr(
                    self.__button_pause, "clicked"
                ):
                    button.update_sprite()
                    delattr(self.__button_pause, "clicked")
                button.widget.sprite.opacity = gc.OPACITY_DEFAULT

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        """Called when the mouse is dragged:
        Drag device accross the GUI if there is a moving device defined"""
        # Mouse drag + SHIFT : to set the dimmer ratio after clicking on it
        if modifiers & pyglet.window.key.MOD_SHIFT:
            if hasattr(self, "_dimmer_being_set"):
                if not self._dimmer_being_set.being_set:
                    self._dimmer_being_set.start_setting_dimmer(
                        self.__batch, self.__foreground
                    )
                new_ratio = gt.dimmer_ratio_from_mouse_pos(
                    y, self._dimmer_being_set.center_y
                )
                self._dimmer_being_set.update_ratio(new_ratio)
        # Mouse drag + OPTION : move person img
        if modifiers & pyglet.window.key.MOD_OPTION:
            if hasattr(self, "person_moving"):
                self.person_moving.update_position(x, y)
        # Mouse drag w/o modifiers to move 'moving' device
        else:
            if buttons & pyglet.window.mouse.LEFT:
                if hasattr(self, "_moving_device"):
                    self._moving_device.update_position(new_x=x, new_y=y)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) -> None:
        """Called when the mouse is scrolled:
        scroll in room devices list"""
        if self.__devicelist_widget.hit_test(x, y):
            self.__display_devices_list(scroll=np.sign(scroll_y))


# Cannot be a class method because first argument must be dt for scheduling, and thus cannot be self.
def update_gui_window(
    dt,
    window,
    date_time,
    current_str_simulation_time,
    weather,
    time_of_day,
    lux_out,
    svshi_mode,
) -> None:
    """Functions called with the pyglet scheduler
    Update the Simulation Time, Date and Weather displayed"""
    if (
        svshi_mode
    ):  # Redraw devices images to take into account delay of telegram from svshi
        window.redraw()
    if hasattr(window, "vacuum_widget"):
        window.vacuum_widget.move()
    sim_time = current_str_simulation_time
    datetime_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
    window.simtime_widget.simtime_value.text = f"{sim_time}"
    window.simtime_widget.date_value.text = f"{datetime_str}"
    window.daytimeweather_widget.update_out_state(weather, time_of_day, lux_out)
    print(f"World state update at simulation time: {sim_time}", end="\r")
