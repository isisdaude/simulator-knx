"""
Classes definitions for the simulation of physical world states:
Time, AmbienLight, AmbientTemperature, AmbientHumidity, AmbientCO2, SoilMoisture, Presence, World
"""

import time
import math
import logging
from datetime import timedelta, datetime
from typing import List, Union, Tuple, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from numpy import float32, mean, sign

import tools
from .world_tools import (
    outdoor_light,
    compute_distance,
    compute_distance_from_window,
    INSULATION_TO_TEMPERATURE_FACTOR,
    INSULATION_TO_HUMIDITY_FACTOR,
    INSULATION_TO_CO2_FACTOR,
    SOIL_MOISTURE_MIN,
)


class Time:
    """
    Class to represent time in simulation, manage scheduling of world updates and evolution of the time and date.
    The scheduler methods manage the regular world updates only when GUI is not used, in the latter case, pyglet library manage scheduling.
    """

    def __init__(
        self, simulation_speed_factor: float, system_dt: float, date_time: datetime
    ) -> None:
        """
        Initialization of a time object.
        Real world simulated time = system_dt * simulation_speed_factor seconds (system_dt = 1 by default)
        Actuators are defined with their evolution per hour, this ratio allows to compute their effect on the corresponding ambient during system_dt

        simulation_speed_factor : corresponding simulated time between two world updates
        system_dt : interval in seconds between two world updates
        date_time : current date and time, to kkep track of simulation date.

        update_rule_ratio : fraction of a simulated hour between two system updates = simulated time corresponding to system_dt
        """
        self.speed_factor = simulation_speed_factor
        self.__system_dt = system_dt
        self.__datetime_init = date_time
        self.date_time = date_time
        self.__simtim_tick_counter = 0
        self.update_rule_ratio = (self.__system_dt * self.speed_factor) / 3600

    # Scheduler management, if not in GUI mode
    def scheduler_init(self) -> AsyncIOScheduler:
        """Initialize the asyncio scheduler."""
        self.__scheduler = AsyncIOScheduler()
        return self.__scheduler

    def scheduler_add_job(self, job_function) -> None:
        """Add a job (function) to the scheduler, and define the interval in seconds between two calls (here system_dt)."""
        try:
            self.__update_job = self.__scheduler.add_job(
                job_function, "interval", seconds=self.__system_dt
            )
        except AttributeError:
            logging.warning(
                "The Scheduler is not initialized: update job cannnot be added."
            )

    def scheduler_start(self) -> None:
        """Start the scheduler and initialize the start simulation time."""
        try:
            self.__scheduler.start()
            self.start_time = time.time()
            self._last_tick_time = self.start_time
        except AttributeError:
            logging.warning("The Scheduler is not initialized and cannot be started.")

    # Simulation time management
    def simulation_time(self, str_mode: bool = False) -> Union[str, float, None]:
        """
        Return the current elapsed simulation time since the start of the simulation (or last reload/pause).
        At each update that occur every system_dt, the tick_counter is increased by system_dt,
        and the simulated time is computed by multiplying with the speed_factor (simulated seconds corresponding to one update = system_dt)."""
        try:
            elapsed_time = (self.__simtim_tick_counter) * self.speed_factor
            if str_mode:
                str_elapsed_time = str(timedelta(seconds=round(elapsed_time, 2)))
                return str_elapsed_time
            else:
                return elapsed_time
        except AttributeError:
            logging.warning("The Simulation time is not initialized.")
            return None

    def update_datetime(self) -> datetime:
        """Increment simtime with system_dt=interval between two tick/updates"""
        self.__simtim_tick_counter += self.__system_dt
        self.date_time = self.__datetime_init + timedelta(
            seconds=self.simulation_time(str_mode=False)
        )
        return self.date_time


