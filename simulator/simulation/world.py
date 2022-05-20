"""
Some class definitions for the simulation of the physical world
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]

from typing import List
import time, math, schedule
import sys, logging
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

    def __init__(self, simulation_speed_factor:float):
        # Real world simulated time that passed between 2 clock ticks
        # self.physical_interval = 3600
        self.speed_factor = simulation_speed_factor
        # Amount of time (in seconds) between two software clock ticks
        # self.virtual_interval = self.physical_interval/self.speed_factor

    # def set_simulation_speed_factor(self, speed_factor):
    #     self.virtual_interval = self.physical_interval/speed_factor

    # def set_virtual_interval(self, interval:float):
    #     # seconds of software simulation corresponding to a simulated 'real-world' hour
    #     self.virtual_interval = interval

    # Scheduler management, if not in GUI mode
    def scheduler_init(self):
        self.scheduler = AsyncIOScheduler()
        return self.scheduler

    def scheduler_add_job(self, job_function):
        try:
            self.update_job = self.scheduler.add_job(job_function, 'interval', seconds = self.virtual_interval)
        except AttributeError:
            logging.warning("The Scheduler is not initialized: job cannnot be added")

    def scheduler_start(self):
        try:
            self.scheduler.start()
            self.start_time = time.time()
        except AttributeError:
            logging.warning("The Scheduler is not initialized and cannot be started")

    # Simulation time management
    def simulation_time(self):
        try:
            elapsed_time = time.time() - self.start_time
            return elapsed_time
        except AttributeError:
            logging.warning("The Simulation time is not initialized")


class AmbientTemperature:
    '''Class that implements temperature in a system'''

    def __init__(self, room_volume, update_rule_ratio, out_temp:float, room_insulation):
        # self.simulation_speed_factor = simulation_speed_factor
        # self.simulated_dt = system_dt * simulation_speed_factor # e.g., update called every 1*180seconds = 3min
        self.update_rule_ratio = update_rule_ratio # update rules are per hour, ratio translate it to the system dt
        self.temperature = out_temp # Will be obsolete when we introduce gradient of temperature
        self.outside_temperature = out_temp
        self.room_insulation = room_insulation
        self.room_volume = room_volume
        """Describes room volume in m3"""
        self.temp_sources = []
        """List of temperature actuators sources in the room"""
        self.temp_sensors = []
        """List of temperature sensors in the room"""
        self.temp_controllers = []

        self.max_power_heater = 0
        self.max_power_ac = 0

    def add_source(self, source ): # source is an InRoomDevice # Heatsource is an object that heats the room
        from devices import Heater, AC
        self.temp_sources.append(source) #add check on source
        if isinstance(source.device, Heater):
            self.max_power_heater += source.device.max_power
        if isinstance(source.device, AC):
            self.max_power_ac += source.device.max_power

    def add_sensor(self, tempsensor):
        self.temp_sensors.append(tempsensor) #add check on sensor

    # def add_temp_controllers(self, temp_controllers):
    #     self.temp_controllers.append(temp_controllers) #add check on sensor
    
    def watts_to_temp(self, watts):
        return ((watts - 70)*2)/7 + 18

    def max_temperature_in_room(self, volume, max_power, insulation_state='good'):
        """Maximum reachable temperature in the specified room with the current enabled heaters, with exterior temperature being 20C"""
        from system import INSULATION_TO_CORRECTION_FACTOR
        watts = max_power/((1+INSULATION_TO_CORRECTION_FACTOR[self.room_insulation])*volume)
        return self.watts_to_temp(watts)

    def update(self):
        from devices import Heater, AC
        from system import INSULATION_TO_TEMPERATURE_FACTOR
        '''Apply the update rules taking into consideration the maximum power of each heating device, if none then go back progressively to default outside temperature'''
        logging.info("Temperature update")
        if(not self.temp_sources):
            self.temperature = (self.temperature + self.outside_temperature)//2 # Decreases by the average of temp and outside_temp, is a softer slope
        else:
            self.total_max_power = self.max_power_heater + self.max_power_ac
            #### actual power would allow to compute concrete max temp
            # self.total_actual_power = 0
            # for source in self.temp_sources:
            #     if source.device.status and source.device.state:
            #         self.total_actual_power += source.device.power
            for source in self.temp_sources: # sources of heat or cold
                if source.device.status and source.device.state: # if source enabled
                    if isinstance(source.device, Heater):
                        source.device.update_rule = source.device.power/self.total_max_power 
                        self.temperature += source.device.update_rule*self.update_rule_ratio
                    if isinstance(source.device, AC):
                        source.device.update_rule = - source.device.power/self.total_max_power
                        self.temperature += source.device.update_rule*self.update_rule_ratio # The ac update rule is <0
            # Compute max temp
            #relative_max_power = self.max_power_heater - self.max_power_ac
            # Apply temp factor from outside temp and insulation
            self.temperature += (self.outside_temperature - self.temperature) * INSULATION_TO_TEMPERATURE_FACTOR[self.room_insulation]
            #TODO: compute max and min temp!!!
            max_temp = 30.0 #self.max_temperature_in_room(self.room_volume, self.max_power_heater, "good") ##mean(max_temps)
            min_temp = 10.0
            self.temperature = max(min_temp, min(max_temp, self.temperature)) # temperature cannot exceed max temp
            # print(f"system temp= {round(self.temperature, 2)}")
            # self.temperature = max(min_temp, self.temperature)
                # self.temperature = (self.temperature + max_temp) // 2 # Decreases by the average of temp and outside_temp, is a softer slope
        temperature_levels = []
        for sensor in self.temp_sensors: # temp sensors are in room devices
            # print(f"sensor {sensor.device.name} temp= {round(self.temperature, 2)}")
            sensor.device.temperature = self.temperature
            temperature_levels.append((sensor.name, sensor.device.temperature))
        # for controller in self.temp_controllers:#
        #     controller.temperature = self.temperature ##TODO: notify the bus with a telegram to heat sources
        return temperature_levels

    def __repr__(self):
        return f"{self.temperature} °C"

    def __str__(self):
        return f"{self.temperature} °C"


class AmbientLight:
    '''Class that implements Light in a room'''
    def __init__(self):
        self.light_sources: List = []
        """List of all devices that emit light"""
        self.light_sensors: List = []
        """List of all devices that measure brightness"""

    def add_source(self, lightsource):
        self.light_sources.append(lightsource) #lightsource is an object of type

    def add_sensor(self, lightsensor):
        self.light_sensors.append(lightsensor)

    def read_brightness(self, brightness_sensor): #Read brightness at a particular sensor
        brightness = 0
        for source in self.light_sources:
            # If the light is on and enabled on the bus
            if source.device.is_enabled() and source.device.state:
                # Compute distance between sensor and each source
                dist = system.compute_distance(source, brightness_sensor)
                # Compute the new brightness
                residual_lumen = (1/dist)*source.device.lumen*(source.device.state_ratio/100) # we suppose proportionality between state ratio and lumen 
                brightness += residual_lumen
        return brightness

    def update(self): #Updates all brightness sensors of the world (the room)
        logging.info("Brightness update")
        brightness_levels = []
        for sensor in self.light_sensors:
            # Update the sensor's brightness
            sensor.device.brightness = self.read_brightness(sensor) # set the newly calculated sensor brightness
            brightness_levels.append((sensor.device.name, sensor.device.brightness))

        return brightness_levels


class AmbientHumidity:
    """ Class for relative humidity in a room (relative compared to max humidity or vapour pressure"""
    # elements that influence humidity:
    # - windows
    # - heater/cooler
    # - insulation
    def __init__(self, out_temp, out_hum, room_insulation, update_rule_ratio):
        self.temp = out_temp
        self.outside_humidity = out_hum
        self.room_insulation = room_insulation
        self.humidity_sources: List = []
        self.humidity_sensors: List = []
        # https://journals.ametsoc.org/view/journals/apme/57/6/jamc-d-17-0334.1.xml
        # https://www.weather.gov/lmk/humidity
        self.saturation_vapour_pressure = self.compute_saturation_vapor_pressure_water(self.temp)
        self.humidity = 35 # default Relative Humidity in %, same in the whole room
        self.vapor_pressure = round(self.saturation_vapour_pressure * self.humidity/100, 8) # Absolut vapor pressure in room
        self.update_rule_ratio = update_rule_ratio

    
    def add_source(self, humiditysource):
        self.humidity_sources.append(humiditysource)
    def add_sensor(self, humiditysensor):
        self.humidity_sensors.append(humiditysensor)
    
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
        self.saturation_vapour_pressure = self.compute_saturation_vapor_pressure_water(temperature)
        self.temp = temperature
        self.humidity = 100 * self.vapor_pressure / self.saturation_vapour_pressure # Compute the new humidity after a temperature change (no open windows considered)
        # Apply humidity factor from outside temp and insulation
        self.humidity += (self.outside_humidity - self.humidity) * INSULATION_TO_HUMIDITY_FACTOR[self.room_insulation] * self.update_rule_ratio
        # We recompute vapor pressure from new hum
        self.vapor_pressure = self.saturation_vapour_pressure * self.humidity/100
        ### TODO: add condition if window open
        # if window open:
        #   new_humidity = hum+2hum_out /3 => drastic change in humidity when we open the window
        humidity_levels = []
        for sensor in self.humidity_sensors:
            sensor.device.humidity = round(self.humidity, 2)
            humidity_levels.append((sensor.device.name, sensor.device.humidity))
        return humidity_levels



class AmbientCO2:
    # elements that influence humidity:
    # - windows

    # 250-400ppm	Normal background concentration in outdoor ambient air
    # 400-1,000ppm	Concentrations typical of occupied indoor spaces with good air exchange
    # 1,000-2,000ppm	Complaints of drowsiness and poor air.
    # 2,000-5,000 ppm	Headaches, sleepiness and stagnant, stale, stuffy air. Poor concentration, loss of attention, increased heart rate and slight nausea may also be present.
    # 5,000	Workplace exposure limit (as 8-hour TWA) in most jurisdictions.
    # >40,000 ppm	Exposure may lead to serious oxygen deprivation resulting in permanent brain damage, coma, even death.

    def __init__(self, out_co2, room_insulation, update_rule_ratio):
        self.co2_level = 800 # ppm
        self.outside_co2 = out_co2
        self.room_insulation = room_insulation
        self.co2_sensors: List = []
        self.update_rule_ratio = update_rule_ratio
    
    def add_sensor(self, co2sensor):
        self.co2_sensors.append(co2sensor)
    
    def update(self, temperature, humidity):
        from system import INSULATION_TO_CO2_FACTOR
        logging.info("CO2 update")
        # self.co2_level = compute_co2level(temperature, humidity) # totally wrong values...
        ## TODO : change CO2 if window opened, co2 rise until window is opened
        ## TODO: check of presence 
        # Apply humidity factor from outside temp and insulation
        self.co2_level += (self.outside_co2 - self.co2_level) * INSULATION_TO_CO2_FACTOR[self.room_insulation] * self.update_rule_ratio
        co2_levels = []
        for sensor in self.co2_sensors:
            sensor.device.co2_level = int(self.co2_level)
            co2_levels.append((sensor.device.name, sensor.device.co2_level))
        return co2_levels



class World:
    '''Class that implements a representation of the physical world with attributes such as time, temperature...'''
    ## INITIALISATION ##
    def __init__(self, room_width, room_length, room_height, simulation_speed_factor, system_dt, room_insulation, out_temp, out_hum, out_co2):
        self.time = Time(simulation_speed_factor) # simulation_speed_factor=240 -> 1h of simulated time = 1min of simulation
        self.room_insulation = room_insulation
        self.out_temp, self.out_hum, self.out_co2 = out_temp, out_hum, out_co2
        self.update_rule_ratio = (system_dt * simulation_speed_factor)/3600
        self.ambient_temperature = AmbientTemperature(room_width*room_height*room_length, self.update_rule_ratio, out_temp, room_insulation)
        self.ambient_light = AmbientLight() #TODO: set a default brightness depending on the time of day (day/night), blinds state (open/closed), and wheather state(sunny, cloudy,...)
        self.ambient_humidity = AmbientHumidity(self.out_temp, self.out_hum, self.room_insulation, self.update_rule_ratio)
        self.ambient_co2 = AmbientCO2(self.out_co2, self.room_insulation, self.update_rule_ratio)
        self.ambient_world = [self.ambient_temperature, self.ambient_light, self.ambient_humidity, self.ambient_co2]

    def update(self):
        brightness_levels = self.ambient_light.update()
        temperature_levels = self.ambient_temperature.update()
        humidity_levels = self.ambient_humidity.update(self.ambient_temperature.temperature)
        co2_levels = self.ambient_co2.update(self.ambient_temperature.temperature, self.ambient_humidity.humidity)
        # humidity_levels = self.ambient_humidity.update()
        return brightness_levels, temperature_levels, humidity_levels, co2_levels

    def get_world_state(self): # one world per room, so status of the room
        print("+---------- STATUS ----------+")
        print(f" Temperature: {self.ambient_temperature.temperature}")
        #TODO: add others when availaible
        print("+----------------------------+")





def compute_co2level(temperature, humidity):
    # https://iopscience.iop.org/article/10.1088/1755-1315/81/1/012083/pdf
    p1 = -122304.827954597
    p2 = 5420.9575012248 
    p3 = -195.944936343794 
    p4 = 2.36182806127216 
    p5 = 634340.418393413
    p6 = -1884046.22528529
    p7 = 1749351.78760737
    p8 = 1191371.85647522
    p9 = -2122702.79768627
    h = temperature # in °C
    t = humidity/100 # 0<h<1
    co2_ppm = p1 + p2*t + p3*math.pow(t,2) + p4*math.pow(t,3)
    co2_ppm += p5*h + p6*math.pow(t,2) + p7*math.pow(t,3) + p8*math.pow(t,4) + p9*math.pow(t,5)
    return co2_ppm