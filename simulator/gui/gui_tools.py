""" 
Module defining the GUI object classes to implement devices, room and other system elements' widge
"""

import logging
import json
from abc import abstractmethod
from datetime import datetime

import pyglet
from pyglet.graphics import Batch, OrderedGroup
from typing import List, Tuple

import gui.gui_config as gc


class DeviceListWidget(object):
    """Class to represent room devices list and its GUI Box"""

    def __init__(
        self,
        x: float,
        y: float,
        batch: Batch,
        group_label: OrderedGroup,
        group_box: OrderedGroup,
    ) -> None:
        """
        Initialization of pyglet Device List widget object.
        group_box should be behind group_label.
        """
        self.__batch = batch
        self.__group_box = group_box
        self.__topleft_y = y + gc.OFFSET_DEVICELIST_BOX_TOP
        self.__length = gc.OFFSET_DEVICELIST_BOX_TOP + gc.OFFSET_DEVICELIST_BOX_BOTTOM
        # Max number of devices to display in list
        self.MAX_SIZE_DEVICES_LIST = (
            y - gc.OFFSET_LIST_DEVICE
        ) // gc.OFFSET_LIST_DEVICE
        self.__box_shape = pyglet.shapes.BorderedRectangle(
            gc.WIN_BORDER / 2,
            self.__topleft_y - self.__length,
            gc.DEVICE_LIST_BOX_WIDTH,
            self.__length,
            border=gc.BOX_BORDER,
            color=gc.COLOR_BOX_DEVICESLIST,
            border_color=gc.COLOR_BOX_DEVICESLIST_BORDER,
            batch=batch,
            group=self.__group_box,
        )
        self.deviceslist_title = pyglet.text.Label(
            "Devices in the Room:",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=15,
            bold=True,
            color=gc.COLOR_FONT_DEVICESLIST_TITLE,
            x=x,
            y=y,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch,
            group=group_label,
        )

    def update_box(self, new_length: int) -> None:
        """
        Update devices list box.
        new_length = number of devices * offset between them.
        """
        new_length = new_length if new_length > 0 else gc.OFFSET_DEVICELIST_BOX_TOP
        self.__length = (
            new_length + gc.OFFSET_DEVICELIST_BOX_TOP + gc.OFFSET_DEVICELIST_BOX_BOTTOM
        )
        self.__box_shape.delete()
        self.__box_shape = pyglet.shapes.BorderedRectangle(
            gc.WIN_BORDER / 2,
            self.__topleft_y - self.__length,
            gc.DEVICE_LIST_BOX_WIDTH,
            height=self.__length,
            border=gc.BOX_BORDER,
            color=gc.COLOR_BOX_DEVICESLIST,
            border_color=gc.COLOR_BOX_DEVICESLIST_BORDER,
            batch=self.__batch,
            group=self.__group_box,
        )

    def hit_test(self, x: float, y: float) -> bool:
        """Test if DeviceList widget was hit by the mouse."""
        return self.__box_shape.x < x < (
            self.__box_shape.x + gc.DEVICE_LIST_BOX_WIDTH
        ) and self.__box_shape.y < y < (self.__box_shape.y + self.__length)


class SimTimeWidget(object):
    """Class to represent the simulation time, date and their GUI box"""

    def __init__(
        self,
        x: float,
        y: float,
        batch: Batch,
        group_box: OrderedGroup,
        group_label: OrderedGroup,
    ) -> None:
        """
        Initialization of pyglet Device List widget object.
        group_box should be behind group_label.
        """
        self.__box_shape = pyglet.shapes.BorderedRectangle(
            x,
            y - gc.SIMTIME_BOX_LENGTH / 2,
            gc.SIMTIME_BOX_WIDTH,
            gc.SIMTIME_BOX_LENGTH,
            border=gc.BOX_BORDER,
            color=gc.COLOR_BOX_SIMTIME,
            border_color=gc.COLOR_BOX_SIMTIME_BORDER,
            batch=batch,
            group=group_box,
        )
        self.__simtime_label = pyglet.text.Label(
            "SimTime:",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=gc.FONT_SIZE_DATETIME_TITLE,
            bold=True,
            color=gc.COLOR_FONT_SIMTIME_LABEL,
            x=x + gc.OFFSET_SIMTIME_BOX,
            y=y,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch,
            group=group_label,
        )
        self.simtime_value = pyglet.text.Label(
            "0:00:00",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=gc.FONT_SIZE_SIMTIME,
            bold=True,
            color=gc.COLOR_FONT_SIMTIME_VALUE,
            x=x + gc.OFFSET_SIMTIME_BOX + gc.OFFSET_SIMTIME_VALUE,
            y=y,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch,
            group=group_label,
        )
        self.__date_label = pyglet.text.Label(
            "Date: ",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=gc.FONT_SIZE_DATETIME_TITLE,
            bold=True,
            color=gc.COLOR_FONT_SIMTIME_LABEL,
            x=x + gc.OFFSET_SIMTIME_BOX,
            y=y - gc.OFFSET_SIMTIME_DATE,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch,
            group=group_label,
        )
        self.date_value = pyglet.text.Label(
            "",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=gc.FONT_SIZE_DATE,
            bold=True,
            color=gc.COLOR_FONT_SIMTIME_VALUE,
            x=x + gc.OFFSET_SIMTIME_BOX + gc.OFFSET_DATETIME_VALUE,
            y=y - gc.OFFSET_SIMTIME_DATE,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch,
            group=group_label,
        )


