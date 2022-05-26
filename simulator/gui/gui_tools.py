#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pyglet
import logging
import json

from datetime import datetime
from .gui_config import *



class DeviceListWidget(object):
    def __init__(self, x, y, batch, group_label, group_box):
        self.__batch = batch
        self.__group_box = group_box
        self.topleft_y = y+OFFSET_DEVICELIST_BOX_TOP
        self.length = OFFSET_DEVICELIST_BOX_TOP+OFFSET_DEVICELIST_BOX_BOTTOM
        # Max number of devices to display in list, int div length (from start of list, below title 'y') by offset between devices
        self.MAX_SIZE_DEVICES_LIST = (y - OFFSET_LIST_DEVICE)//OFFSET_LIST_DEVICE
        self.box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, self.topleft_y-self.length, DEVICE_LIST_BOX_WIDTH, self.length, border=BOX_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=batch, group=self.__group_box)

        self.deviceslist_title = pyglet.text.Label("Devices in the Room:",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15, bold=True,
                                    x=x, y=y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group_label)
    
    def update_box(self, new_length):
        # update devices list box, new_length is simply number of devices * offset between them
        new_length = new_length if new_length>0 else OFFSET_DEVICELIST_BOX_TOP # length depend if there are devices or not
        self.length = new_length + OFFSET_DEVICELIST_BOX_TOP+OFFSET_DEVICELIST_BOX_BOTTOM
        self.box_shape.delete()
        self.box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, self.topleft_y-self.length, DEVICE_LIST_BOX_WIDTH, height=self.length, border=BOX_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=self.__batch, group=self.__group_box)
    
    def hit_test(self, x, y): # to check if mouse click is on the Device list widget
        # print(f"x: {self.box_shape.x} < {x} < {(self.box_shape.x + DEVICE_LIST_BOX_WIDTH)}")
        # print(f"y: {self.box_shape.y} < {y} < {(self.box_shape.y + self.length)}")
        return (self.box_shape.x < x < (self.box_shape.x + DEVICE_LIST_BOX_WIDTH) and
                self.box_shape.y < y < (self.box_shape.y + self.length))


class SimTimeWidget(object):
    def __init__(self, x, y, batch, group_box, group_label):
        self.box_shape = pyglet.shapes.BorderedRectangle(x, y-SIMTIME_BOX_LENGTH/2, SIMTIME_BOX_WIDTH, SIMTIME_BOX_LENGTH, border=BOX_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=batch, group=group_box)
        self.simtime_label = pyglet.text.Label("SimTime: 0", # init the simulation time title
                                    font_name=FONT_SYSTEM_TITLE, font_size=FONT_SIZE_SIMTIME, bold=True,
                                    x=x+OFFSET_SIMTIME_BOX, y=y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group_label)
        
        self.date_label = pyglet.text.Label("Date: ", # init the simulation time display
                                    font_name=FONT_SYSTEM_TITLE, font_size=FONT_SIZE_SIMTIME, bold=True,
                                    x=x+OFFSET_SIMTIME_BOX, y=y-OFFSET_SIMTIME_DATE,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group_label)