class AmbientLight:
    """Class to represent Light/Brightness in a simulation, Brightness is location-dependant in the room."""

    def __init__(self, date_time: datetime, weather: str) -> None:
        """
        Initialization of an ambient light object, brightness in luc=lumen/m^2.

        weather : can be 'slear', 'overcast' or 'dark'
        datetime : datetime.datetime object to represent simulation date and time"""
        from system.room import InRoomDevice
        from system.system_tools import Window

        self.__light_sources: List[InRoomDevice] = []
        self.__light_sensors: List[InRoomDevice] = []
        self.__windows: List[Window] = []
        # values fo global brightness, utilization and light loss factor:
        # https://www.fuzionlighting.com.au/technical/room-index, considering light on 3m ceiling
        self.__utilization_factor = 0.52
        self.__light_loss_factor = 0.8
        self.__weather = weather
        self.__lux_out, self.__time_of_day = outdoor_light(date_time, weather)

    def add_source(self, lightsource) -> None:
        """
        Add a light source to the sources list: LED or Window
        If Window, we compute its resulting lumen from its area and outdoor lux.

        lightsource: InRoomDevice
        """
        from system import Window
        from devices import LightActuator

        if isinstance(lightsource.device, Window):
            self.__windows.append(lightsource)
            # Compute window max_lumen from out_lux and window area
            lightsource.device.max_lumen_from_out_lux(self.__lux_out)
        elif isinstance(lightsource.device, LightActuator):
            self.__light_sources.append(lightsource)

    def add_sensor(self, lightsensor) -> None:
        """
        Add a light sensor to the sensors list: Brightness sensor

        lightsensor: InRoomDevice
        """
        self.__light_sensors.append(lightsensor)

    def __lux_from_lightsource(self, source, distance: float) -> float:
        """
        Compute resulting lux at a certain distance of a light source emitting lumens.
        lux = lumen/square meter
        With the beam angle of source, we compute the total sphere surface reached by lumens 
        at a certain distance from source,
        We then take the fraction corresponding to 1 square meter: 
        (effective_lumen * lumen_ratio) / lux_area = lux/m^2 at a certain distance.

        source: InRoomDevice
        """
        if (
            distance <= 0.01
        ):  # source and sensor at same place, sensor gets all the light emitted
            return source.device.effective_lumen()
        lux_area = 1  # 1 m^2
        # Total surface of sphere reached by light around lightsource
        # https://en.wikipedia.org/wiki/Solid_angle
        solid_angle = 4 * math.pi * (math.sin(source.device.beam_angle / 4)) ** 2
        total_beam_cone_surface = solid_angle * distance**2
        # Fraction of lumen reaching a 1m^2 area at a specific distance from source
        lumen_ratio = lux_area / total_beam_cone_surface
        # Lumen reaching the 1m^2 area at distance from source
        effective_lumen = (
            source.device.effective_lumen() * lumen_ratio
        )  # result in lumen [lm]
        return effective_lumen / lux_area  # result in [lm/m^2]

    def __compute_sensor_brightness(self, brightness_sensor) -> float:
        """
        Compute brightness measured by a certain sensor.

        brightness_sensor: InRoomDevice
        """
        from system import Window

        brightness = 0
        for source in self.__light_sources:
            if source.device.state:
                # Compute distance between sensor and source
                distance = compute_distance(source, brightness_sensor)
                print(
                    f"distance {distance} between source {source.name} and sensor {brightness_sensor.name} "
                )
                # Compute the partial brightness (illuminance in lux=[lm/m^2])
                partial_illuminance = self.__lux_from_lightsource(source, distance)
                # We can linearly add lux values
                brightness += partial_illuminance

        for window in self.__windows:
            distance = compute_distance_from_window(window, brightness_sensor)
            partial_illuminance = self.__lux_from_lightsource(window, distance)
            brightness += partial_illuminance
        return brightness

    def update(
        self, date_time: datetime, first_update: bool = False
    ) -> Tuple[List[Tuple[str, float]], str, datetime, float]:
        """
        Update all brightness sensors of the world (the room), called at each World.update()

        first_update : if start of simulation, no update when first called to display initial values on gui window.

        Return new brightness levels and weather/time info for GUI updates.
        """
        if not first_update:
            logging.info("Brightness update...")

            self.__lux_out, self.__time_of_day = outdoor_light(
                date_time, self.__weather
            )
            for window in self.__windows:  # update max_lumen
                window.device.max_lumen_from_out_lux(self.__lux_out)
        brightness_levels = []
        for sensor in self.__light_sensors:  # update light sensors values
            sensor.device.brightness = self.__compute_sensor_brightness(sensor)
            brightness_levels.append((sensor.device.name, sensor.device.brightness))

        return brightness_levels, self.__weather, self.__time_of_day, self.__lux_out

    # API, CLI functions
    def set_weather(self, date_time: datetime, value: str) -> Union[None, int]:
        """
        Set the weather type, called only in Script Mode with API commands.
        Then updates the light emitted by Windows, and light measured by sensors.

        weather should be 'clear', 'overcast' or 'dark'.
        """
        if value not in ["clear", "overcast", "dark"]:
            logging.warning(
                f"The weather value should be in ['clear', 'overcast', 'dark'], but {value} was given."
            )
            return None
        else:
            self.__weather = value
            self.__lux_out, self.__time_of_day = outdoor_light(
                date_time, self.__weather
            )
            for window in self.__windows:  # update max_lumen
                window.device.max_lumen_from_out_lux(self.__lux_out)
            for sensor in self.__light_sensors:  # update light sensors values
                sensor.device.brightness = self.__compute_sensor_brightness(sensor)
            return 1

    def __compute_global_brightness(self, room) -> float:
        """
        Compute global room brightness considering the light received on room's ground from all light sources.
        There is no fraction of lumen as all lumen reach the room's ground,
        we don't consider light getting out through the window.
        https://www.engineeringtoolbox.com/light-level-rooms-d_708.html

        room : Room
        """
        source_lumen = 0
        for source in self.__light_sources:  # InRoomDevice objects
            source_lumen += source.device.effective_lumen()
        for source in self.__windows:  # InRoomDevice objects
            source_lumen += source.device.effective_lumen()
        N = len(self.__light_sources)
        avg_lumen = source_lumen / N
        room_area = room.width * room.length
        UF, LLF = self.__utilization_factor, self.__light_loss_factor
        global_brightness = N * avg_lumen * UF * LLF / room_area
        return global_brightness

    def get_global_brightness(
        self, room=None, str_mode: bool = False, out: bool = False
    ) -> Union[str, float]:
        """
        Return global brightness.
        call __compute_global_brightness if room info are provided through the room argument.
            -> compute global brightness with detailed formula using light sources.
        simply average sensors values if no room is provided
            -> average sensors values from light_sensors list

        room : Room
        """
        if out == True:
            if str_mode:
                bright = str(round(self.__lux_out, 2)) + " lux"
                return bright
            else:
                return self.__lux_out
        if room is None:  # Average of all sensors' brightness
            brightness_levels = []
            for sensor in self.__light_sensors:
                brightness_levels.append(
                    self.__compute_sensor_brightness(sensor)
                )  # We recompute to have the latest value
            bright = mean(brightness_levels) if len(brightness_levels) else 0
        else:  # Use detailed formula to compute global brightness
            bright = self.__compute_global_brightness(room)

        if str_mode:
            bright = str(round(bright, 2)) + " lux"
            return bright
        else:
            return round(bright, 2)