class DayTimeWeatherWidget(object):
    """Class to represent the simulation outside weather, outside states and their GUI box"""

    def __init__(
        self,
        x: float,
        y: float,
        batch: Batch,
        group_box: OrderedGroup,
        group_daytime: OrderedGroup,
        group_weather: OrderedGroup,
        temp_out: float,
        hum_out: float,
        co2_out: float,
    ) -> None:
        """
        Initialization of pyglet Device List widget object.
        group_box should be behind group_daytime, which should be behind group_weather.
        """
        self.__pos_x = x
        self.__pos_y = y
        self.__batch = batch
        self.__group_weather = group_weather
        self.__group_daytime = group_daytime
        self.__temp_out, self.__hum_out, self.__co2_out = temp_out, hum_out, co2_out
        self.__box_shape = pyglet.shapes.BorderedRectangle(
            self.__pos_x,
            self.__pos_y,
            gc.TIMEWEATHER_BOX_WIDTH,
            gc.TIMEWEATHER_BOX_LENGTH,
            border=gc.BOX_BORDER,
            color=gc.COLOR_BOX_WEATHER,
            border_color=gc.COLOR_BOX_WEATHER_BORDER,
            batch=self.__batch,
            group=group_box,
        )
        self.__out_state_str = f"{self.__temp_out}°C  {self.__hum_out}%  {self.__co2_out}ppm  "  # out_lux is added later
        self.__out_state_label = pyglet.text.Label(
            "Out state:",
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=gc.FONT_SIZE_OUT_STATE,
            bold=True,
            color=gc.COLOR_FONT_OUTSTATE_LABEL,
            x=self.__pos_x + gc.OFFSET_OUTSTATE_LABEL,
            y=self.__pos_y + gc.OFFSET_OUTSTATE_LABEL,
            anchor_x="left",
            anchor_y="bottom",
            batch=self.__batch,
            group=self.__group_daytime,
        )
        self.__out_state_value = pyglet.text.Label(
            self.__out_state_str,
            font_name=gc.FONT_SYSTEM_TITLE,
            font_size=gc.FONT_SIZE_OUT_STATE,
            bold=True,
            color=gc.COLOR_FONT_OUTSTATE_VALUE,
            x=self.__pos_x + gc.OFFSET_OUTSTATE_LABEL + gc.OFFSET_OUTSTATE_VALUE,
            y=self.__pos_y + gc.OFFSET_OUTSTATE_LABEL,
            anchor_x="left",
            anchor_y="bottom",
            batch=self.__batch,
            group=self.__group_daytime,
        )
        self.__sunrise_img = pyglet.image.load(gc.SUNRISE_PATH)
        self.__sun_img = pyglet.image.load(gc.SUN_PATH)
        self.__sunset_img = pyglet.image.load(gc.SUNSET_PATH)
        self.__moon_img = pyglet.image.load(gc.MOON_PATH)
        self.__cloud_overcast_img = pyglet.image.load(gc.CLOUD_OVERCAST_PATH)
        self.__cloud_dark_img = pyglet.image.load(gc.CLOUD_DARK_PATH)
        self.__tod_dict = {
            "sunrise": {
                "img": self.__sunrise_img,
                "offset_x": gc.OFFSET_SUNRISE_X,
                "offset_y": gc.OFFSET_SUNRISE_SUNSET_Y,
            },
            "sun": {
                "img": self.__sun_img,
                "offset_x": gc.OFFSET_SUN_MOON_X,
                "offset_y": gc.OFFSET_SUN_MOON_Y,
            },
            "sunset": {
                "img": self.__sunset_img,
                "offset_x": gc.OFFSET_SUNSET_X,
                "offset_y": gc.OFFSET_SUNRISE_SUNSET_Y,
            },
            "moon": {
                "img": self.__moon_img,
                "offset_x": gc.OFFSET_SUN_MOON_X,
                "offset_y": gc.OFFSET_SUN_MOON_Y,
            },
        }
        self.__weather_dict = {
            "overcast": {
                "img": self.__cloud_overcast_img,
                "offset_x_ratio": gc.OFFSET_CLOUD_WIDTH_RATIO,
                "offset_y_ratio": gc.OFFSET_CLOUD_LENGTH_RATIO,
            },
            "dark": {
                "img": self.__cloud_dark_img,
                "offset_x_ratio": gc.OFFSET_CLOUD_DARK_WIDTH_RATIO,
                "offset_y_ratio": gc.OFFSET_CLOUD_DARK_LENGTH_RATIO,
            },
        }
        self._tod_sprite = None
        self._weather_sprite = None

    def update_out_state(self, weather: str, time_of_day: str, lux_out: float) -> None:
        """
        Update outside physical states in GUI.
        weather is 'clear', 'overcast' or 'dark',
        time_of_day is 'sunrise', 'sun', 'sunset, 'moon'
        """
        if self._tod_sprite is not None:
            self._tod_sprite.delete()
        if self._weather_sprite is not None:
            self._weather_sprite.delete()
        self.__lux_out = round(lux_out, 1) if lux_out > 1 else lux_out
        new_out_states = self.__out_state_str + str(self.__lux_out) + "lux"
        self.__out_state_value.text = new_out_states
        if time_of_day in self.__tod_dict:
            self._tod_sprite = pyglet.sprite.Sprite(
                self.__tod_dict[time_of_day]["img"],
                self.__pos_x + self.__tod_dict[time_of_day]["offset_x"],
                self.__pos_y + self.__tod_dict[time_of_day]["offset_y"],
                batch=self.__batch,
                group=self.__group_daytime,
            )
        if weather in self.__weather_dict:
            self._weather_sprite = pyglet.sprite.Sprite(
                self.__weather_dict[weather]["img"],
                self._tod_sprite.x
                + self.__weather_dict[weather]["offset_x_ratio"]
                * self._tod_sprite.width,
                self._tod_sprite.y
                + self.__weather_dict[weather]["offset_y_ratio"]
                * self._tod_sprite.height,
                batch=self.__batch,
                group=self.__group_weather,
            )

    def delete(self):
        """Delete all components of the DayTimeWeather widget."""
        if self._tod_sprite is not None:
            self._tod_sprite.delete()
        if self._weather_sprite is not None:
            self._weather_sprite.delete()
        self.__out_state_label.delete()
        self.__out_state_value.delete()
        self.__box_shape.delete()


