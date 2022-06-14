"""
Class definitions for the room of the system and the devices located in it.
InRoomDevice is a wrapper class to indicate device location in the room.
"""

import logging
import numbers
import os
import sys
from typing import List, Dict, Tuple, Union
from datetime import datetime

import world
from devices import Device
from system.system_tools import Location, Window
from tools.check_tools import check_group_address, check_room_config
from .knxbus import KNXBus

from svshi_interface.main import Interface


class InRoomDevice:
    """Wrapper class to represent a device located at a certain location in the room"""

    def __init__(self, device, room, x: float, y: float, z: float) -> None:
        """
        Initialization of the In Room Device object representing a device in the room.

        device : Device or Window
        room : Room
        """
        self.room = room
        self.device = device
        self.name = device.name
        self.location = Location(self.room, x, y, z)

    def __eq__(self, other_device) -> bool:
        """
        Redefiniton of instances comparison (with 'is' keyword),

        other_device : InRoomDevice
        """
        if isinstance(self.device, Window):
            return (
                self.device.name == other_device.device.name
                and self.location.pos == other_device.location.pos
            )
        else:
            return (
                self.device.name == other_device.device.name
                and self.location.pos == other_device.location.pos
                and self.device.individual_addr == other_device.device.individual_addr
            )

    def update_location(
        self, new_x: int = None, new_y: int = None, new_z: int = None
    ) -> None:
        """
        Update physical location of a in room device.
        Keep old location if None is given.
        """
        new_z = self.location.z if new_z is None else new_z
        new_y = self.location.y if new_y is None else new_y
        new_x = self.location.x if new_x is None else new_x
        new_loc = Location(self.room, new_x, new_y, new_z)
        self.location = new_loc

    def get_irdev_info(
        self, attribute: str = None
    ) -> Dict[str, Union[str, float, bool, Tuple[float, float, float]]]:
        """
        Return information about the Room Devic's' states, location and configuration, 
        method called via CLI commmand 'getinfo'.

        attribute is for Script API mode, to get specific device's attributes.
        """
        if attribute is not None:
            if "effective" in attribute:
                try:
                    return round(getattr(self.device, attribute)(), 2)
                except AttributeError:
                    logging.error(
                        f"The device {self.name} has no attribute/method '{attribute}'."
                    )
                    return None
            attr = getattr(self.device, attribute)
            if isinstance(attr, numbers.Number):
                return round(attr, 2)

        ir_device_dict = {
            "room_name": self.room.name,
            "device_name": self.device.name,
            "location": self.location.pos,
        }
        device_dict = self.device.get_dev_info()
        ir_device_dict.update(device_dict)
        return ir_device_dict