class DayTimeWeatherWidget(object):
    def __init__(self, x, y, batch, group_box, group_daytime, group_weather, temp_out, hum_out, co2_out):
        self.__pos_x = x
        self.__pos_y = y
        self.__batch = batch
        self.__group_weather = group_weather
        self.__group_daytime = group_daytime
        self.__temp_out, self.__hum_out, self.__co2_out = temp_out, hum_out, co2_out
        self.box_shape = pyglet.shapes.BorderedRectangle(self.__pos_x, self.__pos_y, TIMEWEATHER_BOX_WIDTH, TIMEWEATHER_BOX_LENGTH, border=BOX_BORDER,
                                    color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                    batch=self.__batch, group=group_box)
        self.__out_state_str = f"Out state: {temp_out}°C  {hum_out}%  {co2_out}ppm  " 
        self.out_state_label = pyglet.text.Label(self.__out_state_str, # out_temp, out_co2, out_hum, out_lux
                                    font_name=FONT_SYSTEM_TITLE, font_size=FONT_SIZE_OUT_STATE, bold=True,
                                    x=self.__pos_x+OFFSET_STATE_LABEL, y=self.__pos_y+OFFSET_STATE_LABEL,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__group_daytime)
        self.sunrise_img = pyglet.image.load(SUNRISE_PATH)
        self.sun_img = pyglet.image.load(SUN_PATH)
        self.sunset_img = pyglet.image.load(SUNSET_PATH)
        self.moon_img = pyglet.image.load(MOON_PATH)
        self.cloud_overcast_img = pyglet.image.load(CLOUD_OVERCAST_PATH)
        self.cloud_dark_img = pyglet.image.load(CLOUD_DARK_PATH)

        self.__tod_dict= {"sunrise":{"img":self.sunrise_img, "offset_x":OFFSET_SUNRISE_X, "offset_y":OFFSET_SUNRISE_SUNSET_Y}, 
                            "sun":{"img":self.sun_img, "offset_x":OFFSET_SUN_MOON_X, "offset_y":OFFSET_SUN_MOON_Y},
                            "sunset":{"img":self.sunset_img, "offset_x":OFFSET_SUNSET_X, "offset_y":OFFSET_SUNRISE_SUNSET_Y}, 
                            "moon":{"img":self.moon_img, "offset_x":OFFSET_SUN_MOON_X, "offset_y":OFFSET_SUN_MOON_Y}}
        self.__weather_dict = {"overcast":{"img":self.cloud_overcast_img, "offset_x_ratio":OFFSET_CLOUD_WIDTH_RATIO, "offset_y_ratio":OFFSET_CLOUD_LENGTH_RATIO}, 
                                "dark":{"img":self.cloud_dark_img, "offset_x_ratio":OFFSET_CLOUD_DARK_WIDTH_RATIO, "offset_y_ratio":OFFSET_CLOUD_DARK_LENGTH_RATIO}}
        # self.sunrise = pyglet.sprite.Sprite(self.sunrise_img, self.__pos_x + OFFSET_SUNRISE_X, self.__pos_y + OFFSET_SUNRISE_SUNSET_Y, batch=self.__batch, group=self.__group_daytime)
        # self.sun = pyglet.sprite.Sprite(self.sun_img, self.__pos_x + OFFSET_SUN_MOON_X, self.__pos_y + OFFSET_SUN_MOON_Y, batch=self.__batch, group=self.__group_daytime)
        # self.sunset = pyglet.sprite.Sprite(self.sunset_img, self.__pos_x + OFFSET_SUNSET_X, self.__pos_y + OFFSET_SUNRISE_SUNSET_Y, batch=self.__batch, group=self.__group_daytime)
        # self.moon = pyglet.sprite.Sprite(self.moon_img, self.__pos_x + OFFSET_SUN_MOON_X, self.__pos_y + OFFSET_SUN_MOON_Y, batch=self.__batch, group=self.__group_daytime)

        # self.sprite = self.sun
        # self.cloud_overcast =  pyglet.sprite.Sprite(self.cloud_overcast_img, self.sprite.x + OFFSET_CLOUD_WIDTH_RATIO*self.sprite.width, self.sprite.y + OFFSET_CLOUD_LENGTH_RATIO*self.sprite.height, batch=self.__batch, group=self.__group_weather)
        # self.cloud_dark =  pyglet.sprite.Sprite(self.cloud_dark_img, self.sprite.x + OFFSET_CLOUD_DARK_WIDTH_RATIO*self.sprite.width, self.sprite.y + *self.sprite.height, batch=self.__batch, group=self.__group_weather)
        
    def update_out_state(self, weather:str, time_of_day:str, lux_out:float):
        """ weather is 'clear', 'overcast' or 'dark', time_of_day is 'sunrise', 'sun', 'sunset, 'moon'"""
        # delete old sprite
        if hasattr(self, "tod_sprite"):
            self.tod_sprite.delete()
        if hasattr(self, 'weather_sprite'):
            self.weather_sprite.delete()
        # update lux_out
        self.lux_out = round(lux_out,1) if lux_out > 1 else lux_out
        self.out_state_label.text = self.__out_state_str + str(self.lux_out) + "lux"
        # update time_of_day img
        if time_of_day in self.__tod_dict:
            self.tod_sprite = pyglet.sprite.Sprite(self.__tod_dict[time_of_day]["img"], self.__pos_x + self.__tod_dict[time_of_day]["offset_x"], self.__pos_y + self.__tod_dict[time_of_day]["offset_y"], batch=self.__batch, group=self.__group_daytime)
        # update weather img
        if weather != 'clear':
            if weather in self.__weather_dict:
                self.weather_sprite = pyglet.sprite.Sprite(self.__weather_dict[weather]["img"], self.tod_sprite.x + self.__weather_dict[weather]["offset_x_ratio"] * self.tod_sprite.width, self.tod_sprite.y + self.__weather_dict[weather]["offset_y_ratio"] * self.tod_sprite.height, batch=self.__batch, group=self.__group_weather)

        