class AmbientTemperature:
    """Class to represent Temperature in a simulation, Temperature is homogeneous in the whole room."""

    def __init__(
        self,
        update_rule_ratio: float,
        temp_out: float,
        temp_in: float,
        room_insulation: str,
    ) -> None:
        """
        Initialization of a ambient temperature object, temperature in °C.

        update_rule_ratio : devices' update rules are per hour, ratio translate it to the system dt interval
        room_insulatipn should be 'perfect', 'good', 'average', or 'bad'
        max_power heater and ac are used to update temperature and model its evolution smoothly (mostly arbitrary)."""
        self.__update_rule_ratio = update_rule_ratio  #
        self.__temperature_in = temp_in
        self.temperature_out = temp_out
        self.__room_insulation = room_insulation
        self.__temp_sources = []
        self.__temp_sensors = []
        self.__max_power_heater = 0
        self.__max_power_ac = 0

    def __repr__(self):
        return f"{self.__temperature_in} °C"

    def __str__(self):
        return f"{self.__temperature_in} °C"

    def add_source(self, tempsource) -> None:
        """
        Add a temperature source to sources list: Heater or AC.

        tempsource: InRoomDevice
        """
        from devices import Heater, AC

        self.__temp_sources.append(tempsource)
        if isinstance(tempsource.device, Heater):
            self.__max_power_heater += tempsource.device.max_power
        elif isinstance(tempsource.device, AC):
            self.__max_power_ac += tempsource.device.max_power
        else:
            logging.warning(
                f"The device {tempsource.name} is not a Heater or a AC, thus cannot be added to temperature sources list."
            )

    def add_sensor(self, tempsensor) -> None:
        """
        Add a temperature sensor to sensors list: Thermometer.

        tempsensor: InRoomDevice
        """
        self.__temp_sensors.append(tempsensor)

    def update(
        self, first_update: bool = False
    ) -> Tuple[List[Tuple[str, float]], bool]:
        """
        Update all temperature sensors of the world (the room), called at each World.update().
        Use the devices' update rule taking into consideration the effective power of each heating device.
        If no temperature sources, indoor temperature tends to outdoor temperature progressively.

        first_update : if start of simulation, no update when first called to display initial values on gui window.

        Return new temperature levels and a rising temp flag for GUI updates.
        """
        from devices import Heater, AC

        previous_temp = self.__temperature_in
        max_temp = 35.0  # arbitrary
        min_temp = 5.0  # arbitrary
        if not first_update:
            logging.info("Temperature update...")
            if not self.__temp_sources:
                self.__temperature_in += (
                    self.temperature_out - self.__temperature_in
                ) * INSULATION_TO_TEMPERATURE_FACTOR[self.__room_insulation]
            else:
                self.total_max_power = self.__max_power_heater + self.__max_power_ac
                for source in self.__temp_sources:  # sources of heat or 'cool'
                    # Temperature update with sources influence
                    if source.device.state:
                        if isinstance(source.device, Heater):
                            source.device.update_rule = (
                                source.device.effective_power() / self.total_max_power
                            )
                            self.__temperature_in += (
                                source.device.update_rule * self.__update_rule_ratio
                            )
                        if isinstance(source.device, AC):
                            source.device.update_rule = (
                                -source.device.effective_power() / self.total_max_power
                            )
                            self.__temperature_in += (
                                source.device.update_rule * self.__update_rule_ratio
                            )  # The ac update rule is <0
                # Temperature update with outdoor temperature and room insulation influence
                self.__temperature_in += (
                    self.temperature_out - self.__temperature_in
                ) * INSULATION_TO_TEMPERATURE_FACTOR[self.__room_insulation]
            self.__temperature_in = max(
                min_temp, min(max_temp, self.__temperature_in)
            )  # temperature should be (min_temp <= t <= max_temp)
        temperature_levels = []
        for sensor in self.__temp_sensors:  # InRoomDevice objects
            sensor.device.temperature = self.__temperature_in
            sensor.device.send_state()
            temperature_levels.append((sensor.name, sensor.device.temperature))
        rising_temp = self.__temperature_in > previous_temp
        if round(self.__temperature_in, 2) == round(previous_temp, 2):
            rising_temp = None
        return temperature_levels, rising_temp

    # CLI, API methods
    def set_temperature(self, location: str, value: float) -> int:
        """
        Set the world indoor and/or outdoor temperature value, called only in Script Mode with API commands.
        Then updates the temperature measured by sensors.

        location should be 'in' or 'out'.
        """
        if location == "in":
            self.__temperature_in = float(value)
            for sensor in self.__temp_sensors:
                sensor.device.temperature = self.__temperature_in
        elif location == "out":
            self.temperature_out = float(value)
        else:
            logging.error(
                f"The location should be 'in' or 'out' when setting temperature, but {location} was given."
            )
            return 0
        return 1

    def get_temperature(self, str_mode: bool = False) -> Union[str, float]:
        """Return the current temperature value, called with CLI 'getinfo' command."""
        if str_mode:
            temp = str(round(self.__temperature_in, 2)) + " °C"
        else:
            temp = round(self.__temperature_in, 2)
        return temp