class WindowWidget(object):
    """Class to represent the simulated rooms' windows in GUI"""

    from system.system_tools import Window

    def __init__(
        self,
        window_object: Window,
        window_file: str,
        batch: Batch,
        group: OrderedGroup,
        room_width_ratio: float,
        room_height_ratio: float,
        room_origin_x: float,
        room_origin_y: float,
    ) -> None:
        """
        Initialization of pyglet Window widget object.

        room_width_ratio and room_height_ratio translate simulation meters to GUI pixels.
        room_origin_x and room_origin_y are the bottom left corner of the room widget.
        loc for room's location in meters, pos for GUI position in pixels.
        """
        self.__batch = batch
        self.__group = group
        self.__img = pyglet.image.load(window_file)
        self.__img.anchor_x = self.__img.width // 2
        self.__img.anchor_y = self.__img.height // 2
        self.__loc_x, self.__loc_y = (
            window_object.window_loc[0],
            window_object.window_loc[1],
        )
        self.__pos_x, self.__pos_y = system_loc_to_gui_pos(
            self.__loc_x,
            self.__loc_y,
            room_width_ratio,
            room_height_ratio,
            room_origin_x,
            room_origin_y,
        )
        self.__pos_x, self.__pos_y = window_pos_from_gui_loc(
            self.__pos_x, self.__pos_y, window_object
        )

        if hasattr(window_object, "scale_x"):  # Horizontal window, north or south
            self.sprite = pyglet.sprite.Sprite(
                self.__img,
                self.__pos_x,
                self.__pos_y,
                batch=self.__batch,
                group=self.__group,
            )
            self.sprite.scale_x = window_object.scale_x
        elif hasattr(window_object, "scale_y"):  # Vertical window, east or west
            self.sprite = pyglet.sprite.Sprite(
                self.__img,
                self.__pos_x,
                self.__pos_y,
                batch=self.__batch,
                group=self.__group,
            )
            self.sprite.scale_y = window_object.scale_y
        if (
            window_object.wall == "south" or window_object.wall == "west"
        ):  # problem of perspective in GUI
            self.sprite.rotation = 180

    def delete(self):
        """Delete window sprite (img) from simulation"""
        self.sprite.delete()