# Button widgets
class ButtonWidget(object):
    def __init__(self, x, y, batch, button_file, group, label_text=''):
        self.img = pyglet.image.load(button_file)
        self.__width, self.__length = self.img.width, self.img.height
        self.pos_x, self.pos_y = x, y
        self.__batch, self.group = batch, group
        self.sprite = pyglet.sprite.Sprite(self.img, self.pos_x, self.pos_y, batch=self.__batch, group=self.group)
        self.label = pyglet.text.Label(label_text,
                                    font_name=FONT_BUTTON, font_size=10,
                                    x=(self.pos_x+self.__width//2), y=(self.pos_y-OFFSET_LABEL_BUTTON),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.__batch, group=self.group)

    def hit_test(self, x, y): # to check if mouse click is on the Button widget
        return (self.pos_x < x < (self.pos_x + self.__width) and
                self.pos_y < y < (self.pos_y + self.__length))

class ButtonPause(object):
    def __init__(self, x, y, batch, button_pause_file, button_play_file, group):
        self.pause_file = button_pause_file
        self.play_file = button_play_file
        self.file_to_use = self.pause_file
        self.widget = ButtonWidget(x, y, batch, self.file_to_use, group=group, label_text='PLAY/PAUSE')

    def activate(self, gui_window):
        gui_window.pause_simulation()
        if gui_window.room.simulation_status: # Pause button if simulation running
            self.file_to_use = self.pause_file
        elif not gui_window.room.simulation_status: # Play button if simulation paused
            self.file_to_use = self.play_file
        self.clicked = True  ## NOTE cannot be private as we call hasattr() from GUI class

    def update_image(self, reload=False):
        if reload:
            self.file_to_use = self.pause_file
        self.widget.sprite.image = pyglet.image.load(self.file_to_use)

class ButtonStop(object):
    def __init__(self, x, y, batch, button_file, group):
        self.stop_file = button_file
        self.widget = ButtonWidget(x, y, batch, self.stop_file, group=group, label_text='STOP')

    def activate(self, gui_window):
        pyglet.app.exit()

class ButtonReload(object):
    def __init__(self, x, y, batch, button_file, group):
        self.widget = ButtonWidget(x, y, batch, button_file, group=group, label_text='RELOAD')

    def activate(self, gui_window):
        gui_window.reload_simulation()

class ButtonSave(object):
    def __init__(self, x, y, batch, button_file, group):
        self.widget = ButtonWidget(x, y, batch, button_file, group=group, label_text='SAVE')

    def activate(self, gui_window):
        #from system import generate_configfile_from_system
        saved_config_path = gui_window.SAVED_CONFIG_PATH + datetime.now().strftime("%d%m%Y_%H%M%S")
        # generate_configfile_from_system(gui_window.room, saved_config_path)
        with open(saved_config_path, 'w') as saved_config_file:
            json.dump(gui_window.system_config_dict, saved_config_file, indent=2)
        print(" button SAVE is pressed")

class ButtonDefault(object):
    def __init__(self, x, y, batch, button_file, group):
        self.default_file = button_file
        self.widget = ButtonWidget(x, y, batch, self.default_file, group=group, label_text='DEFAULT')

    def activate(self, gui_window):
        gui_window.reload_simulation(default_config = True)


class DimmerSetterWidget(object):
    def __init__(self, room_device_widget):
        # Initialize dimmer state ratio label
        self.room_device_widget = room_device_widget
        self.room_device_widget.sprite.opacity = OPACITY_CLICKED
        self.init_state_ratio = room_device_widget.in_room_device.device.state_ratio
        self.center_x, self.center_y = room_device_widget.pos_x, room_device_widget.pos_y
        self.state_label_x = self.center_x + room_device_widget.width//2
        self.state_label_y = self.center_y - room_device_widget.length//2
        self.being_set = False


    def start_setting_dimmer(self, batch, group):
        self.being_set = True
        self.state_ratio_label = pyglet.text.Label(str(self.init_state_ratio),
                                    font_name=FONT_INTERACTIVE, font_size=FONT_SIZE_INTERACTIVE,
                                    x=(self.state_label_x+OFFSET_DIMMER_RATIO), y=self.state_label_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group,
                                    color=color_from_state_ratio(self.init_state_ratio))

    def update_ratio(self, new_ratio):
        self.state_ratio = new_ratio
        self.state_ratio_label.text = str(self.state_ratio)
        self.state_ratio_label.color = color_from_state_ratio(self.state_ratio)

    def delete(self):
        self.room_device_widget.sprite.opacity = OPACITY_DEFAULT
        if hasattr(self, 'state_ratio_label'):
            self.state_ratio_label.delete()
            return 1
        return 0


# Device widgets
class DeviceWidget(object):
    def __init__(self, pos_x, pos_y, batch, img_file_ON, img_file_OFF, group, device_type, device_class, device_number, available_device=False, img_neutral=None): # img_neutral for themometer
        ''' docstring'''
        # in room device attribute set during initialization
        self.device_class = device_class
        self.label_name = self.device_class.lower()+device_number
        # self.name = label_name
        self.device_type = device_type
        self.in_motion = False # Temporary flag to inform that the device widget is being moved
        self.sprite_state = False # devices turned ON/OFF
        self.sprite_state_ratio = 100
        # self.group_addresses = [] # will store the group addresses, can control the number e.g. for sensors
        self.file_ON = img_file_ON
        self.file_OFF = img_file_OFF #usefull to create a moving instance of the available devices
        self.pos_x, self.pos_y = pos_x, pos_y # Center of the image, simulated position on room
        self.img_ON, self.img_OFF = pyglet.image.load(self.file_ON), pyglet.image.load(self.file_OFF)
        self.width, self.length = self.img_ON.width, self.img_ON.height #ON/OFF images have the same width, height of image is called length in this program
        self.__batch = batch
        self.group = group

        if available_device: # available devices for a manual import (displayed outside of the GUI)
            self.origin_x, self.origin_y = self.pos_x, self.pos_y
        else:
            self.origin_x, self.origin_y = self.pos_x - self.width//2, self.pos_y - self.length//2
            if "humiditysoil" in self.label_name: 
                self.humiditysoil = 10 # arbitrary init of soil humidity
                # https://www.acurite.com/blog/soil-moisture-guide-for-plants-and-vegetables.html
                self.drop_red = pyglet.image.load(DROP_RED_PATH)
                self.drop_yellow = pyglet.image.load(DROP_YELLOW_PATH)
                self.drop_green = pyglet.image.load(DROP_GREEN_PATH)
                self.drop_blue = pyglet.image.load(DROP_BLUE_PATH)
                self.drop_pos_x = self.pos_x + self.width//2
                self.drop_pos_y = self.pos_y
                self.drop_label_pos_x = self.drop_pos_x
                self.drop_label_pos_y = self.pos_y - 1.5*OFFSET_LABEL_DEVICE  ####NOTE
                self.drop_sprite = pyglet.sprite.Sprite(self.drop_red, x=self.drop_pos_x, y=self.drop_pos_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
                self.drop_label = pyglet.text.Label('10%',
                                    font_name=FONT_INTERACTIVE, font_size=FONT_SIZE_INTERACTIVE,
                                    x=self.drop_label_pos_x, y=self.drop_label_pos_y,
                                    anchor_x='left', anchor_y='center',
                                    batch=self.__batch, group=self.group)
                self.drop_label.color = color_from_humiditysoil(self.humiditysoil)
        
        if img_neutral is not None: # for thermometer when no change in temperature
            self.img_neutral = pyglet.image.load(img_neutral)
            self.sprite = pyglet.sprite.Sprite(self.img_neutral, x=self.origin_x, y=self.origin_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
        else:
            self.sprite = pyglet.sprite.Sprite(self.img_OFF, x=self.origin_x, y=self.origin_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
        self.label = pyglet.text.Label(self.label_name,
                                    font_name=FONT_DEVICE, font_size=10,
                                    x=(self.origin_x+self.width//2), y=(self.origin_y-OFFSET_LABEL_DEVICE),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.__batch, group=self.group)

    def __eq__(self, device_to_compare):
        return self.label_name == device_to_compare.label_name


    def hit_test(self, x, y): # to check if mouse click is on a device image
        # if "humiditysoil" in self.label_name and self.device_class == 'HumiditySoil':
        if hasattr(self, "humiditysoil"):
            return ((self.sprite.x < x < self.sprite.x+self.width and
                    self.sprite.y < y < self.sprite.y+self.length) or 
                    (self.drop_sprite.x < x < self.drop_sprite.x+self.drop_sprite.width and 
                    self.drop_sprite.y < y < self.drop_sprite.y+self.drop_sprite.height))
        else:
            return (self.sprite.x < x < self.sprite.x+self.width and
                self.sprite.y < y < self.sprite.y+self.length)

    def update_position(self, new_x, new_y, loc_x=0, loc_y=0, update_loc=False):
        """ Doct string"""
        self.pos_x, self.pos_y = new_x, new_y
        self.origin_x, self.origin_y = self.pos_x - self.width//2, self.pos_y - self.length//2
        self.sprite.update(x=self.origin_x, y=self.origin_y)
        self.label.update(x=(self.origin_x+self.width//2), y=(self.origin_y-OFFSET_LABEL_DEVICE))
        if update_loc:
            self.loc_x, self.loc_y = loc_x, loc_y
            self.in_room_device.update_location(new_x=self.loc_x, new_y=self.loc_y)
            logging.info(f"Location of {self.label_name} is updated to {self.loc_x}, {self.loc_y}")

    def delete(self):
        self.sprite.delete()
        self.label.delete()
        if "humiditysoil" in self.label_name:
            self.drop_sprite.delete()
            self.drop_label.delete()
    
    def update_drop(self):
        if hasattr(self, 'humiditysoil'):
            # https://www.acurite.com/media/magpleasure/mpblog/upload/5/2/523755c20577be6c9f5ee5a27003abf6.jpg
            if self.humiditysoil <= 20.0:
                drop = self.drop_red
            elif self.humiditysoil <= 40.0:
                drop = self.drop_yellow
            elif self.humiditysoil <= 60.0:
                drop = self.drop_green
            else:
                drop = self.drop_blue
            self.drop_sprite.delete()
            self.drop_label.delete()
            self.drop_sprite = pyglet.sprite.Sprite(drop, x=self.drop_pos_x, y=self.drop_pos_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
            self.drop_label = pyglet.text.Label(str(self.humiditysoil)+'%',
                                    font_name=FONT_INTERACTIVE, font_size=FONT_SIZE_INTERACTIVE,
                                    x=self.drop_label_pos_x, y=self.drop_label_pos_y,
                                    anchor_x='left', anchor_y='center',
                                    batch=self.__batch, group=self.group)
            self.drop_label.color = color_from_humiditysoil(self.humiditysoil)
    
    def update_thermometer_sprite(self, rising_temp):
        if 'thermometer' in self.label_name:
            if rising_temp is None and hasattr(self, 'img_neutral'):
                self.sprite.delete()
                self.sprite = pyglet.sprite.Sprite(self.img_neutral, x=self.origin_x, y=self.origin_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
            elif rising_temp:
                self.sprite.delete()
                self.sprite = pyglet.sprite.Sprite(self.img_ON, x=self.origin_x, y=self.origin_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
            elif rising_temp == False:
                self.sprite.delete()
                self.sprite = pyglet.sprite.Sprite(self.img_OFF, x=self.origin_x, y=self.origin_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
            




class AvailableDevices(object): # library of devices availables, presented on the left side on the GUI
    def __init__(self, batch, group_dev, group_box):
        self.in_motion = False
        self.devices = []

        self.box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, OFFSET_AVAILABLEDEVICES_LINE3-OFFSET_AVAILABLE_DEVICES-WIN_BORDER/2, AVAILABLE_DEVICES_BOX_WIDTH, AVAILABLE_DEVICES_BOX_LENGTH, border=BOX_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=batch, group=group_box)

        # Line 1
        self.led = DeviceWidget(WIN_BORDER, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_LED_ON_PATH, DEVICE_LED_OFF_PATH, group_dev, "actuator", "LED", '', available_device=True)
        self.devices.append(self.led)
        next_image_offset_x = self.led.pos_x + self.led.width + OFFSET_AVAILABLE_DEVICES
        self.heater = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_HEATER_ON_PATH, DEVICE_HEATER_OFF_PATH, group_dev, "actuator", "Heater", '',  available_device=True)
        self.devices.append(self.heater)
        next_image_offset_x = self.heater.pos_x + self.heater.width + OFFSET_AVAILABLE_DEVICES
        self.ac = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_AC_ON_PATH, DEVICE_AC_OFF_PATH, group_dev, "actuator", "AC", '',  available_device=True)
        self.devices.append(self.ac)
        next_image_offset_x = self.ac.pos_x + self.ac.width + OFFSET_AVAILABLE_DEVICES
        self.switch = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_SWITCH_ON_PATH, DEVICE_SWITCH_OFF_PATH, group_dev, "actuator", "Switch", '', available_device=True)
        self.devices.append(self.switch)
        # next_image_offset_x = self.switch.pos_x + self.switch.width + OFFSET_AVAILABLE_DEVICES

        # Line 2
        self.button = DeviceWidget(WIN_BORDER, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_BUTTON_ON_PATH, DEVICE_BUTTON_OFF_PATH, group_dev, "functional_module", "Button", '', available_device=True)
        self.devices.append(self.button)
        next_image_offset_x = self.button.pos_x + self.button.width + OFFSET_AVAILABLE_DEVICES
        self.dimmer = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_DIMMER_ON_PATH, DEVICE_DIMMER_OFF_PATH, group_dev, "functional_module", "Dimmer", '', available_device=True)
        self.devices.append(self.dimmer)
        next_image_offset_x = self.dimmer.pos_x + self.dimmer.width + 1.2*OFFSET_AVAILABLE_DEVICES
        self.presencesensor = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_PRESENCE_ON_PATH, DEVICE_PRESENCE_OFF_PATH, group_dev, "sensor", "PresenceSensor", '',  available_device=True)
        self.devices.append(self.presencesensor)
        next_image_offset_x = self.presencesensor.pos_x + self.presencesensor.width + 5*OFFSET_AVAILABLE_DEVICES
        self.thermometer = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2+OFFSET_AVAILABLE_DEVICES, batch, DEVICE_THERMO_HOT_PATH, DEVICE_THERMO_COLD_PATH, group_dev, "sensor", "Thermometer", '', available_device=True, img_neutral = DEVICE_THERMO_NEUTRAL_PATH)
        self.devices.append(self.thermometer)
        # next_image_offset_x = self.thermometer.pos_x + self.thermometer.width + 2*OFFSET_AVAILABLE_DEVICES

        # Line 3
        self.brightness = DeviceWidget(WIN_BORDER, OFFSET_AVAILABLEDEVICES_LINE3, batch, DEVICE_BRIGHT_SENSOR_PATH, DEVICE_BRIGHT_SENSOR_PATH, group_dev, "sensor", "Brightness", '', available_device=True)
        self.devices.append(self.brightness)
        next_image_offset_x = self.brightness.pos_x + self.brightness.width + 0.1*OFFSET_AVAILABLE_DEVICES
        self.airsensor = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE3, batch, DEVICE_AIRSENSOR_PATH, DEVICE_AIRSENSOR_PATH, group_dev, "actuator", "AirSensor", '', available_device=True)
        self.devices.append(self.airsensor)
        next_image_offset_x = self.airsensor.pos_x + self.airsensor.width + 0.4*OFFSET_AVAILABLE_DEVICES
        self.co2sensor = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE3, batch, DEVICE_CO2_PATH, DEVICE_CO2_PATH, group_dev, "sensor", "CO2Sensor", '',  available_device=True)
        self.devices.append(self.co2sensor)
        next_image_offset_x = self.co2sensor.pos_x + self.co2sensor.width + OFFSET_AVAILABLE_DEVICES
        self.humidityair = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE3, batch, DEVICE_HUMIDITYAIR_PATH, DEVICE_HUMIDITYAIR_PATH, group_dev, "sensor", "HumidityAir", '',  available_device=True)
        self.devices.append(self.humidityair)
        next_image_offset_x = self.humidityair.pos_x + self.humidityair.width + 1.85*OFFSET_AVAILABLE_DEVICES
        self.humiditysoil = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE3, batch, DEVICE_HUMIDITYSOIL_PATH, DEVICE_HUMIDITYSOIL_PATH, group_dev, "sensor", "HumiditySoil", '',  available_device=True)
        self.devices.append(self.humiditysoil)
        # next_image_offset_x = self.humiditysoil.pos_x + self.humiditysoil.width + OFFSET_AVAILABLE_DEVICES
        
        




# Room widget
class RoomWidget(object):
    def __init__(self, width, length, batch, group_bg, group_mg, label_group, label):
        # Coordinates to draw room rectangle shape
        self.origin_x_shape = WIN_WIDTH - width - WIN_BORDER - 2*ROOM_BORDER
        self.origin_y_shape = WIN_BORDER
        # Cordinates to represent the actual room dimensions (border is a margin to accept devices on boundaries)
        self.origin_x = WIN_WIDTH - WIN_BORDER - ROOM_BORDER - width
        self.origin_y = WIN_BORDER + ROOM_BORDER
        # Label coordinates
        # self.label_x = self.origin_x + width/2
        # self.label_y = self.origin_y + OFFSET_ROOM_LABEL
        # Actual dimensions of the room, not the rectangle shape
        self.width = width
        self.length = length
        self.name = label
        self.img = pyglet.image.load(ROOM_BACKGROUND_PATH)
        self.__batch = batch
        self.shape = pyglet.shapes.BorderedRectangle(self.origin_x_shape, self.origin_y_shape, width+2*ROOM_BORDER, length+2*ROOM_BORDER, border=ROOM_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=self.__batch, group=group_bg)#, group = group
        self.shape.opacity = OPACITY_ROOM
        self.sprite = pyglet.sprite.Sprite(self.img, self.origin_x, self.origin_y, batch=self.__batch, group=group_mg)
        self.label = pyglet.text.Label(self.name,
                                    font_name=FONT_SYSTEM_INFO, font_size=75,
                                    x=(self.origin_x + self.width/2), y=(self.origin_y + self.length/2),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.__batch, group=label_group)
        self.label.opacity = OPACITY_ROOM_LABEL
        self.sprite.opacity = OPACITY_ROOM

    def hit_test(self, x, y): # to check if mouse click is on the Room widget
        return (self.origin_x < x < (self.origin_x + self.width) and
                self.origin_y < y < (self.origin_y + self.length))


class PersonWidget(object):
    def __init__(self, img_path, x, y, batch, group):
        self.moving = True
        self.__batch, self.__group = batch, group
        self.pos_x, self.pos_y = x, y
        self.img = pyglet.image.load(img_path)
        self.width, self.length = self.img.width, self.img.height
        self.origin_x, self.origin_y = self.pos_x - self.width//2, self.pos_y - self.length//2
        self.sprite = pyglet.sprite.Sprite(self.img, self.origin_x, self.origin_y, batch=self.__batch, group=self.__group)
    
    def hit_test(self, x, y): # to check if mouse click is on the Room widget
        return (self.origin_x < x < (self.origin_x + self.width) and
                self.origin_y < y < (self.origin_y + self.length))
    
    def update_position(self, new_x, new_y):
        """ Doct string"""
        self.pos_x, self.pos_y = new_x, new_y
        self.origin_x, self.origin_y = self.pos_x - self.width//2, self.pos_y - self.length//2
        self.sprite.update(x=self.origin_x, y=self.origin_y)
    
    def delete(self):
        self.sprite.delete()

   

# Useful functions
def gui_pos_to_system_loc( pos_x, pos_y, width_ratio, length_ratio, room_x, room_y):
    try:
        loc_x = (pos_x - room_x) / width_ratio
        loc_y = (pos_y - room_y) / length_ratio
    except AttributeError:
        logging.warning("The system is not initialized and the room width/length ratios are not defined")
    return loc_x, loc_y

def system_loc_to_gui_pos( loc_x, loc_y, width_ratio, length_ratio, room_x, room_y):
    try:
        pos_x = int(room_x + width_ratio * loc_x)
        pos_y = int(room_y + length_ratio * loc_y)
    except AttributeError:
        logging.warning("The system is not initialized and the room width/length ratios are not defined")
    return pos_x, pos_y

def color_from_state_ratio(state_ratio): #state_ratio in 0-100
    if 0 <= state_ratio:
        if state_ratio < 25:
            return COLOR_LOW
        elif state_ratio < 50:
            return COLOR_MEDIUM_LOW
        elif state_ratio < 75:
            return COLOR_MEDIUM_HIGH
        elif state_ratio <= 100 :
            return COLOR_HIGH

def color_from_humiditysoil(humiditysoil):
    if 0 <= humiditysoil:
        if humiditysoil <= 20.0:
            return COLOR_RED
        elif humiditysoil <= 40.0:
            return COLOR_YELLOW
        elif humiditysoil <= 60.0:
            return COLOR_GREEN
        elif humiditysoil <= 100 :
            return COLOR_BLUE

def dimmer_ratio_from_mouse_pos(mouse_y, dimmer_center_y):
    # We check distance from mouse to center on vertical y axis only
    relative_distance = mouse_y - dimmer_center_y 
    if relative_distance >= OFFSET_MAX_DIMMER_RATIO:
        return 100 # max percentage ratio
    elif relative_distance <= -OFFSET_MAX_DIMMER_RATIO:
        return 0 # min percentage ratio
    else:
        ratio = round(100 * (relative_distance+OFFSET_MAX_DIMMER_RATIO) / (2*OFFSET_MAX_DIMMER_RATIO), 2)
        return ratio