class AmbientHumidity:
    """Class to represent Relative Air Humidity in a simulation, Humidity is homogeneous in the whole room."""

    def __init__(
        self,
        temp_out: float,
        hum_out: float,
        temp_in: float,
        hum_in: float,
        room_insulation: str,
        update_rule_ratio: float,
    ) -> None:
        """
        Initialization of a ambient humidity object, humidity in %.
        See following links for theoretical info on physical concepts of humidity:
        https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
        https://www.weather.gov/lmk/humidity

        hum_in, hum_out, temp_in, temp_out : arbitrary initialization of temperature and humidity indoor/outdoor values.
        room_insulatipn should be 'perfect', 'good', 'average', or 'bad'
        update_rule_ratio : devices' update rules are per hour, ratio translate it to the system dt interval
        saturation_vapour_pressure in/out: max possible concentration of water in the air at a certain temperature.
        vapor_pressure : actual concentration of water particles in the air at a certain temperature.
        """
        self.__temperature_out = temp_out
        self.__temperature_in = temp_in
        self.humidity_out = hum_out
        self.__humidity_in = hum_in
        self.__room_insulation = room_insulation
        self.__update_rule_ratio = update_rule_ratio
        self.__humidity_sensors: List = []

        self.__saturation_vapour_pressure_out = (
            self.compute_saturation_vapor_pressure_water(self.__temperature_out)
        )
        self.__saturation_vapour_pressure_in = (
            self.compute_saturation_vapor_pressure_water(self.__temperature_in)
        )
        self.__vapor_pressure_in = round(
            self.__saturation_vapour_pressure_in * self.__humidity_in / 100, 8
        )  # Absolut vapor pressure in room
        self.__vapor_pressure_out = round(
            self.__saturation_vapour_pressure_out * self.humidity_out / 100, 8
        )

    def add_sensor(self, humiditysoil) -> None:
        """
        Add humidity sensor to the sensors list : HumidityAir and AirSensor.

        humiditysoil: InRoomDevice
        """
        self.__humidity_sensors.append(humiditysoil)

    def compute_saturation_vapor_pressure_water(
        self, temperature: float
    ) -> Union[float, None]:
        """
        Compute saturation_vapour_pressure of water 
        = max possible concentration of water in the air at a certain temperature.
        https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
        """
        if temperature > 0:
            exp_arg = 34.494 - 4924.99 / (temperature + 237.1)
            num = math.exp(exp_arg)
            denom = math.pow(temperature + 105, 1.57)
            p_sat = num / denom
            return round(p_sat, 8)
        else:
            logging.warning(
                f"Cannot compute saturation vapor pressure because temperature {temperature}<0."
            )
            return None

    def update(
        self, temperature: float, first_update: bool = False
    ) -> List[Tuple[str, float]]:
        """
        Update all humidity sensors of the world (the room), called at each World.update().
        We update the humidity using the vapor pressure and room's insulation:
        room's insulation allows exchanges of air with outside of the room,
        we use it to update the vapor pressur of water in the room,
        we then compute the saturation vapor pressure at current temperature,
        and finally we can compute the relative humidity by taking the percentage ratio between the two.

        first_update : if start of simulation, no update when first called to display initial values on gui window.

        Return humidity levels for GUI updates.
        """
        if not first_update:
            logging.info("Humidity update...")
            # We recompute sat vapor pressure from new temperature
            self.__saturation_vapour_pressure_in = (
                self.compute_saturation_vapor_pressure_water(temperature)
            )
            self.__temperature_in = temperature
            # Apply humidity factor from outside temp and room's insulation
            self.__vapor_pressure_in += (
                (self.__vapor_pressure_out - self.__vapor_pressure_in)
                * INSULATION_TO_HUMIDITY_FACTOR[self.__room_insulation]
                * self.__update_rule_ratio
            )
            self.__humidity_in = (
                100 * self.__vapor_pressure_in / self.__saturation_vapour_pressure_in
            )

        humidity_levels = []
        for sensor in self.__humidity_sensors:
            sensor.device.humidity = round(self.__humidity_in, 2)
            humidity_levels.append((sensor.device.name, sensor.device.humidity))
        return humidity_levels

    # API, CLI methods
    def set_humidity(self, location: str, value: float) -> int:
        """
        Set the world indoor and/or outdoor humidity value, called only in Script Mode with API commands.
        Then updates the humidity measured by sensors.

        location should be 'in' or 'out'.
        """
        if location == "in":
            self.__humidity_in = float(value)
            self.__saturation_vapour_pressure_in = (
                self.compute_saturation_vapor_pressure_water(self.__temperature_in)
            )
            self.__saturation_vapour_pressure_out = (
                self.compute_saturation_vapor_pressure_water(self.__temperature_out)
            )
            self.__vapor_pressure_in = round(
                self.__saturation_vapour_pressure_in * self.__humidity_in / 100, 8
            )
            for sensor in self.__humidity_sensors:
                sensor.device.humidity = round(self.__humidity_in, 2)
        elif location == "out":
            self.humidity_out = float(value)
            self.__saturation_vapour_pressure_out = (
                self.compute_saturation_vapor_pressure_water(self.__temperature_out)
            )
            self.__vapor_pressure_out = round(
                self.__saturation_vapour_pressure_out * self.humidity_out / 100, 8
            )
        else:
            logging.error(
                f"The location should be 'in' or 'out' when setting humidity, but {location} was given."
            )
            return 0
        return 1

    def get_humidity(self, str_mode: bool = False) -> Union[str, float]:
        """Return the current humidity value, called with CLI 'getinfo' command."""
        if str_mode:
            hum = str(round(self.__humidity_in, 2)) + " %"
        else:
            hum = round(self.__humidity_in, 2)
        return hum