# Button widgets
class ButtonWidget(object):
    """Class to represent the GUI Buttons widgets"""

    # from gui.gui_knx import GUIWindow
    def __init__(
        self,
        x: float,
        y: float,
        batch: Batch,
        button_file: str,
        group: OrderedGroup,
        label_text: str = "",
    ) -> None:
        """Initialization of pyglet Button widget object."""
        self.__img = pyglet.image.load(button_file)
        self.__width, self.__length = self.__img.width, self.__img.height
        self.__pos_x, self.__pos_y = x, y
        self.__batch, self.__group = batch, group
        self.sprite = pyglet.sprite.Sprite(
            self.__img,
            self.__pos_x,
            self.__pos_y,
            batch=self.__batch,
            group=self.__group,
        )
        self.label = pyglet.text.Label(
            label_text,
            font_name=gc.FONT_BUTTON,
            font_size=10,
            color=gc.COLOR_FONT_BUTTON,
            x=(self.__pos_x + self.__width // 2),
            y=(self.__pos_y - gc.OFFSET_LABEL_BUTTON),
            anchor_x="center",
            anchor_y="center",
            batch=self.__batch,
            group=self.__group,
        )

    def hit_test(self, x: float, y: float) -> bool:
        """Test if Button widget was hit by the mouse."""
        return self.__pos_x < x < (self.__pos_x + self.__width) and self.__pos_y < y < (
            self.__pos_y + self.__length
        )

    @abstractmethod
    def activate(self, gui_window) -> None:  # gui_window: gui.GUIWindow
        """Method called when the Button is pressed."""
        pass


class ButtonPause(object):
    """Class to represent the GUI Pause Button widget"""

    def __init__(
        self,
        x: float,
        y: float,
        batch: Batch,
        button_pause_file: str,
        button_play_file: str,
        group: OrderedGroup,
    ) -> None:
        """Initialization of the Pause Button widget object."""
        self.pause_file = button_pause_file
        self.play_file = button_play_file
        self.file_to_use = self.pause_file
        self.widget = ButtonWidget(
            x, y, batch, self.file_to_use, group=group, label_text="PLAY/PAUSE"
        )

    def activate(self, gui_window) -> None:  # gui_window: gui.GUIWindow
        gui_window.pause_simulation()
        if gui_window.room.simulation_status:  # Pause button PNG if simulation running
            self.file_to_use = self.pause_file
        elif (
            not gui_window.room.simulation_status
        ):  # Play button PNG if simulation paused
            self.file_to_use = self.play_file
        self.clicked = True

    def update_sprite(self, reload: bool = False) -> None:
        """Change Button sprite when clicked."""
        if reload:
            self.file_to_use = self.pause_file
        self.widget.sprite.image = pyglet.image.load(self.file_to_use)


class ButtonStop(object):
    """Class to represent the GUI Stop Button widget"""

    def __init__(
        self, x: float, y: float, batch: Batch, button_file: str, group: OrderedGroup
    ) -> None:
        """Initialization of the Stop Button widget object."""
        self.stop_file = button_file
        self.widget = ButtonWidget(
            x, y, batch, self.stop_file, group=group, label_text="STOP"
        )

    def activate(
        self, gui_window
    ) -> None:  # gui_window: gui.GUIWindow, gui_window to be compliant with the call from gui_knx.py module
        pyglet.app.exit()


class ButtonReload(object):
    """Class to represent the GUI Reload Button widget"""

    def __init__(
        self, x: float, y: float, batch: Batch, button_file: str, group: OrderedGroup
    ) -> None:
        """Initialization of the Reload Button widget object."""
        self.widget = ButtonWidget(
            x, y, batch, button_file, group=group, label_text="RELOAD"
        )

    def activate(self, gui_window) -> None:  # gui_window: gui.GUIWindow
        gui_window.reload_simulation()


class ButtonSave(object):
    """Class to represent the GUI Save Button widget"""

    def __init__(
        self, x: float, y: float, batch: Batch, button_file: str, group: OrderedGroup
    ) -> None:
        """Initialization of the Save Button widget object."""
        self.widget = ButtonWidget(
            x, y, batch, button_file, group=group, label_text="SAVE"
        )

    def activate(self, gui_window) -> None:  # gui_window: gui.GUIWindow
        saved_config_path = gui_window.SAVED_CONFIG_PATH + datetime.now().strftime(
            "%d%m%Y_%H%M%S"
        )
        with open(saved_config_path, "w") as saved_config_file:
            json.dump(gui_window.system_config_dict, saved_config_file, indent=2)


class ButtonDefault(object):
    """Class to represent the GUI Default Button widget"""

    def __init__(
        self, x: float, y: float, batch: Batch, button_file: str, group: OrderedGroup
    ) -> None:
        """Initialization of the Default Button widget object."""
        self.default_file = button_file
        self.widget = ButtonWidget(
            x, y, batch, self.default_file, group=group, label_text="DEFAULT"
        )

    def activate(self, gui_window) -> None:  # gui_window: gui.GUIWindow
        gui_window.reload_simulation(default_config=True)


# Device widgets
class DeviceWidget(object):
    """Class to represent a GUI Device widget"""

    def __init__(
        self,
        pos_x: float,
        pos_y: float,
        batch: Batch,
        img_file_ON: str,
        img_file_OFF: str,
        group: OrderedGroup,
        device_class: str,
        device_number: str,
        available_device: bool = False,
        img_neutral=None,
    ) -> None:
        """
        Initialization of a Device Widget.
        Object InRoomDevice added to attributes when initializing the system in gui_knx.py
        humiditysoil sensor: initialization of a drop img next to it to show the soil moisture level.
        thermometer: neutral img when temperature stable, red img when rising, blue when decreasing.
        """
        self.device_class = device_class
        self.label_name = self.device_class.lower() + device_number
        self.sprite_state = False
        self.sprite_state_ratio = 100
        self.file_ON = img_file_ON
        self.file_OFF = img_file_OFF
        self.pos_x, self.pos_y = (
            pos_x,
            pos_y,
        )  # Center of the image, simulated position on room
        self.img_ON, self.img_OFF = pyglet.image.load(self.file_ON), pyglet.image.load(
            self.file_OFF
        )
        self.width, self.length = self.img_ON.width, self.img_ON.height
        self.__batch = batch
        self.__group = group
        # Device's sprite displayed on the side of the GUI, to be added manually by the user
        if available_device:
            self.origin_x, self.origin_y = self.pos_x, self.pos_y
            label_color = gc.COLOR_FONT_AVAILABLEDEVICE
        else:  # origin_x and y are bottom left of image
            self.origin_x, self.origin_y = (
                self.pos_x - self.width // 2,
                self.pos_y - self.length // 2,
            )
            label_color = gc.COLOR_FONT_ROOMDEVICE
            # Humidity soil sensor
            if "humiditysoil" in self.label_name:
                # https://www.acurite.com/blog/soil-moisture-guide-for-plants-and-vegetables.html
                self.humiditysoil = 10  # Arbitrary init of soil humidity
                self.__drop_red = pyglet.image.load(gc.DROP_RED_PATH)
                self.__drop_yellow = pyglet.image.load(gc.DROP_YELLOW_PATH)
                self.__drop_green = pyglet.image.load(gc.DROP_GREEN_PATH)
                self.__drop_blue = pyglet.image.load(gc.DROP_BLUE_PATH)
                self.__drop_pos_x = self.pos_x + self.width // 2
                self.__drop_pos_y = self.pos_y
                self.__drop_label_pos_x = self.__drop_pos_x
                self.__drop_label_pos_y = self.pos_y - 1.5 * gc.OFFSET_LABEL_DEVICE
                self.__drop_sprite = pyglet.sprite.Sprite(
                    self.__drop_red,
                    x=self.__drop_pos_x,
                    y=self.__drop_pos_y,
                    batch=self.__batch,
                    group=self.__group,
                )
                self.__drop_label = pyglet.text.Label(
                    "10%",
                    font_name=gc.FONT_INTERACTIVE,
                    font_size=gc.FONT_SIZE_INTERACTIVE,
                    color=color_from_humiditysoil(self.humiditysoil),
                    x=self.__drop_label_pos_x,
                    y=self.__drop_label_pos_y,
                    anchor_x="left",
                    anchor_y="center",
                    batch=self.__batch,
                    group=self.__group,
                )
        # Thermometer
        if img_neutral is not None:
            self._img_neutral = pyglet.image.load(img_neutral)
            self.sprite = pyglet.sprite.Sprite(
                self._img_neutral,
                x=self.origin_x,
                y=self.origin_y,
                batch=self.__batch,
                group=self.__group,
            )
        else:
            self.sprite = pyglet.sprite.Sprite(
                self.img_OFF,
                x=self.origin_x,
                y=self.origin_y,
                batch=self.__batch,
                group=self.__group,
            )
        self.label = pyglet.text.Label(
            self.label_name,
            font_name=gc.FONT_DEVICE,
            font_size=gc.FONT_SIZE_SOILMOISTURE,
            color=label_color,
            x=(self.origin_x + self.width // 2),
            y=(self.origin_y - gc.OFFSET_LABEL_DEVICE),
            anchor_x="center",
            anchor_y="center",
            batch=self.__batch,
            group=self.__group,
        )

    def __eq__(self, device_to_compare) -> bool:  # device_to_compare: DeviceWidget
        """Define equality with another device class instance"""
        return self.label_name == device_to_compare.label_name

    def hit_test(self, x, y) -> bool:
        """Test if Device widget was hit by the mouse."""
        if hasattr(self, "humiditysoil"):
            return (
                self.sprite.x < x < self.sprite.x + self.width
                and self.sprite.y < y < self.sprite.y + self.length
            ) or (
                self.__drop_sprite.x
                < x
                < self.__drop_sprite.x + self.__drop_sprite.width
                and self.__drop_sprite.y
                < y
                < self.__drop_sprite.y + self.__drop_sprite.height
            )
        else:
            return (
                self.sprite.x < x < self.sprite.x + self.width
                and self.sprite.y < y < self.sprite.y + self.length
            )

    def update_position(
        self,
        new_x: float,
        new_y: float,
        loc_x: float = 0,
        loc_y: float = 0,
        update_loc: bool = False,
    ) -> None:
        """Update the GUI position (pixels) of the device widget, and potentially the system location (meters) of the KNX device instance"""
        self.pos_x, self.pos_y = new_x, new_y
        self.origin_x, self.origin_y = (
            self.pos_x - self.width // 2,
            self.pos_y - self.length // 2,
        )
        self.sprite.update(x=self.origin_x, y=self.origin_y)
        self.label.update(
            x=(self.origin_x + self.width // 2),
            y=(self.origin_y - gc.OFFSET_LABEL_DEVICE),
        )
        if "humiditysoil" in self.label_name:
            self.__drop_pos_x = self.pos_x + self.width // 2
            self.__drop_pos_y = self.pos_y
            self.__drop_label_pos_x = self.__drop_pos_x
            self.__drop_label_pos_y = self.pos_y - 1.5 * gc.OFFSET_LABEL_DEVICE
            self.__drop_sprite.update(x=self.__drop_pos_x, y=self.__drop_pos_y)
            self.__drop_label.update(
                x=self.__drop_label_pos_x, y=self.__drop_label_pos_y
            )
        if update_loc:
            self.loc_x, self.loc_y = loc_x, loc_y
            self.in_room_device.update_location(new_x=self.loc_x, new_y=self.loc_y)
            logging.info(
                f"Location of {self.label_name} is updated to {self.loc_x}, {self.loc_y}."
            )

    def delete(self) -> None:
        """Delete the visual representation of the device : sprite and label"""
        self.sprite.delete()
        self.label.delete()
        if "humiditysoil" in self.label_name:
            self.__drop_sprite.delete()
            self.__drop_label.delete()

    def update_drop_sprite(self) -> None:
        """Method specific for humidity soil sensor, update the color of the drop depending on the moisture level"""
        if hasattr(self, "humiditysoil"):
            # https://www.acurite.com/media/magpleasure/mpblog/upload/5/2/523755c20577be6c9f5ee5a27003abf6.jpg
            if self.humiditysoil <= 20.0:
                drop = self.__drop_red
            elif self.humiditysoil <= 40.0:
                drop = self.__drop_yellow
            elif self.humiditysoil <= 60.0:
                drop = self.__drop_green
            else:
                drop = self.__drop_blue
            self.__drop_sprite.delete()
            self.__drop_label.delete()
            self.__drop_sprite = pyglet.sprite.Sprite(
                drop,
                x=self.__drop_pos_x,
                y=self.__drop_pos_y,
                batch=self.__batch,
                group=self.__group,
            )
            self.__drop_label = pyglet.text.Label(
                str(self.humiditysoil) + "%",
                font_name=gc.FONT_INTERACTIVE,
                font_size=gc.FONT_SIZE_INTERACTIVE,
                color=color_from_humiditysoil(self.humiditysoil),
                x=self.__drop_label_pos_x,
                y=self.__drop_label_pos_y,
                anchor_x="left",
                anchor_y="center",
                batch=self.__batch,
                group=self.__group,
            )

    def update_thermometer_sprite(self, rising_temp: bool) -> None:
        """Method specific for thermometer, update the color of the thermomneter if temp is stable, rising or decreasing."""
        if "thermometer" in self.label_name:
            if rising_temp is None and hasattr(self, "_img_neutral"):
                self.sprite.delete()
                self.sprite = pyglet.sprite.Sprite(
                    self._img_neutral,
                    x=self.origin_x,
                    y=self.origin_y,
                    batch=self.__batch,
                    group=self.__group,
                )
            elif rising_temp:
                self.sprite.delete()
                self.sprite = pyglet.sprite.Sprite(
                    self.img_ON,
                    x=self.origin_x,
                    y=self.origin_y,
                    batch=self.__batch,
                    group=self.__group,
                )
            elif rising_temp == False:
                self.sprite.delete()
                self.sprite = pyglet.sprite.Sprite(
                    self.img_OFF,
                    x=self.origin_x,
                    y=self.origin_y,
                    batch=self.__batch,
                    group=self.__group,
                )


class AvailableDevices(object):
    """Class to represent the available devices widget and their GUI box."""

    def __init__(
        self, batch: Batch, group_dev: OrderedGroup, group_box: OrderedGroup
    ) -> None:
        """
        Initialize the devices widget, their positions and the GUI box.
        group_box should be behind group_dev.
        """
        self.devices: List[DeviceWidget] = []

        self.__box_shape = pyglet.shapes.BorderedRectangle(
            gc.WIN_BORDER / 2,
            gc.OFFSET_AVAILABLEDEVICES_LINE3
            - gc.OFFSET_AVAILABLE_DEVICES
            - gc.WIN_BORDER / 2,
            gc.AVAILABLE_DEVICES_BOX_WIDTH,
            gc.AVAILABLE_DEVICES_BOX_LENGTH,
            border=gc.BOX_BORDER,
            color=gc.COLOR_BOX_AVAILABLEDEVICES,
            border_color=gc.COLOR_BOX_AVAILABLEDEVICES_BORDER,
            batch=batch,
            group=group_box,
        )

        # Line 1
        self.led = DeviceWidget(
            gc.WIN_BORDER,
            gc.OFFSET_AVAILABLEDEVICES_LINE1,
            batch,
            gc.DEVICE_LED_ON_PATH,
            gc.DEVICE_LED_OFF_PATH,
            group_dev,
            "LED",
            "",
            available_device=True,
        )
        self.devices.append(self.led)
        next_image_offset_x = (
            self.led.pos_x + self.led.width + gc.OFFSET_AVAILABLE_DEVICES
        )
        self.heater = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE1,
            batch,
            gc.DEVICE_HEATER_ON_PATH,
            gc.DEVICE_HEATER_OFF_PATH,
            group_dev,
            "Heater",
            "",
            available_device=True,
        )
        self.devices.append(self.heater)
        next_image_offset_x = (
            self.heater.pos_x + self.heater.width + gc.OFFSET_AVAILABLE_DEVICES
        )
        self.ac = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE1,
            batch,
            gc.DEVICE_AC_ON_PATH,
            gc.DEVICE_AC_OFF_PATH,
            group_dev,
            "AC",
            "",
            available_device=True,
        )
        self.devices.append(self.ac)
        next_image_offset_x = (
            self.ac.pos_x + self.ac.width + gc.OFFSET_AVAILABLE_DEVICES
        )
        self.switch = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE1,
            batch,
            gc.DEVICE_SWITCH_ON_PATH,
            gc.DEVICE_SWITCH_OFF_PATH,
            group_dev,
            "Switch",
            "",
            available_device=True,
        )
        self.devices.append(self.switch)
        # next_image_offset_x = self.switch.pos_x + self.switch.width + OFFSET_AVAILABLE_DEVICES

        # Line 2
        self.button = DeviceWidget(
            gc.WIN_BORDER,
            gc.OFFSET_AVAILABLEDEVICES_LINE2,
            batch,
            gc.DEVICE_BUTTON_ON_PATH,
            gc.DEVICE_BUTTON_OFF_PATH,
            group_dev,
            "Button",
            "",
            available_device=True,
        )
        self.devices.append(self.button)
        next_image_offset_x = (
            self.button.pos_x + self.button.width + gc.OFFSET_AVAILABLE_DEVICES
        )
        self.dimmer = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE2,
            batch,
            gc.DEVICE_DIMMER_ON_PATH,
            gc.DEVICE_DIMMER_OFF_PATH,
            group_dev,
            "Dimmer",
            "",
            available_device=True,
        )
        self.devices.append(self.dimmer)
        next_image_offset_x = (
            self.dimmer.pos_x + self.dimmer.width + 1.2 * gc.OFFSET_AVAILABLE_DEVICES
        )
        self.presencesensor = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE2,
            batch,
            gc.DEVICE_PRESENCE_ON_PATH,
            gc.DEVICE_PRESENCE_OFF_PATH,
            group_dev,
            "PresenceSensor",
            "",
            available_device=True,
        )
        self.devices.append(self.presencesensor)
        next_image_offset_x = (
            self.presencesensor.pos_x
            + self.presencesensor.width
            + 5 * gc.OFFSET_AVAILABLE_DEVICES
        )
        self.thermometer = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE2 + gc.OFFSET_AVAILABLE_DEVICES,
            batch,
            gc.DEVICE_THERMO_HOT_PATH,
            gc.DEVICE_THERMO_COLD_PATH,
            group_dev,
            "Thermometer",
            "",
            available_device=True,
            img_neutral=gc.DEVICE_THERMO_NEUTRAL_PATH,
        )
        self.devices.append(self.thermometer)
        # next_image_offset_x = self.thermometer.pos_x + self.thermometer.width + 2*OFFSET_AVAILABLE_DEVICES

        # Line 3
        self.brightness = DeviceWidget(
            gc.WIN_BORDER,
            gc.OFFSET_AVAILABLEDEVICES_LINE3,
            batch,
            gc.DEVICE_BRIGHT_SENSOR_PATH,
            gc.DEVICE_BRIGHT_SENSOR_PATH,
            group_dev,
            "Brightness",
            "",
            available_device=True,
        )
        self.devices.append(self.brightness)
        next_image_offset_x = (
            self.brightness.pos_x
            + self.brightness.width
            + 0.1 * gc.OFFSET_AVAILABLE_DEVICES
        )
        self.airsensor = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE3,
            batch,
            gc.DEVICE_AIRSENSOR_PATH,
            gc.DEVICE_AIRSENSOR_PATH,
            group_dev,
            "AirSensor",
            "",
            available_device=True,
        )
        self.devices.append(self.airsensor)
        next_image_offset_x = (
            self.airsensor.pos_x
            + self.airsensor.width
            + 0.4 * gc.OFFSET_AVAILABLE_DEVICES
        )
        self.co2sensor = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE3,
            batch,
            gc.DEVICE_CO2_PATH,
            gc.DEVICE_CO2_PATH,
            group_dev,
            "CO2Sensor",
            "",
            available_device=True,
        )
        self.devices.append(self.co2sensor)
        next_image_offset_x = (
            self.co2sensor.pos_x + self.co2sensor.width + gc.OFFSET_AVAILABLE_DEVICES
        )
        self.humidityair = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE3,
            batch,
            gc.DEVICE_HUMIDITYAIR_PATH,
            gc.DEVICE_HUMIDITYAIR_PATH,
            group_dev,
            "HumidityAir",
            "",
            available_device=True,
        )
        self.devices.append(self.humidityair)
        next_image_offset_x = (
            self.humidityair.pos_x
            + self.humidityair.width
            + 1.85 * gc.OFFSET_AVAILABLE_DEVICES
        )
        self.humiditysoil = DeviceWidget(
            next_image_offset_x,
            gc.OFFSET_AVAILABLEDEVICES_LINE3,
            batch,
            gc.DEVICE_HUMIDITYSOIL_PATH,
            gc.DEVICE_HUMIDITYSOIL_PATH,
            group_dev,
            "HumiditySoil",
            "",
            available_device=True,
        )
        self.devices.append(self.humiditysoil)
        # next_image_offset_x = self.humiditysoil.pos_x + self.humiditysoil.width + OFFSET_AVAILABLE_DEVICES