class Room:
    """Class to represent a room, containing devices at certain locations connected through a KNX Bus 
    and a physical world representation."""

    def __init__(
        self,
        name: str,
        width: float,
        length: float,
        height: float,
        simulation_speed_factor: float,
        group_address_style: str,
        system_dt: float = 1,
        insulation: str = "average",
        temp_out: float = 20.0,
        hum_out: float = 50.0,
        co2_out: float = 300,
        temp_in: float = 25.0,
        hum_in: float = 35.0,
        co2_in: float = 800,
        date_time: str = "today",
        weather: str = "clear",
        test_mode: bool = False,
        svshi_mode: bool = False,
        telegram_logging: bool = False,
        interface: Interface = None,
    ):
        """
        Initialization of a romm object, central class during a simulation, gathering all simulated elements.
        It contains the World object, teh KNXBus object, and a list of all room devices and windows.

        test_mode : when writing tests, to avoid launching the GUI and doing certain action,
        svshi_mode : if user is running svshi apps, initiate the connection with svshi process,
        telegram_logging : if in svshi mode, indicate to log telegrams in subfloder of logs/ folder,
        interface : if a user reloads the simulation in the GUI, 
        the interface that initiated the connection with svshi is used to avoid stopping the thread.
        """
        self.__test_mode = test_mode
        # Room main attributes
        (
            self.name,
            self.width,
            self.length,
            self.height,
            self.__speed_factor,
            self.__group_address_style,
            self.__insulation,
        ) = check_room_config(
            name,
            width,
            length,
            height,
            simulation_speed_factor,
            group_address_style,
            insulation,
        )
        self.world = world.World(
            self.__speed_factor,
            system_dt,
            date_time,
            weather,
            self.__insulation,
            temp_out,
            hum_out,
            co2_out,
            temp_in,
            hum_in,
            co2_in,
        )  # date_time is simply a string keyword from config file at this point"
        self.knxbus = KNXBus()
        self.devices: List[InRoomDevice] = []
        self.windows: List[InRoomDevice] = []
        self.__system_dt = system_dt
        # Manage paused simulation
        self.simulation_status = True
        self.__paused_tick_counter = 0
        self.__first_update = True
        # SVSHI mode handling
        if telegram_logging:
            tel_logging_path = "./logs/" + datetime.now().strftime("%d-%m-%Y_%H%M%S")
            os.mkdir(tel_logging_path)
            self.telegram_logging_file_path = tel_logging_path + "/telegram_logs.txt"
        self.svshi_mode = svshi_mode
        self.telegram_logging = telegram_logging
        if self.svshi_mode:
            if (
                interface is not None
            ):  # Simulation reloaded, we keep same interface to maintain connection
                self.__interface = interface
                self.__interface.room = self
            else:
                self.__interface = Interface(self, self.telegram_logging)
            from devices.actuators import IPInterface
            from system import IndividualAddress

            if self.__interface is not None:
                self.interface_device = IPInterface(
                    "ipinterface1", IndividualAddress(0, 0, 0), self.__interface
                )

    def __repr__(self):
        return f"Room {self.name}"

    def add_device(
        self, device: Device, x: float, y: float, z: float = 1
    ) -> InRoomDevice:
        """
        Add a device in the Room at a certain location by creating an InRoomDevice object.
        Add the device to the corresponding Ambient object if device is an actuator or sensor.
        Add the knxbus object as attribute to functional module or sensor.

        z=1 by default as we mostly consider 2D simulations.

        return the InRoomDevice object for the GUI part of the project."""
        from devices import (
            FunctionalModule,
            Actuator,
            LightActuator,
            TemperatureActuator,
            Sensor,
            Brightness,
            Thermometer,
            AirSensor,
            HumiditySoil,
            HumidityAir,
            CO2Sensor,
            PresenceSensor,
        )

        in_room_device = InRoomDevice(device, self, x, y, z)
        self.devices.append(in_room_device)
        if isinstance(device, Actuator):
            if isinstance(device, LightActuator):
                self.world.ambient_light.add_source(in_room_device)
            elif isinstance(device, TemperatureActuator):
                self.world.ambient_temperature.add_source(in_room_device)
        elif isinstance(device, Sensor):
            if self.svshi_mode:
                device.connect_to(self.knxbus)
            if isinstance(device, Brightness):
                self.world.ambient_light.add_sensor(in_room_device)
            elif isinstance(device, Thermometer):
                self.world.ambient_temperature.add_sensor(in_room_device)
            elif isinstance(device, HumiditySoil):
                self.world.soil_moisture.add_sensor(in_room_device)
            elif isinstance(device, HumidityAir):
                self.world.ambient_humidity.add_sensor(in_room_device)
            elif isinstance(device, CO2Sensor):
                self.world.ambient_co2.add_sensor(in_room_device)
            elif isinstance(device, AirSensor):
                self.world.ambient_temperature.add_sensor(in_room_device)
                self.world.ambient_humidity.add_sensor(in_room_device)
                self.world.ambient_co2.add_sensor(in_room_device)
            elif isinstance(device, PresenceSensor):
                self.world.presence.add_sensor(in_room_device)
        elif isinstance(device, FunctionalModule):
            device.connect_to(self.knxbus)
        return in_room_device

    def add_window(self, window: Window) -> None:
        """Add a window in the room"""
        x, y, z = window.window_loc[0], window.window_loc[1], window.window_loc[2]
        in_room_device = InRoomDevice(window, self, x, y, z)
        self.windows.append(in_room_device)
        self.world.ambient_light.add_source(in_room_device)

    def attach(self, device: Device, group_address: str) -> bool:
        """
        Assign a device to a group address.

        return boolean for confirmation in GUI code.
        """
        ga = check_group_address(self.__group_address_style, group_address)
        if ga:
            self.knxbus.attach(device, ga)
            if self.svshi_mode:
                self.knxbus.attach(self.interface_device, ga)
            return True
        else:
            return False

    def detach(self, device, group_address: str) -> bool:
        """
        Remove a device from a group address.

        return boolean for confirmation in GUI code.
        """
        ga = check_group_address(self.__group_address_style, group_address)
        if ga:
            self.knxbus.detach(device, ga)
            return True
        else:
            return False

    def update_world(self, interval: float = 1, gui_mode: bool = False) -> None:
        """
        Update the world states and sensors values by calling world.update()

        test_mode : Simply update sensors values.
        gui_mode : update graphical representation of teh room and devices.
        """
        if self.simulation_status:
            if self.__paused_tick_counter > 0:
                logging.info(
                    f"Simulation was paused for {self.__paused_tick_counter * self.__system_dt} seconds."
                )
                self.__paused_tick_counter = 0
            # Update KNX devices' states and World's physical states
            (
                date_time,
                weather,
                time_of_day,
                out_lux,
                brightness_levels,
                temperature_levels,
                rising_temp,
                humidity_levels,
                co2_levels,
                humiditysoil_levels,
                presence_sensors_states,
            ) = self.world.update(self.__first_update)
            self.__first_update = False
            if (
                gui_mode and not self.__test_mode
            ):  # testing with pyglet blocked by gui during github CI
                import gui

                try:  # Update GUI devices' main graphical states and representations
                    gui.update_gui_window(
                        interval,
                        self.gui_window,
                        date_time,
                        self.world.time.simulation_time(str_mode=True),
                        weather,
                        time_of_day,
                        out_lux,
                        self.svshi_mode,
                    )
                except AttributeError as msg:
                    logging.error(
                        f"Cannot update GUI window due to Room/World attributes missing : '{msg}'."
                    )
                except Exception:
                    logging.error(f"Cannot update GUI window: '{sys.exc_info()[0]}'.")
                try:  # Update GUI sensors' graphical states and representations
                    self.gui_window.update_sensors(
                        brightness_levels,
                        temperature_levels,
                        rising_temp,
                        humidity_levels,
                        co2_levels,
                        humiditysoil_levels,
                        presence_sensors_states,
                    )
                except Exception:
                    logging.error(
                        f"Cannot update sensors value on GUI window: '{sys.exc_info()[0]}'."
                    )
        else:  # Simulation on pause
            self.__paused_tick_counter += 1
            print(
                f" Simulation paused for {self.__paused_tick_counter * self.__system_dt} seconds"
                + 30 * " ",
                end="\r",
            )

    def get_interface(self) -> Union[Interface, None]:
        """Return the interface used to set up svshi connection if in svshi mode. 
        Used to store it and reusi it if simulation reloaded."""
        if self.svshi_mode:
            return self.__interface
        else:
            return None

    def get_device_info(
        self, device_name: str, attribute: str = None
    ) -> Union[None, Dict[str, Union[str, float, bool, Tuple[float, float, float]]]]:
        """
        Return information about the Room Devics's' states, location and configuration.
        Method called via CLI commmand 'getinfo', or when storing a particular attribute with acript API 'store.

        attribute is for Script API mode, to get specific device's attributes.
        """
        for ir_device in self.devices:
            if device_name == ir_device.name:
                ir_dev_dict = ir_device.get_irdev_info(attribute=attribute)
                return ir_dev_dict
        logging.warning(
            f" Device's name '{device_name}' not found in list of room '{self.name}'."
        )
        return None

    def get_world_info(
        self, ambient: str = None, str_mode: bool = True
    ) -> Dict[str, str]:
        """Return information about the World physical states, indoor and/or outdoor, 
        room insulation and simulation time.
        Method called via CLI commmand 'getinfo'"""
        return self.world.get_info(ambient, self, str_mode=str_mode)

    def get_bus_info(self) -> Dict[str, Union[str, Dict[str, Dict[str, List[str]]]]]:
        """Return information about the bus, the group address encoding style 
        and the devices assigned to a group address, method called via CLI commmand 'getinfo'"""
        bus_dict = {"group address encoding style": self.__group_address_style}
        bus_dict.update(self.knxbus.get_info())
        return bus_dict

    def get_room_info(self) -> Dict[str, Union[str, List[str]]]:
        """Return information about the room, the insulation and dimensions, 
        and the room devices, method called via CLI commmand 'getinfo'"""
        room_dict = {
            "name": self.name,
            "width/length/height": str(self.width)
            + "x"
            + str(self.length)
            + "x"
            + str(self.height),
            "volume": str(self.width * self.length * self.height) + " m3",
            "insulation": self.__insulation,
            "devices": [],
        }
        for ir_dev in self.devices:
            room_dict["devices"].append(ir_dev.name)
        return room_dict