class AmbientCO2:
    """
    Class to represent CO2 in a simulation, CO2 is homogeneous in the whole room.
    Typical co2 levels:
    250-400ppm	Normal background concentration in outdoor ambient air
    400-1,000ppm	Concentrations typical of occupied indoor spaces with good air exchange
    1,000-2,000ppm	Complaints of drowsiness and poor air.
    2,000-5,000 ppm	Headaches, sleepiness and stagnant, stale, stuffy air. Poor concentration, loss of attention.
    5,000	Workplace exposure limit (as 8-hour TWA) in most jurisdictions.
    >40,000 ppm	Exposure may lead to serious oxygen deprivation resulting in permanent brain damage, coma, even death.
    """

    def __init__(
        self,
        co2_out: float,
        co2_in: float,
        room_insulation: str,
        update_rule_ratio: float,
    ) -> None:
        """
        Initialization of a ambient co2 object, co2 level in ppm.

        co2_in, co2_out : arbitrary initialization of co2 indoor/outdoor values
        room_insulatipn should be 'perfect', 'good', 'average', or 'bad'
        update_rule_ratio : devices' update rules are per hour, ratio translate it to the system dt interval
        """
        self.__co2_in = co2_in
        self.co2_out = co2_out
        self.__room_insulation = room_insulation
        self.__co2_sensors: List = []
        self.__update_rule_ratio = update_rule_ratio

    def add_sensor(self, co2sensor) -> None:
        """
        Add a co2 sensor in sensors list: CO2Sensor.

        co2sensor: InRoomDevice
        """
        self.__co2_sensors.append(co2sensor)

    def update(self, first_update: bool = False) -> List[Tuple[str, float]]:
        """
        Update all co2 sensors of the world (the room), called at each World.update().
        Arbitrarly update co2 values with room insulation, update_rule_ratio and a specific arbitrary factor.
        Indoor co2 tends toward outdoor co2.

        first_update : if start of simulation, no update when first called to display initial values on gui window.

        Return co2 levels for GUI updates.
        """
        if not first_update:
            logging.info("CO2 update...")
            self.__co2_in += (
                (self.co2_out - self.__co2_in)
                * INSULATION_TO_CO2_FACTOR[self.__room_insulation]
                * self.__update_rule_ratio
            )
        co2_levels = []
        for sensor in self.__co2_sensors:
            sensor.device.co2 = int(self.__co2_in)
            co2_levels.append((sensor.device.name, sensor.device.co2))
        return co2_levels

    # API, CLI
    def set_co2(self, location: str, value: float) -> int:
        """
        Set the world indoor and/or outdoor co2 value, called only in Script Mode with API commands.
        Then updates the co2 levels measured by sensors.

        location should be 'in' or 'out'.
        """
        if location == "in":
            self.__co2_in = float(value)
            for sensor in self.__co2_sensors:
                sensor.device.co2 = int(self.__co2_in)
        elif location == "out":
            self.co2_out = float(value)
        else:
            logging.error(
                f"The location should be 'in' or 'out' when setting CO2, but {location} was given."
            )
            return 0
        return 1

    def get_co2(self, str_mode: bool = False) -> Union[str, float]:
        """Return the current co2 value, called with CLI 'getinfo' command."""
        if str_mode:
            co2 = str(round(self.__co2_in, 2)) + " ppm"
        else:
            co2 = round(self.__co2_in, 2)
        return co2