class DimmerSetterWidget(object):
    """Class to represent the state_ratio in an animation when setting the dimmer value."""

    def __init__(self, room_dimmer_widget: DeviceWidget) -> None:
        """Initialization of the state_ratio label next to the dimmer device room_dimmer_widget."""
        self.room_dimmer_widget = room_dimmer_widget
        self.room_dimmer_widget.sprite.opacity = gc.OPACITY_CLICKED
        self.init_state_ratio = room_dimmer_widget.in_room_device.device.state_ratio
        self.center_x, self.center_y = (
            room_dimmer_widget.pos_x,
            room_dimmer_widget.pos_y,
        )
        self.state_label_x = (
            self.center_x + room_dimmer_widget.width // 2 + gc.OFFSET_DIMMER_RATIO
        )
        self.state_label_y = self.center_y - room_dimmer_widget.length // 2
        self.being_set = False

    def start_setting_dimmer(self, batch: Batch, group: OrderedGroup) -> None:
        """Start the animation of setting the dimmer ratio."""
        self.being_set = True
        self.state_ratio_label = pyglet.text.Label(
            str(self.init_state_ratio),
            font_name=gc.FONT_INTERACTIVE,
            font_size=gc.FONT_SIZE_INTERACTIVE,
            x=(self.state_label_x),
            y=self.state_label_y,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch,
            group=group,
            color=color_from_state_ratio(self.init_state_ratio),
        )

    def update_ratio(self, new_ratio: float) -> None:
        """Update the state_ratio label of the animation next to the dimmer."""
        self.state_ratio = new_ratio
        self.state_ratio_label.text = str(self.state_ratio)
        self.state_ratio_label.color = color_from_state_ratio(self.state_ratio)

    def delete(self) -> None:
        """Delete the state_ratio animation."""
        self.room_dimmer_widget.sprite.opacity = gc.OPACITY_DEFAULT
        if hasattr(self, "state_ratio_label"):
            self.state_ratio_label.delete()


