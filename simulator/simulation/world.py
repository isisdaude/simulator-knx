"""
Some class definitions for the simulation of the physical world
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]

from typing import List
import time, math, schedule
import sys, logging
from datetime import timedelta, datetime
from numpy import mean

#from soupsieve import escape
# sys.path.append("..") # Adds higher directory to python modules path, for relative includes
# sys.path.append("core")
#
# from devices import *
import system

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Time:
    '''Class that implements time by handling events that should be executed at regular intervals'''

    def __init__(self, simulation_speed_factor:float, system_dt, date_time):
        # Real world simulated time = system_dt * simulation_speed_factor seconds (system_dt = 1 for now)
        self.speed_factor = simulation_speed_factor
        self.__system_dt = system_dt
        self.__datetime_init = date_time
        self.__date_time = date_time
        self.__simtim_tick_counter = 0
        # ratio for physical state update, pro rata per hour
        self.update_rule_ratio = (self.__system_dt * self.speed_factor)/3600


    # Scheduler management, if not in GUI mode
    def scheduler_init(self):
        self.__scheduler = AsyncIOScheduler()
        return self.__scheduler

    def scheduler_add_job(self, job_function):
        try:
            self.__update_job = self.__scheduler.add_job(job_function, 'interval', seconds = self.__system_dt)
        except AttributeError:
            logging.warning("The Scheduler is not initialized: update job cannnot be added")

    def scheduler_start(self):
        try:
            self.__scheduler.start()
            self.start_time = time.time()
            self._last_tick_time = self.start_time
        except AttributeError:
            logging.warning("The Scheduler is not initialized and cannot be started")

    # Simulation time management  ##TODO increment a counter every tick (system_dt) and compute correspondign timedelta wit hspeed factor, do not consider time() function 
    def simulation_time(self, str_mode=False):
        try:
            # if hasattr(self, 'pause_time'): # if system was paused, we consider only the active simulation time 
            #     elapsed_time = (self.pause_time - self.start_time)*self.speed_factor
            #     print(f"elapsed time when paused: {elapsed_time}")
            # else:
            # Elapsed time from simulation point-of-view (not real seconds but simulated seconds)
            elapsed_time = (self.__simtim_tick_counter)*self.speed_factor
            # print(f"elapsed_time system : {self.__simtim_tick_counter}, simulation : {elapsed_time}")
            # elapsed_time = (time.time() - self.start_time)*self.speed_factor
            if str_mode:
                str_elapsed_time = str(timedelta(seconds=round(elapsed_time, 2)))#[:-5]
                # print(f"str_simtime : {str_elapsed_time}")
                return str_elapsed_time
            else:
                return elapsed_time # in seconds
        except AttributeError:
            logging.warning("The Simulation time is not initialized")
    
    def update_datetime(self):
        # if not hasattr(self, "_last_tick_time"):
        #     self._last_tick_time = time.time()
        # else:
        #     print(f"time since last tick : {time.time() - self._last_tick_time}")
        #     self._last_tick_time = time.time()
        self.__simtim_tick_counter += self.__system_dt # Increment simtime with system_dt=interval between two tick/updates
        self.__date_time = self.__datetime_init + timedelta(seconds = self.simulation_time(str_mode=False)) # current date time, timedelta from simulation start, elapsed time is the simulated seconds elapsed (real seconds not system's)
        print(self.__date_time.strftime("%Y-%m-%d %H:%M:%S"))
        return self.__date_time


class AmbientTemperature:
    '''Class that implements temperature in a system'''

    def __init__(self, room_volume, update_rule_ratio, temp_out:float, temp_in:float, room_insulation):
        # self.simulation_speed_factor = simulation_speed_factor
        # self.simulated_dt = system_dt * simulation_speed_factor # e.g., update called every 1*180seconds = 3min
        self.__update_rule_ratio = update_rule_ratio # update rules are per hour, ratio translate it to the system dt
        self.__temperature_in = temp_in 
        self.temperature_out = temp_out
        self.__room_insulation = room_insulation
        # self.__room_volume = room_volume
        """Describes room volume in m3"""
        self.__temp_sources = []
        """List of temperature actuators sources in the room"""
        self.__temp_sensors = []
        """List of temperature sensors in the room"""
        self.__temp_controllers = []

        self.__max_power_heater = 0
        self.__max_power_ac = 0

    def add_source(self, tempsource): # Heatsource is an object that heats the room
        """ tempsource: InRoomDevice """
        from devices import Heater, AC
        self.__temp_sources.append(tempsource) #add check on source
        if isinstance(tempsource.device, Heater):
            self.__max_power_heater += tempsource.device.max_power
        if isinstance(tempsource.device, AC):
            self.__max_power_ac += tempsource.device.max_power

    def add_sensor(self, tempsensor): 
        """ tempsensor: InRoomDevice """
        self.__temp_sensors.append(tempsensor) #add check on sensor

    # def add_temp_controllers(self, temp_controllers):
    #     self.__temp_controllers.append(temp_controllers) #add check on sensor
    
    # def watts_to_temp(self, watts):
    #     return ((watts - 70)*2)/7 + 18

    # def max_temperature_in_room(self, volume, max_power, insulation_state='good'):
    #     """Maximum reachable temperature in the specified room with the current enabled heaters, with exterior temperature being 20C"""
    #     from system import INSULATION_TO_CORRECTION_FACTOR
    #     watts = max_power/((1+INSULATION_TO_CORRECTION_FACTOR[self.__room_insulation])*volume)
    #     return self.watts_to_temp(watts)

    def update(self):
        from devices import Heater, AC
        from system import INSULATION_TO_TEMPERATURE_FACTOR
        '''Apply the update rules taking into consideration the maximum power of each heating device, if none then go back progressively to default outside temperature'''
        logging.info("Temperature update")
        previous_temp = self.__temperature_in
        if(not self.__temp_sources):
            self.__temperature_in += (self.temperature_out - self.__temperature_in) * INSULATION_TO_TEMPERATURE_FACTOR[self.__room_insulation] 
        else:
            self.total_max_power = self.__max_power_heater + self.__max_power_ac
            #### actual power would allow to compute concrete max temp
            # self.total_actual_power = 0
            # for source in self.__temp_sources:
            #     if source.device.status and source.device.state:
            #         self.total_actual_power += source.device.effective_power
            for source in self.__temp_sources: # sources of heat or cold
                if source.device.status and source.device.state: # if source enabled
                    if isinstance(source.device, Heater):
                        source.device.update_rule = source.device.effective_power/self.total_max_power 
                        self.__temperature_in += source.device.update_rule*self.__update_rule_ratio
                    if isinstance(source.device, AC):
                        source.device.update_rule = - source.device.effective_power/self.total_max_power
                        self.__temperature_in += source.device.update_rule*self.__update_rule_ratio # The ac update rule is <0
            # Compute max temp
            #relative_max_power = self.__max_power_heater - self.__max_power_ac
            # Apply temp factor from outside temp and insulation
            self.__temperature_in += (self.temperature_out - self.__temperature_in) * INSULATION_TO_TEMPERATURE_FACTOR[self.__room_insulation]
            #TODO: compute max and min temp!!!
            max_temp = 30.0 #self.max_temperature_in_room(self.__room_volume, self.__max_power_heater, "good") ##mean(max_temps)
            min_temp = 10.0
            self.__temperature_in = max(min_temp, min(max_temp, self.__temperature_in)) # temperature cannot exceed max temp and be less than min_temp
            # print(f"system temp= {round(self.temperature, 2)}")
            # self.temperature = max(min_temp, self.temperature)
                # self.temperature = (self.temperature + max_temp) // 2 # Decreases by the average of temp and outside_temp, is a softer slope
        temperature_levels = []
        for sensor in self.__temp_sensors: # temp sensors are in room devices
            # print(f"sensor {sensor.device.name} temp= {round(self.temperature, 2)}")
            sensor.device.temperature = self.__temperature_in
            temperature_levels.append((sensor.name, sensor.device.temperature))
        # for controller in self.__temp_controllers:#
        #     controller.temperature = self.temperature ##TODO: notify the bus with a telegram to heat sources
        rising_temp = self.__temperature_in > previous_temp
        if round(self.__temperature_in,2) == round(previous_temp,2):
            rising_temp = None
        return temperature_levels, rising_temp

    def __repr__(self):
        return f"{self.__temperature_in} °C"

    def __str__(self):
        return f"{self.__temperature_in} °C"
    
    def get_temperature(self, str_mode=False):
        if str_mode:
            temp = str(round(self.__temperature_in, 2)) + " °C"
        else:
            temp = self.__temperature_in
        return temp


class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self, date_time, weather):
        self.__light_sources: List = []
        self.__light_sensors: List = [] # inroom devices
        self.__windows: List = []
        # values fo global brightness # https://www.fuzionlighting.com.au/technical/room-index, considering light on 3m ceiling 
        self.__utilization_factor = 0.52 
        self.__light_loss_factor = 0.8  # TODO magic number 
        self.__weather = weather
        self.__lux_out, self.__time_of_day = system.outdoor_light(date_time, weather)

    def add_source(self, lightsource): 
        """ lightsource: InRoomDevice """
        self.__light_sources.append(lightsource) 
        if isinstance(lightsource.device, system.Window):
            # print(f"window {lightsource.device.name} is added to light sources")
            self.__windows.append(lightsource)
            # Compute window lumen from out_lux and window area
            lightsource.device.max_lumen_from_out_lux(self.__lux_out)

    def add_sensor(self, lightsensor):
        """ lightsensor: InRoomDevice """
        self.__light_sensors.append(lightsensor)

    
    def __lux_from_lightsource(self, source, distance):
        """ source: InRoomDevice """
        lux_area = 1 # Lux consider lumen per square meter (1 m^2)
        # Total surface of sphere reached by light around lightsource
        # https://en.wikipedia.org/wiki/Solid_angle and 
        solid_angle = 4 * math.pi * (math.sin(source.device.beam_angle/4))**2
        total_beam_cone_surface = solid_angle * distance**2
        # Fraction of lumen reaching a 1m^2 area at a specific distance from source
        lumen_ratio = lux_area / total_beam_cone_surface
        # Lumen reaching the 1m^2 area at distance from source
        resulting_lumen = source.device.effective_lumen() * lumen_ratio # result in lumen [lm]
        return resulting_lumen / lux_area # result in [lm/m^2]
        

    def __compute_sensor_brightness(self, brightness_sensor): # Read brightness at a particular sensor
        """ brightness_sensor: InRoomDevice """
        brightness = 0
        for source in self.__light_sources:
            # If the light is on and enabled on the bus
            if isinstance(source.device, system.Window):
                # Compute closest distance between sensor and windows
                distance = system.compute_distance_from_window(source, brightness_sensor)
                # print(f"sensor {brightness_sensor.name} is at {distance} from window {source.name}")
            elif (source.device.is_enabled() and source.device.state):
                # print(f"{source.device.name} is a light source")
                # Compute distance between sensor and each source
                distance = system.compute_distance(source, brightness_sensor)  
            # Compute the new brightness (illuminance in lux=[lm/m^2])
            partial_illuminance = self.__lux_from_lightsource(source, distance)
            # We can linearly add lux values
            brightness += partial_illuminance
        
        return brightness
    
    def update(self, date_time): # Updates all brightness sensors of the world (the room)
        logging.info("Brightness update")
        brightness_levels = []
        self.__lux_out, self.__time_of_day = system.outdoor_light(date_time, self.__weather)
        for window in self.__windows: # update max_lumen
            window.device.max_lumen_from_out_lux(self.__lux_out)
        ## TODO window and blinds with out_lux
        for sensor in self.__light_sensors:
            # Update the sensor's brightness
            sensor.device.brightness = self.__compute_sensor_brightness(sensor) # set the newly calculated sensor brightness
            brightness_levels.append((sensor.device.name, sensor.device.brightness))

        return brightness_levels, self.__weather, self.__time_of_day, self.__lux_out

    # API functions    
    def __compute_global_brightness(self, room):
        # There is no fraction of lumen as all lumen reach the room's ground
        # We don't consider light getting out through the window
        # https://www.engineeringtoolbox.com/light-level-rooms-d_708.html
        source_lumen = 0
        for source in self.__light_sources: # InRoomDevice
            source_lumen += source.device.effective_lumen()
        N = len(self.__light_sources)
        avg_lumen = source_lumen / N
        room_area = room.width * room.length
        UF, LLF = self.__utilization_factor, self.__light_loss_factor
        global_brightness = N * avg_lumen * UF * LLF / room_area
        return global_brightness


    def get_global_brightness(self, room = None, str_mode=False):
        if room is None: # simply make an average of all sensors' brightness
            brightness_levels = []
            for sensor in self.__light_sensors:
                brightness_levels.append(self.__compute_sensor_brightness(sensor)) # We recompute to have the latest value
            bright = mean(brightness_levels) if len(brightness_levels) else 0
        else:
            bright = self.__compute_global_brightness(room)
        
        if str_mode:
            bright = str(round(bright, 2)) + " lux"
            return bright
        else:
            return bright




class AmbientHumidity:
    """ Class for relative humidity in a room (relative compared to max humidity or vapour pressure"""
    # elements that influence humidity:
    # - windows
    # - heater/cooler
    # - insulation
    def __init__(self, temp_out, hum_out, temp_in, hum_in, room_insulation, update_rule_ratio):
        self.__temperature_out = temp_out ## NOTE maybe useless as we use it once in init
        self.__temperature_in = temp_in
        self.humidity_out = hum_out
        self.__humidity_in = hum_in # default initial Relative Humidity in %, same in the whole room
        self.saturation_vapour_pressure_out = self.compute_saturation_vapor_pressure_water(self.__temperature_out )
        self.__room_insulation = room_insulation
        self.__humidity_sources: List = []
        self.__humidity_sensors: List = []
        # https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
        # https://www.weather.gov/lmk/humidity
        self.__saturation_vapour_pressure_in = self.compute_saturation_vapor_pressure_water(self.__temperature_in)
        
        self.__vapor_pressure = round(self.__saturation_vapour_pressure_in * self.__humidity_in/100, 8) # Absolut vapor pressure in room
        self.__update_rule_ratio = update_rule_ratio

    
    def add_source(self, humiditysource):
        """ humiditysource: InRoomDevice """
        self.__humidity_sources.append(humiditysource)
    def add_sensor(self, humiditysoil):
        """ humiditysoil: InRoomDevice """
        self.__humidity_sensors.append(humiditysoil)
    
    def compute_saturation_vapor_pressure_water(self, temperature):
        if temperature > 0:
            exp_arg = 34.494 - 4924.99 / (temperature + 237.1)
            num = math.exp(exp_arg)
            denom = math.pow(temperature+105, 1.57)
            p_sat = num / denom
            return round(p_sat, 8)
        else:
            logging.warning(f"Cannot compute saturation vapor pressure because temperature {temperature}<0")
            return None

    # def read_humidity(self, humidity_sensor):

    def update(self, temperature):
        from system import INSULATION_TO_HUMIDITY_FACTOR
        logging.info("Humidity update")
        # We recompute sat vapor pressure from new temp
        self.__saturation_vapour_pressure_in = self.compute_saturation_vapor_pressure_water(temperature)
        self.__temperature_in = temperature

        self.__humidity_in = 100 * self.__vapor_pressure / self.__saturation_vapour_pressure_in # Compute the new humidity after a temperature change (no open windows considered)
        # Apply humidity factor from outside temp and insulation
        self.__humidity_in += (self.humidity_out - self.__humidity_in) * INSULATION_TO_HUMIDITY_FACTOR[self.__room_insulation] * self.__update_rule_ratio
        # We recompute vapor pressure from new hum
        self.__vapor_pressure = self.__saturation_vapour_pressure_in * self.__humidity_in/100
        ### TODO: add condition if window open
        # if window open:
        #   new_humidity = hum+2hum_out /3 => drastic change in humidity when we open the window
        humidity_levels = []
        for sensor in self.__humidity_sensors:
            sensor.device.humidity = round(self.__humidity_in, 2)
            humidity_levels.append((sensor.device.name, sensor.device.humidity))
        return humidity_levels

    def get_humidity(self, str_mode=False):
        if str_mode:
            hum = str(round(self.__humidity_in, 2)) + " %"
        else:
            hum = self.__humidity_in
        return hum



class AmbientCO2:
    # elements that influence humidity:
    # - windows

    # 250-400ppm	Normal background concentration in outdoor ambient air
    # 400-1,000ppm	Concentrations typical of occupied indoor spaces with good air exchange
    # 1,000-2,000ppm	Complaints of drowsiness and poor air.
    # 2,000-5,000 ppm	Headaches, sleepiness and stagnant, stale, stuffy air. Poor concentration, loss of attention, increased heart rate and slight nausea may also be present.
    # 5,000	Workplace exposure limit (as 8-hour TWA) in most jurisdictions.
    # >40,000 ppm	Exposure may lead to serious oxygen deprivation resulting in permanent brain damage, coma, even death.

    def __init__(self, co2_out, co2_in, room_insulation, update_rule_ratio):
        self.__co2_in = co2_in # ppm
        self.co2_out = co2_out
        self.__room_insulation = room_insulation
        self.__co2_sensors: List = []
        self.__update_rule_ratio = update_rule_ratio
    
    def add_sensor(self, co2sensor):
        """ co2sensor: InRoomDevice """
        self.__co2_sensors.append(co2sensor)
    
    def update(self, temperature, humidity):  ### TODO remove temp et humif not used
        from system import INSULATION_TO_CO2_FACTOR
        logging.info("CO2 update")
        # self.__co2_in = compute_co2level(temperature, humidity) # totally wrong values...
        ## TODO : change CO2 if window opened, co2 rise until window is opened
        ## TODO: check of presence 
        # Apply humidity factor from outside temp and insulation
        self.__co2_in += (self.co2_out - self.__co2_in) * INSULATION_TO_CO2_FACTOR[self.__room_insulation] * self.__update_rule_ratio
        co2_levels = []
        for sensor in self.__co2_sensors:
            sensor.device.co2level = int(self.__co2_in)
            co2_levels.append((sensor.device.name, sensor.device.co2level))
        return co2_levels
    
    def get_co2level(self, str_mode=False):
        if str_mode:
            co2 = str(round(self.__co2_in, 2)) + " ppm"
        else:
            co2 = self.__co2_in
        return co2


class SoilMoisture:
    def __init__(self, update_rule_ratio):
        self.__humiditysoil_sensors = []
        self.__update_rule_ratio = update_rule_ratio
        self.__update_rule_down = -0.5 # -0.5% of soil moisture per hour, limited to ambient humidity
        self.__update_rule_up = 0.1 # if lower than humidity in, the moisture increase very slowly
    
    def add_sensor(self, humiditysoilsensor):
        """ humiditysoilsensor: InRoomDevice """
        self.__humiditysoil_sensors.append(humiditysoilsensor)

    def update(self, humidity_in):
        logging.info("Soil Moisture update")
        moisture_levels = []
        for sensor in self.__humiditysoil_sensors:
            if sensor.device.humiditysoil > humidity_in:
                moisture_delta = self.__update_rule_down * self.__update_rule_ratio 
                if (sensor.device.humiditysoil+moisture_delta) < humidity_in: 
                    sensor.device.humiditysoil = humidity_in
            elif sensor.device.humiditysoil <= humidity_in:
                moisture_delta = self.__update_rule_up * self.__update_rule_ratio 
                if (sensor.device.humiditysoil+moisture_delta) > humidity_in: 
                    sensor.device.humiditysoil = humidity_in
            if sensor.device.humiditysoil != humidity_in:
                sensor.device.humiditysoil += moisture_delta
            moisture_levels.append((sensor.device.name, round(sensor.device.humiditysoil,2)))
        return moisture_levels


class Presence:
    def __init__(self):
        self.presence = False
        self.entities = [] # person or object detectable by presence sensor
        self.presence_sensors = []
    
    def add_entity(self, entity:str):
        self.entities.append(entity)
        self.presence = True
        self.update()
    def add_sensor(self, presencesensor):
        """ presencesensor: InRoomDevice """
        self.presence_sensors.append(presencesensor)

    def remove_entity(self, entity:str):
        if entity in self.entities:
            self.entities.remove(entity)
            self.presence = True if len(self.entities) else False
            self.update()
        else:
            logging.warning(f"The entity {entity} is not present in the simulation.")
    
    # def remove_sensor(self, presencesensor): ## TODO, device removal
    #     """ presencesensor: InRoomDevice """
    #     if presencesensor in self.presence_sensors:
    #         self.presence_sensors.remove(presencesensor)
    
    def update(self):
        presence_sensors_states = []
        for sensor in self.presence_sensors:
            sensor.device.state = self.presence
            presence_sensors_states.append((sensor.device.name, sensor.device.state))
        return presence_sensors_states
    
    ## TODO: implement set for world states
    # def set_presence(self):
        # self.presence = True


class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''
    ## INITIALISATION ##
    def __init__(self, room_width, room_length, room_height, simulation_speed_factor, system_dt, room_insulation, temp_out, hum_out, co2_out, temp_in, hum_in, co2_in, date_time, weather): #date_time is simply a string keyword from config file at this point
        self.__date_time, self.__weather = system.check_wheater_date(date_time, weather) # self.__date_time is a datetime.datetime instance, self.__weather is a string
        self.time = Time(simulation_speed_factor, system_dt, self.__date_time) # simulation_speed_factor=240 -> 1h of simulated time = 1min of simulation
        self.__room_insulation = room_insulation
        self.__temp_out, self.__hum_out, self.__co2_out = temp_out, hum_out, co2_out # does not change during simulation
        # self.speed_factor = simulation_speed_factor
        self.ambient_temperature = AmbientTemperature(room_width*room_height*room_length, self.time.update_rule_ratio, self.__temp_out, temp_in, room_insulation)
        self.ambient_light = AmbientLight(self.__date_time, self.__weather) #TODO: set a default brightness depending on the time of day (day/night), blinds state (open/closed), and wheather state(sunny, cloudy,...)
        self.ambient_humidity = AmbientHumidity(self.__temp_out, self.__hum_out, temp_in, hum_in,  self.__room_insulation, self.time.update_rule_ratio)
        self.ambient_co2 = AmbientCO2(self.__co2_out, co2_in, self.__room_insulation, self.time.update_rule_ratio)
        self.soil_moisture = SoilMoisture(self.time.update_rule_ratio)
        self.presence = Presence()
        # self.ambient_world = [self.ambient_temperature, self.ambient_light, self.ambient_humidity, self.ambient_co2, self.soil_moisture]

    def update(self):
        # co2 and humidity update need temperature update to be done before
        date_time = self.time.update_datetime()
        brightness_levels, weather, time_of_day, out_lux = self.ambient_light.update(date_time)
        temperature_levels, rising_temp = self.ambient_temperature.update()
        humidity_levels = self.ambient_humidity.update(self.ambient_temperature.get_temperature(str_mode=False))
        co2_levels = self.ambient_co2.update(self.ambient_temperature.get_temperature(str_mode=False), self.ambient_humidity.get_humidity(str_mode=False))
        humiditysoil_levels = self.soil_moisture.update(self.ambient_humidity.get_humidity(str_mode=False))
        presence_sensors_states = self.presence.update()
        # humidity_levels = self.ambient_humidity.update()
        return date_time, weather, time_of_day, out_lux, brightness_levels, temperature_levels, rising_temp, humidity_levels, co2_levels, humiditysoil_levels, presence_sensors_states

    def get_world_state(self): # one world per room, so status of the room
        print("+---------- STATUS ----------+")
        print(f" Temperature: {self.ambient_temperature.temperature_in}")
        #TODO: add others when availaible
        print("+----------------------------+")
    
    def get_info(self, ambient, room, str_mode):
        basic_dict = {"room_insulation":self.__room_insulation, "temperature_out":str(self.__temp_out)+" °C", "humidity_out":str(self.__hum_out)+" %", "co2_out":str(self.__co2_out)+" ppm"}
        if 'temperature' == ambient:
            basic_dict.update({"temperature_in": self.ambient_temperature.get_temperature(str_mode=str_mode)})
            return basic_dict
        elif 'humidity' == ambient:
            basic_dict.update({"humidity_in": self.ambient_humidity.get_humidity(str_mode=str_mode)})
            return basic_dict
        elif 'co2level' == ambient:
            basic_dict.update({"co2_in": self.ambient_co2.get_co2level(str_mode=str_mode)})
            return basic_dict
        elif 'brightness' == ambient:
            basic_dict.update({"brightness_in": self.ambient_light.get_global_brightness(room, str_mode=str_mode)}) # room can be None, average of bright sensors is then computed
            return basic_dict
        elif 'time' == ambient:
            basic_dict.update({"simtime_in": self.time.simulation_time(str_mode=str_mode), "speed_factor":self.time.speed_factor})
            return basic_dict
        elif 'all' == ambient:
            ambient_dict = {"temperature_in": self.ambient_temperature.get_temperature(str_mode=str_mode),
                            "humidity_in": self.ambient_humidity.get_humidity(str_mode=str_mode),
                            "co2_in": self.ambient_co2.get_co2level(str_mode=str_mode),
                            "brightness_in": self.ambient_light.get_global_brightness(room, str_mode=str_mode),
                            "simtime": self.time.simulation_time(str_mode=str_mode), "speed_factor":self.time.speed_factor}
            basic_dict.update(ambient_dict)
            return basic_dict
        







# def compute_co2level(temperature, humidity):
#     # https://iopscience.iop.org/article/10.1088/1755-1315/81/1/012083/pdf
#     p1 = -122304.827954597
#     p2 = 5420.9575012248 
#     p3 = -195.944936343794 
#     p4 = 2.36182806127216 
#     p5 = 634340.418393413
#     p6 = -1884046.22528529
#     p7 = 1749351.78760737
#     p8 = 1191371.85647522
#     p9 = -2122702.79768627
#     h = temperature # in °C
#     t = humidity/100 # 0<h<1
#     co2_ppm = p1 + p2*t + p3*math.pow(t,2) + p4*math.pow(t,3)
#     co2_ppm += p5*h + p6*math.pow(t,2) + p7*math.pow(t,3) + p8*math.pow(t,4) + p9*math.pow(t,5)
#     return co2_ppm