class SoilMoisture:
    """Class to represent Soil Moisture in a simulation"""

    def __init__(self, update_rule_ratio: float) -> None:
        """
        Initialization of a soil moisture object.
        Soil moisture can be set by a user, and will then decrease linearly and progrssively to SOIL_MOISTURE_MIN=10%.

        update_rule_ratio : devices' update rules are per hour, ratio translate it to the system dt interval
        update_rule_down : update rule per hour
        """
        self.__humiditysoil_sensors = []
        self.__update_rule_ratio = update_rule_ratio
        self.__update_rule_down = (
            -0.5
        )  # -0.5% of soil moisture per hour, limited to SOIL_MOISTURE_MIN

    def add_sensor(self, humiditysoilsensor) -> None:
        """
        Add a soil moisture sensor to sensors list: HumiditySoil.

        humiditysoilsensor: InRoomDevice
        """
        self.__humiditysoil_sensors.append(humiditysoilsensor)

    def update(self, first_update: bool = False) -> List[Tuple[str, float]]:
        """
        Update all soil moisture sensors of the world (the room), called at each World.update().

        first_update : if start of simulation, no update when first called to display initial values on gui window.

        Return soil moisture levels for GUI updates.
        """
        moisture_levels = []
        for sensor in self.__humiditysoil_sensors:
            if not first_update:
                logging.info("Soil Moisture update...")
                if sensor.device.humiditysoil > SOIL_MOISTURE_MIN:
                    moisture_delta = self.__update_rule_down * self.__update_rule_ratio
                    if (
                        sensor.device.humiditysoil + moisture_delta
                    ) < SOIL_MOISTURE_MIN:
                        sensor.device.humiditysoil = SOIL_MOISTURE_MIN
                    else:
                        sensor.device.humiditysoil += moisture_delta
                else:
                    sensor.device.humiditysoil = SOIL_MOISTURE_MIN
            moisture_levels.append(
                (sensor.device.name, round(sensor.device.humiditysoil, 2))
            )
        return moisture_levels