# Room widget
class RoomWidget(object):
    """Class to represent the GUI Room widget."""

    def __init__(
        self,
        width: float,
        length: float,
        batch: Batch,
        group_bg: OrderedGroup,
        group_mg: OrderedGroup,
        label_group: str,
        label: str,
    ) -> None:
        """
        Initialization of the Room widget object.
        width is on x axis, length on y (height on z)
        group_bg (back ground) should be behinf group_mg (middleground)"""
        # Room Box shape coordinates (with border/walls)
        self.__origin_x_shape = (
            gc.WIN_WIDTH - width - gc.WIN_BORDER - 2 * gc.ROOM_BORDER
        )
        self.__origin_y_shape = gc.WIN_BORDER
        # Room widget coordinates
        self.origin_x = gc.WIN_WIDTH - gc.WIN_BORDER - gc.ROOM_BORDER - width
        self.origin_y = gc.WIN_BORDER + gc.ROOM_BORDER
        # Actual dimensions of the room widget, without borders
        self.width = width
        self.length = length
        self.name = label
        self.__img = pyglet.image.load(gc.ROOM_BACKGROUND_PATH)
        self.__batch = batch
        self.__shape = pyglet.shapes.BorderedRectangle(
            self.__origin_x_shape,
            self.__origin_y_shape,
            width + 2 * gc.ROOM_BORDER,
            length + 2 * gc.ROOM_BORDER,
            border=gc.ROOM_BORDER,
            color=gc.COLOR_ROOM,
            border_color=gc.COLOR_ROOM_BORDER,
            batch=self.__batch,
            group=group_bg,
        )
        self.__shape.opacity = gc.OPACITY_ROOM
        self.__sprite = pyglet.sprite.Sprite(
            self.__img, self.origin_x, self.origin_y, batch=self.__batch, group=group_mg
        )
        self.__label = pyglet.text.Label(
            self.name,
            font_name=gc.FONT_SYSTEM_INFO,
            font_size=75,
            x=(self.origin_x + self.width / 2),
            y=(self.origin_y + self.length / 2),
            anchor_x="center",
            anchor_y="center",
            batch=self.__batch,
            group=label_group,
        )
        self.__label.opacity = gc.OPACITY_ROOM_LABEL
        self.__sprite.opacity = gc.OPACITY_ROOM

    def hit_test(self, x: float, y: float) -> bool:
        """Test if Room widget was hit by the mouse."""
        return self.origin_x < x < (
            self.origin_x + self.width
        ) and self.origin_y < y < (self.origin_y + self.length)


class PersonWidget(object):
    """Class to represent a Person widget, for the presence sensor."""

    def __init__(
        self, img_path: str, x: float, y: float, batch: Batch, group: OrderedGroup
    ):
        """Initialize the Person widget object."""
        self.__batch, self.__group = batch, group
        self.__pos_x, self.__pos_y = x, y
        self.__img = pyglet.image.load(img_path)
        self.__width, self.__length = self.__img.width, self.__img.height
        self.__origin_x, self.__origin_y = (
            self.__pos_x - self.__width // 2,
            self.__pos_y - self.__length // 2,
        )
        self.__sprite = pyglet.sprite.Sprite(
            self.__img,
            self.__origin_x,
            self.__origin_y,
            batch=self.__batch,
            group=self.__group,
        )

    def hit_test(self, x: float, y: float) -> bool:
        """Test if Person widget was hit by the mouse."""
        return self.__origin_x < x < (
            self.__origin_x + self.__width
        ) and self.__origin_y < y < (self.__origin_y + self.__length)

    def update_position(self, new_x: float, new_y: float) -> None:
        """Update GUI position (pixels) of the Person Widget."""
        self.__pos_x, self.__pos_y = new_x, new_y
        self.__origin_x, self.__origin_y = (
            self.__pos_x - self.__width // 2,
            self.__pos_y - self.__length // 2,
        )
        self.__sprite.update(x=self.__origin_x, y=self.__origin_y)

    def delete(self) -> None:
        """Delete the Person widget sprite."""
        self.__sprite.delete()