class Presence:
    """Class to represent Presence Detection in a simulation"""

    def __init__(self) -> None:
        """
        Initialization of a world presence object, presence homogeneous in the whole room.

        entities : list of persons present in simulation.
        presence : indicate presence in room, same for all presence sensors.
        """
        self.presence = False
        self.entities = []  # person detectable by presence sensor
        self.__presence_sensors = []

    def add_entity(self, entity: str) -> None:
        """Add an entity (person) in the room, and update presence values."""
        self.entities.append(entity)
        self.presence = True
        self.update()

    def add_sensor(self, presencesensor) -> None:
        """
        Add a presence sensor sensors list.

        presencesensor: InRoomDevice
        """
        self.__presence_sensors.append(presencesensor)

    def remove_entity(self, entity: str) -> None:
        """Remove an entity (person) from the room, and update presence value accordingly."""
        if entity in self.entities:
            self.entities.remove(entity)
            self.presence = True if len(self.entities) else False
            self.update()
        else:
            logging.warning(f"The entity {entity} is not present in the simulation.")

    def update(self) -> List[Tuple[str, float]]:
        """Update all presence sensors of the world (the room), called at each World.update()"""
        presence_sensors_states = []
        for sensor in self.__presence_sensors:
            sensor.device.state = self.presence
            presence_sensors_states.append((sensor.device.name, sensor.device.state))
        return presence_sensors_states

    # API method
    def set_presence(self, value: str) -> Union[None, int]:
        """
        Set the world presence value, called only in Script Mode with API commands.
        Then updates the presence value measured by sensors.
        Simulate the addition of an entity, just by changing the presence world state
        """
        if len(value) <= len("False"):
            if "True" == value.capitalize():
                value_bool = True
            elif "False" == value.capitalize():
                value_bool = False
            else:
                logging.warning(
                    f"The presence value should be in [True, False], but {value} was given."
                )
                return None

            self.presence = value_bool
            for sensor in self.__presence_sensors:
                sensor.device.state = self.presence
            return 1