class VacuumWidget(object):
    """CLass to represent the Vacuum cleaner animation"""

    def __init__(
        self, img_path: str, x: float, y: float, batch: Batch, group: OrderedGroup
    ):
        """Initialize the vaccum cleaner widget object"""
        self.__batch, self.__group = batch, group
        self.__pos_x, self.__pos_y = x, y
        self.__img = pyglet.image.load(img_path)
        self.__img.anchor_x = self.__img.width // 2
        self.__img.anchor_y = self.__img.height // 2
        self.__width, self.__length = self.__img.width, self.__img.height
        self.__origin_x, self.__origin_y = (
            self.__pos_x - self.__width // 2,
            self.__pos_y - self.__length // 2,
        )
        self.__sprite = pyglet.sprite.Sprite(
            self.__img,
            self.__origin_x,
            self.__origin_y,
            batch=self.__batch,
            group=self.__group,
        )
        self.__orientation = 0
        self.__step = 0

    def hit_test(self, x: float, y: float) -> bool:
        """Test if Vacuum widget was hit by the mouse."""
        return self.__origin_x < x < (
            self.__origin_x + self.__width
        ) and self.__origin_y < y < (self.__origin_y + self.__length)

    def update_position(self, new_x: float, new_y: float) -> None:
        """Update GUI position (pixels) of the Vacuum Widget."""
        self.__pos_x, self.__pos_y = new_x, new_y
        self.__origin_x, self.__origin_y = (
            self.__pos_x - self.__width // 2,
            self.__pos_y - self.__length // 2,
        )
        self.__sprite.update(x=self.__origin_x, y=self.__origin_y)

    def move(self):
        """Sequence of movements (13 steps in loop) to show off with the vacuum cleaner"""
        if self.__step == 0:
            self.__orientation = 0
            self.__sprite.rotation = 0
            self.__step += 1
        elif self.__step == 1:
            self.__sprite.rotation = self.__orientation - 45
            self.__orientation -= 45
            if self.__orientation == -90:
                self.__step += 1
        elif self.__step == 2:
            self.update_position(self.__pos_x - 30, self.__pos_y)
            if self.__pos_x < 700:
                self.__step += 1
        elif self.__step == 3:
            self.__sprite.rotation = self.__orientation - 45
            self.__orientation -= 45
            if self.__orientation == -180:
                self.__step += 1
        elif self.__step == 4:
            self.update_position(self.__pos_x, self.__pos_y - 30)
            if self.__pos_y < 300:
                self.__step += 1
        elif self.__step == 5:
            self.__sprite.rotation = self.__orientation - 45
            self.__orientation -= 45
            if self.__orientation == -270:
                self.__step += 1
        elif self.__step == 6:
            self.update_position(self.__pos_x + 30, self.__pos_y)
            if self.__pos_x > 980:
                self.__step += 1
        elif self.__step == 7:
            self.__sprite.rotation = self.__orientation - 45
            self.__orientation -= 45
            if self.__orientation == 0 or self.__orientation == -360:
                self.__step += 1
        elif self.__step == 8:
            self.update_position(self.__pos_x, self.__pos_y + 30)
            if self.__pos_y > 450:
                self.__step += 1
        elif self.__step == 9:
            self.__sprite.rotation = self.__orientation + 45
            self.__orientation += 45
            if self.__orientation == 90 or self.__orientation == -270:
                self.__step += 1
        elif self.__step == 10:
            self.update_position(self.__pos_x + 30, self.__pos_y)
            if self.__pos_x > 1350:
                self.__step += 1
        elif self.__step == 11:
            self.__sprite.rotation = self.__orientation - 45
            self.__orientation -= 45
            if self.__orientation == 0 or self.__orientation == -360:
                self.__step += 1
        elif self.__step == 12:
            self.update_position(self.__pos_x, self.__pos_y + 30)
            if self.__pos_y > 625:
                self.__step = 0
        return

    def delete(self) -> None:
        """Delete the Vacuum widget sprite."""
        self.__sprite.delete()


# Useful functions
def gui_pos_to_system_loc(
    pos_x: float,
    pos_y: float,
    width_ratio: float,
    length_ratio: float,
    room_x: float,
    room_y: float,
) -> Tuple[float, float]:
    """Tranlates gui position in pixels to system location in meters."""
    try:
        loc_x = (pos_x - room_x) / width_ratio
        loc_y = (pos_y - room_y) / length_ratio
    except AttributeError:
        logging.warning(
            "The system is not initialized and the room width/length ratios are not defined."
        )
    return loc_x, loc_y


def system_loc_to_gui_pos(
    loc_x: float,
    loc_y: float,
    width_ratio: float,
    length_ratio: float,
    room_x: float,
    room_y: float,
) -> Tuple[float, float]:
    """Tranlates gui position in pixels to system location in meters."""
    try:
        pos_x = int(room_x + width_ratio * loc_x)
        pos_y = int(room_y + length_ratio * loc_y)
    except AttributeError:
        logging.warning(
            "The system is not initialized and the room width/length ratios are not defined."
        )
    return pos_x, pos_y


def window_pos_from_gui_loc(
    pos_x: float, pos_y: float, window_object
) -> Tuple[float, float]:  # window_object : system.Window
    """Move Window widget of an offset ROOM_BORDER/2 in the correct direction to place it in the Room's wall."""
    if window_object.wall == "north":
        return pos_x, pos_y + gc.ROOM_BORDER / 2
    if window_object.wall == "south":
        return pos_x, pos_y - gc.ROOM_BORDER / 2
    if window_object.wall == "east":
        return pos_x + gc.ROOM_BORDER / 2, pos_y
    if window_object.wall == "west":
        return pos_x - gc.ROOM_BORDER / 2, pos_y


def color_from_state_ratio(state_ratio: float) -> Tuple[int, int, int, int]:
    """Return color of state_ratio dimmer animation depending on state_ratio value, state_ratio must be in (0-100)."""
    if 0 <= state_ratio:
        if state_ratio < 25:
            return gc.COLOR_LOW
        elif state_ratio < 50:
            return gc.COLOR_MEDIUM_LOW
        elif state_ratio < 75:
            return gc.COLOR_MEDIUM_HIGH
        elif state_ratio <= 100:
            return gc.COLOR_HIGH


def color_from_humiditysoil(humiditysoil: float) -> Tuple[int, int, int, int]:
    """Return color of drop animation depending on value of soil humidity."""
    if 0 <= humiditysoil:
        if humiditysoil <= 20.0:
            return gc.COLOR_RED
        elif humiditysoil <= 40.0:
            return gc.COLOR_YELLOW
        elif humiditysoil <= 60.0:
            return gc.COLOR_GREEN
        elif humiditysoil <= 100:
            return gc.COLOR_BLUE


def dimmer_ratio_from_mouse_pos(mouse_y: float, dimmer_center_y: float) -> float:
    """Retunr the state_ratio value depending on vertical distance of mouse from dimmer widget when settin the dimmer value>"""
    relative_distance = mouse_y - dimmer_center_y
    if relative_distance >= gc.OFFSET_MAX_DIMMER_RATIO:
        return 100.0
    elif relative_distance <= -gc.OFFSET_MAX_DIMMER_RATIO:
        return 0.0
    else:
        ratio = round(
            100
            * (relative_distance + gc.OFFSET_MAX_DIMMER_RATIO)
            / (2 * gc.OFFSET_MAX_DIMMER_RATIO),
            2,
        )
        return ratio