class World:
    """
    Class to represnt the physical world simulation and evolution in time.
    Time, Temperature, Humidity, CO2, SoilHumidity and Presence.
    """

    def __init__(
        self,
        simulation_speed_factor: float,
        system_dt: float,
        date_time: datetime,
        weather: str,
        room_insulation: str,
        temp_out: float,
        hum_out: float,
        co2_out: float,
        temp_in: float,
        hum_in: float,
        co2_in: float,
    ) -> None:
        """
        Initialization of a world object.

        # Time
        simulation_speed_factor : corresponding simulated time between two world updates
        system_dt : interval in seconds between two world updates
        date_time : current date and time, to keep track of simulation date.
        # Brightness
        weather : 'clear', 'overcast' or 'dark'
        # Temperature, Humidity, CO2
        room_insulation : 'perfect', 'good', 'average' or 'bad'
        """
        # Time
        self.__date_time, self.__weather = tools.check_weather_date(date_time, weather)
        self.time = Time(simulation_speed_factor, system_dt, self.__date_time)
        # Brightness
        self.ambient_light = AmbientLight(self.__date_time, self.__weather)
        # Temperature
        self.__room_insulation = room_insulation
        self.__temp_out, self.__hum_out, self.__co2_out = (
            temp_out,
            hum_out,
            co2_out,
        )  # does not change during simulation
        self.ambient_temperature = AmbientTemperature(
            self.time.update_rule_ratio,
            self.__temp_out,
            temp_in,
            self.__room_insulation,
        )
        # Humidity
        self.ambient_humidity = AmbientHumidity(
            self.__temp_out,
            self.__hum_out,
            temp_in,
            hum_in,
            self.__room_insulation,
            self.time.update_rule_ratio,
        )
        # CO2
        self.ambient_co2 = AmbientCO2(
            self.__co2_out, co2_in, self.__room_insulation, self.time.update_rule_ratio
        )
        # Soil Moisture
        self.soil_moisture = SoilMoisture(self.time.update_rule_ratio)
        # Presence
        self.presence = Presence()

    def update(
        self, first_update: bool
    ) -> Tuple[
        datetime,
        str,
        datetime,
        float,
        List[Tuple[str, float]],
        List[Tuple[str, float]],
        bool,
        List[Tuple[str, float]],
        List[Tuple[str, float]],
        List[Tuple[str, float]],
        List[Tuple[str, bool]],
    ]:
        """
        World states update, call all ambient states updates methods.

        Return world info and states, and ambient levels for GUI updates."""
        if first_update:
            logging.info(
                f"Initial simulation state at {self.time.simulation_time(str_mode=True)}."
            )
            date_time = self.time.date_time
            (
                brightness_levels,
                weather,
                time_of_day,
                out_lux,
            ) = self.ambient_light.update(date_time, first_update=first_update)
            temperature_levels, rising_temp = self.ambient_temperature.update(
                first_update=first_update
            )
            humidity_levels = self.ambient_humidity.update(
                self.ambient_temperature.get_temperature(str_mode=False),
                first_update=first_update,
            )
            co2_levels = self.ambient_co2.update(first_update=first_update)
            humiditysoil_levels = self.soil_moisture.update(first_update=first_update)
            presence_sensors_states = self.presence.update()
        else:
            date_time = self.time.update_datetime()
            logging.info(
                f"Simulation update at {self.time.simulation_time(str_mode=True)}."
            )
            (
                brightness_levels,
                weather,
                time_of_day,
                out_lux,
            ) = self.ambient_light.update(date_time)
            temperature_levels, rising_temp = self.ambient_temperature.update()
            humidity_levels = self.ambient_humidity.update(
                self.ambient_temperature.get_temperature(str_mode=False)
            )
            co2_levels = self.ambient_co2.update()
            humiditysoil_levels = self.soil_moisture.update()
            presence_sensors_states = self.presence.update()
        return (
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
        )

    # API, CLI methods
    def set_ambient_value(
        self, ambient: str, value: Union[str, float]
    ) -> Union[None, int]:
        """
        Set the world states values, called only in Script Mode with API commands.

        ambient : world state to set,
        value : ambient value or presence bool(in str) or weather string.

        Return 1 or None if the value given was appropriate.
        """
        if "temperature" in ambient:
            if ambient == "temperature_in":
                ret = self.ambient_temperature.set_temperature("in", value)
            elif ambient == "temperature_out":
                ret = self.ambient_temperature.set_temperature("out", value)
        elif "humidity" in ambient:
            if ambient == "humidity_in":
                ret = self.ambient_humidity.set_humidity("in", value)
            elif ambient == "humidity_out":
                ret = self.ambient_humidity.set_humidity("out", value)
        elif "co2" in ambient:
            if ambient == "co2_in":
                ret = self.ambient_co2.set_co2("in", value)
            elif ambient == "co2_out":
                ret = self.ambient_co2.set_co2("out", value)
        elif "presence" in ambient:
            ret = self.presence.set_presence(value)
        elif "weather" in ambient:
            ret = self.ambient_light.set_weather(self.time.date_time, value)
            if ret is not None:
                self.__weather = value
        else:
            ret = None
        return ret  # None or 1

    def get_info(self, ambient: str, room, str_mode: bool) -> Dict[str, str]:
        """Return the current world states values, called with CLI 'getinfo' command."""
        basic_dict_out = {
            "room_insulation": self.__room_insulation,
            "temperature_out": str(self.__temp_out) + " °C",
            "humidity_out": str(self.__hum_out) + " %",
            "co2_out": str(self.__co2_out) + " ppm",
            "brightness_out": self.ambient_light.get_global_brightness(
                room, str_mode=str_mode, out=True
            ),
        }
        basic_dict = {"simtime": self.time.simulation_time(str_mode=str_mode)}
        if "temperature" == ambient:
            basic_dict.update(
                {
                    "temperature_in": self.ambient_temperature.get_temperature(
                        str_mode=str_mode
                    )
                }
            )
            basic_dict.update({"temperature_out": basic_dict_out["temperature_out"]})
            return basic_dict
        elif "humidity" == ambient:
            basic_dict.update(
                {"humidity_in": self.ambient_humidity.get_humidity(str_mode=str_mode)}
            )
            basic_dict.update({"humidity_out": basic_dict_out["humidity_out"]})
            return basic_dict
        elif "co2" in ambient:  # just in case co2 is given
            basic_dict.update({"co2_in": self.ambient_co2.get_co2(str_mode=str_mode)})
            basic_dict.update({"co2_out": basic_dict_out["co2_out"]})
            return basic_dict
        elif "brightness" == ambient:
            basic_dict.update(
                {
                    "brightness_in": self.ambient_light.get_global_brightness(
                        room, str_mode=str_mode
                    ),
                    "brightness_out": self.ambient_light.get_global_brightness(
                        room, str_mode=str_mode, out=True
                    ),
                }
            )  # NOTE room can be None, average of bright sensors is then computed
            return basic_dict
        elif "time" in ambient:  # can be simtime
            basic_dict.update({"speed_factor": self.time.speed_factor})
            return basic_dict
        elif "weather" == ambient:
            basic_dict.update({"weather": self.__weather})
            return basic_dict
        elif "out" == ambient:
            basic_dict.update(basic_dict_out)
            return basic_dict
        elif "all" == ambient:
            ambient_dict = {
                "temperature_in": self.ambient_temperature.get_temperature(
                    str_mode=str_mode
                ),
                "humidity_in": self.ambient_humidity.get_humidity(str_mode=str_mode),
                "co2_in": self.ambient_co2.get_co2(str_mode=str_mode),
                "brightness_in": self.ambient_light.get_global_brightness(
                    room, str_mode=str_mode
                ),
            }
            basic_dict.update(ambient_dict)
            basic_dict.update(basic_dict_out)
            return basic_dict
