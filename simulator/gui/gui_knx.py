#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pyglet
import copy
import logging
import shutil
import json
from time import time
from datetime import timedelta
import numpy as np



from system.tools import configure_system_from_file, DEV_CLASSES, GroupAddress, Location
from .gui_tools import ButtonPause, ButtonStop, ButtonReload, ButtonSave, ButtonDefault, DeviceWidget, AvailableDevices, RoomWidget, system_loc_to_gui_pos, gui_pos_to_system_loc, DimmerSetterWidget, dimmer_ratio_from_mouse_pos, SimTimeWidget, DeviceListWidget
from .gui_config import *


class GUIWindow(pyglet.window.Window):
    ''' Class to define the GUI window, the widgets and text displayed in it and the functions reactign to the user actions (mouse click, input text,...) '''
    def __init__(self, config_path, default_config_path, empty_config_path, rooms=None):
        super(GUIWindow, self).__init__(WIN_WIDTH, WIN_LENGTH, caption='KNX Simulation Window', resizable=False)
        from system import configure_system_from_file
        # Configure the window size
        self.width = WIN_WIDTH
        self.length = WIN_LENGTH
        #self.set_minimum_size(1200, 1000) #minimum window size
        #self.set_minimum_size(1300, 1100) #minimum window size
        #self.push_handlers(on_resize=self.local_on_resize) #to avoid redefining the on_resize handler
        # Configure batch of modules to draw on events (mouse click, moving,...)
        self.batch = pyglet.graphics.Batch()
        # Create multiple layers to superpose the graphical elements
        self.background = pyglet.graphics.OrderedGroup(0)
        self.middlebackground = pyglet.graphics.OrderedGroup(1)
        self.middleground = pyglet.graphics.OrderedGroup(2)
        self.foreground = pyglet.graphics.OrderedGroup(3)
        #document = pyglet.text.document.UnformattedDocument()
        # STore the initial configuration file path if the user wants to reload the simulation
        self.CONFIG_PATH = config_path
        self.DEFAULT_CONFIG_PATH = default_config_path
        self.EMPTY_CONFIG_PATH = empty_config_path
        # Room object to represent the KNX System
        try:
            self.room = rooms[0]
        except TypeError:
            logging.info("No room is defined, the rooms default characteristics are applied")
            self.room = configure_system_from_file(self.DEFAULT_CONFIG_PATH)

        # Array to store the devices added to the room (by dragging them for instance)
        self.room_devices = [] # DeviceWidget instances 
        self.devices_scroll = 0
        # Default individual addresses when adding devices during simulation
        self.individual_address_default = [0,0,100] # we suppose no more than 99 devices on area0/line0, and no more than 155 new manually added devices
        # Flag to set up group addresses
        self.linking_group_address = True
        # Initialize the room widget to draw in the window
        self.room_widget = RoomWidget(ROOM_WIDTH, ROOM_LENGTH, self.batch, group_bg=self.background, group_mg=self.middlebackground, label=self.room.name, label_group=self.middleground)
        # Array to store labels to display in room devices list
        self.room_devices_labels = []
        # Array to store brightnesses & temperature in the room
        self.room_brightness_labels = []
        self.room_brightness_levels = []
        self.room_temperature_labels = []
        self.room_temperature_levels = []
        self.room_airquality_labels = []
        self.room_airquality_levels = []

        # Initialize the Available devices widgets to draw them on the left size, s that a user can drag them in the room
        self.available_devices = AvailableDevices(self.batch, group_dev=self.foreground, group_box=self.background)
        # Define the position of the text elements and the text box to interact with the user
        self.commandlabel_pos = (self.width-WIN_BORDER, 96*(self.length//100))
        self.simlabel_pos = (WIN_WIDTH-ROOM_WIDTH-WIN_BORDER-ROOM_BORDER, 95*(self.length//100))  #2*(self.width//100)
        self.textbox_pos = (80*(self.width//100), 91*(self.length//100))
        self.devicelist_pos = (WIN_BORDER, 50*(self.length//100))  #2*(self.width//100)
        self.brightness_label_pos = (WIN_BORDER, 95*(self.length//100)) #2*(self.width//100)
        self.brightness_level_pos = self.brightness_label_pos[0], self.brightness_label_pos[1]-OFFSET_TITLE
        self.temperature_label_pos = (WIN_BORDER, 89*(self.length//100))  #2*(self.width//100)
        self.temperature_level_pos = self.temperature_label_pos[0], self.temperature_label_pos[1]-OFFSET_TITLE
        self.airsensor_label_pos = (WIN_BORDER, 83*(self.length//100))
        self.arisensor_level_pos = self.airsensor_label_pos[0], self.airsensor_label_pos[1]-OFFSET_TITLE
        # Define the position of the buttons to interact with the user
        self.button_pause_pos = (INITIAL_POSITION_BUTTON*(self.width//100), 93*(self.length//100)) # 
        self.button_stop_pos = ((OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.width//100), 93*(self.length//100))
        self.button_reload_pos = ((2*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.width//100), 93*(self.length//100))
        self.button_save_pos = ((3*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.width//100), 93*(self.length//100))
        self.button_default_pos = ((4*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.width//100), 93*(self.length//100))
        # Create the text labels and the textbox to display to the user
        self.command_label = pyglet.text.Label('Enter your command',
                                    font_name=FONT_SYSTEM_TITLE, font_size=20, bold=True,
                                    x=self.commandlabel_pos[0], y=self.commandlabel_pos[1],
                                    anchor_x='right', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
        self.simtime_widget = SimTimeWidget(self.simlabel_pos[0], self.simlabel_pos[1], self.batch, group_label=self.foreground, group_box=self.background)
        self.text_box = pyglet.shapes.Rectangle(self.textbox_pos[0], self.textbox_pos[1], self.width-self.textbox_pos[0]-WIN_BORDER, 40, color=(255, 255, 255),
                                    batch=self.batch, group=self.background)
        # Initialize the text box label to display the user input in the textbox
        self.input_label = pyglet.text.Label("",
                                    font_name=FONT_USER_INPUT, font_size=15,
                                    color=(10, 10, 10, 255),
                                    x=(self.text_box.x+10), y=(self.text_box.y+20),
                                    anchor_x='left', anchor_y='center',
                                    batch=self.batch, group=self.foreground)
        # Initialize the list of devices in the room
        self.devicelist_widget = DeviceListWidget(self.devicelist_pos[0], self.devicelist_pos[1], self.batch, group_label=self.foreground, group_box=self.background)

        self.sensors_box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, OFFSET_SENSOR_LEVELS_BOX_Y, SENSOR_LEVELS_BOX_WIDTH, WIN_LENGTH - OFFSET_SENSOR_LEVELS_BOX_Y- WIN_BORDER/2, border=WIN_BORDER/2,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=self.batch, group=self.background)
        self.brightness_label = pyglet.text.Label("Brightness (lumens):",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.brightness_label_pos[0], y=self.brightness_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
        self.temperature_label = pyglet.text.Label("Temperature (°C):",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.temperature_label_pos[0], y=self.temperature_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
        self.airquality_label = pyglet.text.Label("Air quality - T(°C) / CO2(ppm) / RH(%):",  #350-1,000 ppm, 
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.airsensor_label_pos[0], y=self.airsensor_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
        # GUI buttons
        self.buttons = []
        # Reload Button to re-initialize the simulation
        self.button_pause = ButtonPause(self.button_pause_pos[0], self.button_pause_pos[1], self.batch, BUTTON_PAUSE_PATH, BUTTON_PLAY_PATH, group=self.foreground)
        self.buttons.append(self.button_pause)
        self.button_stop = ButtonStop(self.button_stop_pos[0], self.button_stop_pos[1], self.batch, BUTTON_STOP_PATH, group=self.foreground)
        self.buttons.append(self.button_stop)
        self.button_reload = ButtonReload(self.button_reload_pos[0], self.button_reload_pos[1], self.batch, BUTTON_RELOAD_PATH, group=self.foreground)
        self.buttons.append(self.button_reload)
        self.button_save = ButtonSave(self.button_save_pos[0], self.button_save_pos[1], self.batch, BUTTON_SAVE_PATH, group=self.foreground)
        self.buttons.append(self.button_save)
        self.button_default = ButtonDefault(self.button_default_pos[0], self.button_default_pos[1], self.batch, BUTTON_DEFAULT_PATH, group=self.foreground)
        self.buttons.append(self.button_default)

## Method to initialize the gui system from room object
    def initialize_system(self, saved_config_path=None, system_dt=1):
        from devices import Button, LED, Brightness, Dimmer, Heater, AC, Thermometer, AirSensor # ,PresenceSensor
        self.room.window = self # same for the GUi window object, but to room1 object
        if saved_config_path: # stor the saved config path only at first call, not when user reload the system
            self.saved_config_path = saved_config_path + "saved_config_" # We will add the time when the simulation was saved
            # We save the system dictionary from config file to update it as the user add devices
            with open(self.CONFIG_PATH, "r") as config_file:
                self.system_config_dict = json.load(config_file)
        # self.saved_config_path_temp = shutil.copyfile(self.CONFIG_PATH, self.saved_config_path+"temp.json")
        # self.room.saved_config_path = self.saved_config_path
        pyglet.clock.schedule_interval(self.room.update_world, interval=system_dt, gui_mode=True) # update every 1seconds, corresponding to 1 * speed_factor real seconds
        # ratio to translate room physical (simulated) size in pixels to place correctly devices
        self.room_width_ratio = ROOM_WIDTH / self.room.width
        self.room_length_ratio = ROOM_LENGTH / self.room.length

        # self.green_img = pyglet.image.load(GREEN_PATH)
        # self.green_sprite = pyglet.sprite.Sprite(self.green_img, x=80, y=0, batch=self.batch, group=self.foreground)
        print(" ------- Initialization of the KNX System's GUI representation -------")
        for in_room_device in self.room.devices:
            device = in_room_device.device
            if isinstance(device, Brightness):
                brightness_sensor = self.available_devices.brightness
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, brightness_sensor.file_ON, brightness_sensor.file_OFF, group=self.foreground, device_type='sensor', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)

            if isinstance(device, Button):
                button = self.available_devices.button
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, button.file_ON, button.file_OFF, group=self.foreground, device_type='functional_module', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)
            
            if isinstance(device, Dimmer):
                dimmer = self.available_devices.dimmer
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, dimmer.file_ON, dimmer.file_OFF, group=self.foreground, device_type='functional_module', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)

            if isinstance(device, LED):
                led = self.available_devices.led
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, led.file_ON, led.file_OFF, group=self.foreground, device_type='actuator', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)

            if isinstance(device, Heater):
                heater = self.available_devices.heater
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, heater.file_ON, heater.file_OFF, group=self.foreground, device_type='actuator', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)
            
            if isinstance(device, AC):
                ac = self.available_devices.ac
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, ac.file_ON, ac.file_OFF, group=self.foreground, device_type='actuator', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)
            
            if isinstance(device, Thermometer):
                thermometer = self.available_devices.thermometer
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, thermometer.file_ON, thermometer.file_OFF, group=self.foreground, device_type='actuator', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)
            
            if isinstance(device, AirSensor):
                airsensor = self.available_devices.airsensor
                # x, y = in_room_device.location.x, in_room_device.location.y
                # x = int(self.room_widget.x + self.room_width_ratio * x)
                # y = int(self.room_widget.y + self.room_length_ratio * y)
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, airsensor.file_ON, airsensor.file_OFF, group=self.foreground, device_type='sensor', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)
            
        self.display_devices_list()
        self.display_brightness_labels()
        self.display_temperature_labels()
        self.display_airquality_labels()

## Methods to display lists, devices and sensor values
    def display_devices_list(self, scroll=0):
        # Re-Initialisation of the room devices list
        for room_device_label in self.room_devices_labels:
            room_device_label.delete()
        self.room_devices_labels = []
        room_devices_counter = 0
        list_x = self.devicelist_widget.deviceslist_title.x
        list_y = self.devicelist_widget.deviceslist_title.y - OFFSET_DEVICESLIST_TITLE
        # To scroll in devices list
        self.devices_scroll = max(0, self.devices_scroll+scroll)
        # max scroll to limit how deep a user can go down in the list, we keep MAX_SIZE_DEVICE_LIST devices visible at least
        max_scroll = len(self.room_devices) - MAX_SIZE_DEVICE_LIST
        if max_scroll > 0: # if enough devices 
            self.devices_scroll = int(min(self.devices_scroll, max_scroll))
        # Display the current room devices name in list
        for room_device in self.room_devices[self.devices_scroll:]:
            room_dev_x = list_x
            room_dev_y = list_y - room_devices_counter*(OFFSET_LIST_DEVICE) # display device name below main label
            room_dev_ia_y = room_dev_y - OFFSET_INDIVIDUAL_ADDR_LABEL 
            ia_label = room_device.in_room_device.device.individual_addr.ia_string
            room_dev_gas = room_device.in_room_device.device.group_addresses
            ga_text = ' -- (' + ', '.join([str(ga) for ga in room_dev_gas]) + ')'
            label_text = room_device.label.text + ga_text
            room_device_label = pyglet.text.Label(label_text,
                                font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_DEVICESLIST,
                                x=room_dev_x, y=room_dev_y,
                                anchor_x='left', anchor_y='bottom',
                                batch=self.batch, group=self.foreground)
            room_device_ia_label = pyglet.text.Label(ia_label,
                                font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_INDIVIDUAL_ADDR,
                                x=room_dev_x, y=room_dev_ia_y,
                                anchor_x='left', anchor_y='bottom',
                                batch=self.batch, group=self.foreground)
            self.room_devices_labels.append(room_device_label) 
            self.room_devices_labels.append(room_device_ia_label) 
            room_devices_counter += 1
        self.devicelist_widget.update_box(new_length=room_devices_counter*OFFSET_LIST_DEVICE)

    def display_brightness_labels(self):
        # Re-Initialisation of the room devices list
        for room_brightness_label in self.room_brightness_labels:
            room_brightness_label.delete()
        self.room_brightness_labels = []
        room_brightness_counter = 0
        bright_x = self.brightness_label.x
        bright_y = self.brightness_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.room_devices:
            if 'bright' in room_device.label.text.lower():
                room_bright_x = bright_x + room_brightness_counter*OFFSET_SENSOR_LEVELS
                room_bright_y = bright_y
                room_brightness_counter += 1
                room_brightness_label = pyglet.text.Label('bright'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LABEL,
                                    x=room_bright_x, y=room_bright_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
                self.room_brightness_labels.append(room_brightness_label)

    def display_temperature_labels(self):
        # Re-Initialisation of the room devices list
        for room_temperature_label in self.room_temperature_labels:
            room_temperature_label.delete()
        self.room_temperature_labels = []
        room_temperature_counter = 0
        temp_x = self.temperature_label.x
        temp_y = self.temperature_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.room_devices:
            if 'thermometer' in room_device.label.text.lower():
                room_temp_x = temp_x + room_temperature_counter*OFFSET_SENSOR_LEVELS
                room_temp_y = temp_y
                room_temperature_counter += 1
                room_temperature_label = pyglet.text.Label('thermo'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LABEL,
                                    x=room_temp_x, y=room_temp_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
                self.room_temperature_labels.append(room_temperature_label)
    
    def display_airquality_labels(self):
        # Re-Initialisation of the room devices list
        for room_airquality_label in self.room_airquality_labels:
            room_airquality_label.delete()
        self.room_airquality_labels = []
        room_airquality_counter = 0
        air_x = self.airquality_label.x
        air_y = self.airquality_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.room_devices:
            if 'airsensor' in room_device.label.text.lower():
                room_air_x = air_x + room_airquality_counter*OFFSET_SENSOR_LEVELS
                room_air_y = air_y
                room_airquality_counter += 1
                room_airquality_label = pyglet.text.Label('airsens'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LABEL,
                                    x=room_air_x, y=room_air_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
                self.room_airquality_labels.append(room_airquality_label)

    def update_sensors(self, brightness_levels, temperature_levels, humidity_levels, co2_levels):
        # Re-Initialisation of the room sensors list
        for room_brightness_level in self.room_brightness_levels:
            room_brightness_level.delete()
        self.room_brightness_levels = []
        for room_temperature_level in self.room_temperature_levels:
            room_temperature_level.delete()
        self.room_temperature_levels = []
        for room_airquality_level in self.room_airquality_levels:
            room_airquality_level.delete()
        self.room_airquality_levels = []
        airsensor_dict = {}

        for bright in brightness_levels:
            bright_name, brightness = bright[0], round(bright[1],1)
            self.display_brightness_level(bright_name, brightness)
        for temp in temperature_levels:
            temp_name, temperature = temp[0], round(temp[1],2)
            if 'air' in temp_name:
                try:
                    airsensor_dict[temp_name]["temperature"] = temperature
                except KeyError:
                    airsensor_dict[temp_name] = {}
                    airsensor_dict[temp_name]["temperature"] = temperature
            self.display_temperature_level(temp_name, temperature)
        for hum in humidity_levels:
            hum_name, humidity = hum[0], hum[1]
            if 'air' in hum_name:
                try:
                    airsensor_dict[hum_name]["humidity"] = humidity
                except KeyError:
                    airsensor_dict[hum_name] = {}
                    airsensor_dict[hum_name]["humidity"] = humidity
            # else only if humidity sensor exist by itself in the system
            # else:
            #     self.display_humidity_levels(hum_name, humidity=humidity)
        for co2 in co2_levels:
            co2_name, co2_level = co2[0], co2[1]
            if 'air' in co2_name:
                try:
                    airsensor_dict[co2_name]["co2_level"] = co2_level
                except KeyError:
                    airsensor_dict[co2_name] = {}
                    airsensor_dict[co2_name]["co2_level"] = co2_level
        # Display all air quality sensors at once
        if len(airsensor_dict) > 0:
            self.display_airquality_levels(airsensor_dict)
        

    def display_airquality_levels(self, airsensor_dict):
        for airsensor in airsensor_dict: # airsensor are the keys
            temp = hum = co2 = None
            airquality_level_text = ''
            room_airsensor_counter = 0
            for room_airquality_label in self.room_airquality_labels:
                if airsensor[-1] == room_airquality_label.text[-1]:
                    air_level_x = room_airquality_label.x
                    air_level_y = room_airquality_label.y - OFFSET_SENSOR_TITLE
                    if "temperature" in airsensor_dict[airsensor]:
                        temp = airsensor_dict[airsensor]["temperature"]
                        airquality_level_text += str(temp)+'/'
                    else:
                        airquality_level_text += '-/'
                    if "co2_level" in airsensor_dict[airsensor]:
                        co2 = airsensor_dict[airsensor]["co2_level"]
                        airquality_level_text += str(co2)+'/'
                    else:
                        airquality_level_text += '-/'
                    if "humidity" in airsensor_dict[airsensor]:
                        hum = airsensor_dict[airsensor]["humidity"]
                        airquality_level_text += str(hum)
                    else:
                        airquality_level_text += '-'
                    room_airquality_level = pyglet.text.Label(airquality_level_text,
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LEVEL,
                                    x=air_level_x, y=air_level_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
                    self.room_airquality_levels.append(room_airquality_level)
                room_airsensor_counter += 1


    def display_brightness_level(self, bright_name, brightness):
        room_brightness_counter = 0
        for room_brightness_label in self.room_brightness_labels:
            if bright_name[-1] == room_brightness_label.text[-1]: #check only the digit
                bright_level_x = room_brightness_label.x #+ room_brightness_counter*OFFSET_SENSOR_LEVELS
                bright_level_y = room_brightness_label.y - OFFSET_SENSOR_TITLE
                bright_level_text = str(brightness) # + ' lm'
                room_brightness_level = pyglet.text.Label(bright_level_text,
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LEVEL,
                                    x=bright_level_x, y=bright_level_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
                self.room_brightness_levels.append(room_brightness_level)
            room_brightness_counter +=1

    def display_temperature_level(self, temp_name, temperature):
        room_temperature_counter = 0
        for room_temperature_label in self.room_temperature_labels:
            if temp_name[-1] == room_temperature_label.text[-1]: #check only the digit
                temp_level_x = room_temperature_label.x #+ room_brightness_counter*OFFSET_SENSOR_LEVELS
                temp_level_y = room_temperature_label.y - OFFSET_SENSOR_TITLE
                temp_level_text = str(temperature) # + ' lm'
                room_temperature_level = pyglet.text.Label(temp_level_text,
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LEVEL,
                                    x=temp_level_x, y=temp_level_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
                self.room_temperature_levels.append(room_temperature_level)
            room_temperature_counter +=1

## Methods to react to user actions (turn ON/OFF a device button, press a gui button, add device to simulation,...)
    def switch_sprite(self):
        for room_device in self.room_devices:
            try:
                if room_device.sprite_state != room_device.in_room_device.device.state: #sprite represetation is not the same as real state
                    room_device.sprite_state = not room_device.sprite_state
                    room_device.sprite.delete()
                    if room_device.sprite_state: # device turned ON
                        room_device.sprite = pyglet.sprite.Sprite(room_device.img_ON, x=room_device.origin_x, y=room_device.origin_y, batch=self.batch, group=self.foreground)
                    else: # device turned OFF
                        room_device.sprite = pyglet.sprite.Sprite(room_device.img_OFF, x=room_device.origin_x, y=room_device.origin_y, batch=self.batch, group=self.foreground)
                if room_device.sprite_state and room_device.sprite_state_ratio != room_device.in_room_device.device.state_ratio: # dimmmer changed state_ratio of e.g. a light that is ON
                    room_device.sprite_state_ratio = room_device.in_room_device.device.state_ratio
                    new_opacity = OPACITY_MIN + (OPACITY_DEFAULT-OPACITY_MIN) * room_device.sprite_state_ratio/100
                    room_device.sprite.opacity = new_opacity
        
            except AttributeError: #if no state attribute (e.g. sensor)
                pass
    
    def add_device_to_simulation(self, room, pos_x, pos_y):
        from system.tools import IndividualAddress
        new_device_class = self.moving_device.device_class
        area, line, dev_number = [self.individual_address_default[i] for i in range(3)]#, self.individual_address_default[1], self.individual_address_default[2]
        individual_address = IndividualAddress(area, line, dev_number)
        new_refid = "M-O_X" + str(self.individual_address_default[2])
        self.individual_address_default[2] += 1
        if self.individual_address_default[2] > 255:
            self.individual_address_default[2] = 0
            self.individual_address_default[1] += 1
            if self.individual_address_default[1] > 15:
                self.individual_address_default[1] = 0
                self.individual_address_default[0] = max(self.individual_address_default[0]+1, 15)

        similar_devices_counter = 1
        for device in self.room_devices:
            if new_device_class.lower() in device.device_class.lower():
                # print(f"---+++--- device similar: {device.label_name}, {device_class}")
                similar_devices_counter +=1
        new_device_name = new_device_class.lower()+str(similar_devices_counter)
        # print(f"device_name: {device_name}")
        # Creation of the device object
        new_status = "enabled"
        device = DEV_CLASSES[new_device_class](new_device_name, new_refid, individual_address, new_status)
        loc_x, loc_y = gui_pos_to_system_loc(pos_x, pos_y, self.room_width_ratio, self.room_length_ratio,
                                            self.room_widget.origin_x, self.room_widget.origin_y)
        loc_z = 1 # 1 is default height z
        self.moving_device.in_room_device = room.add_device(device, loc_x, loc_y, loc_z)
        self.moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
        self.room_devices.append(self.moving_device)
        self.add_device_to_config(new_device_name, new_device_class, new_refid, str(area), str(line), str(dev_number), new_status, loc_x, loc_y, loc_z, room.name)

        self.display_brightness_labels()
        self.display_temperature_labels()
        self.display_airquality_labels()

## Methods to react to gui buttons when pressed
    def reload_simulation(self, default_config = False, empty_config = False):
        # Remove the update function from schedule
        pyglet.clock.unschedule(self.room.update_world)
        # Re-Initialisation of the room devices list
        for room_device in self.room_devices:
            room_device.delete()
        self.room_devices = []
        # Re-Initialisation of the room brightness labels list
        for room_brightness_label in self.room_brightness_labels:
            room_brightness_label.delete()
        self.room_brightness_labels = []
        # Re-Initialisation of the room device labels list
        for room_device_label in self.room_devices_labels:
            room_device_label.delete()
        self.room_devices_labels = []
        # Re-initialization of Pause button
        self.button_pause.update_image(reload=True)
        # Re configuration of the room and simulation time
        if default_config:
            self.room = configure_system_from_file(self.DEFAULT_CONFIG_PATH)[0]
        elif empty_config:
            self.room = configure_system_from_file(self.EMPTY_CONFIG_PATH)[0]
        else:
            self.room = configure_system_from_file(self.CONFIG_PATH)[0] # only one room for now
        self.room.world.time.start_time = time()
        self.initialize_system()

    def pause_simulation(self):
        self.room.simulation_status = not self.room.simulation_status
        if not self.room.simulation_status:
            logging.info("The simulation is paused")
            self.room.world.time.pause_time = time() # save current time to update start_time when
        else:
            logging.info("The simulation is resumed")
            paused_time = time() - self.room.world.time.pause_time
            self.room.world.time.start_time += paused_time

## Methods to update devices position (in simulation) and/or location (physical location of device in room)
    def update_device_location(self, pos_x, pos_y):
        loc_x, loc_y = gui_pos_to_system_loc(pos_x, pos_y, self.room_width_ratio, self.room_width_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
        self.moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
        self.update_config_loc(loc_x, loc_y, self.room.name)
    
    def replace_moving_device_in_room(self, x, y):
        from system import Location
        x_min = self.room_widget.origin_x #+ self.moving_device.width//2
        x_max = self.room_widget.origin_x + self.room_widget.width #- self.moving_device.width//2
        y_min = self.room_widget.origin_y #+ self.moving_device.length//2
        y_max = self.room_widget.origin_y + self.room_widget.length #- self.moving_device.length//2

        new_x = (x_min if x<x_min else x)
        new_x = (x_max if x_max<new_x else new_x)
        new_y = (y_min if y<y_min else y)
        new_y = (y_max if y_max<new_y else new_y)
        loc_x, loc_y = gui_pos_to_system_loc(new_x, new_y, self.room_width_ratio, self.room_width_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
        self.moving_device.update_position(new_x, new_y, loc_x, loc_y, update_loc = True)
        self.update_config_loc(loc_x, loc_y, self.room.name)

## Methods to update the config dict to be saved as config file
    def add_device_to_config(self,dev_name, dev_class, dev_refid, area, line, dev_number, dev_status, loc_x, loc_y, loc_z, room_name):
        # KNX config
        knx_config = self.system_config_dict["knx"]
        area_key = 'area' + area
        line_key = 'line' + line
        knx_loc = '.'.join([area, line, dev_number])
        line_devices = knx_config[area_key][line_key]["devices"]
        line_devices[dev_name] = {"class":dev_class, "refid":dev_refid, "knx_location":knx_loc, "status":dev_status}
        # knx_config[area_key][line_key]["devices"] = line_devices
        # World config
        world_config = self.system_config_dict["world"]
        for room in world_config["rooms"]:
            if world_config["rooms"][room]["name"] == room_name:
                world_config["rooms"][room]["room_devices"][dev_name] = [loc_x, loc_y, loc_z]

    def update_config_loc(self, loc_x, loc_y, room_name:str):
        loc_z = 1
        dev_name = self.moving_device.in_room_device.device.name
        world_config = self.system_config_dict["world"]
        for room in world_config["rooms"]:
            if world_config["rooms"][room]["name"] == room_name:
                world_config["rooms"][room]["room_devices"][dev_name] = [loc_x, loc_y, loc_z]
    
    def update_config_ga(self, room_device, group_address:str, detach = False):
        dev_name = room_device.in_room_device.device.name
        gas_config = self.system_config_dict["knx"]["group_addresses"]
        for g in range(len(gas_config)): #ga_config is a list of dict[{},{}]
            ga = gas_config[g]
            if group_address == ga["address"]:
                if dev_name not in ga["group_devices"]: # Test if device not already assigned to this group address
                    ga["group_devices"].append(dev_name)
                    logging.info(f"The {dev_name} is added to device list of group address {group_address} in temporary config dict")
                    return 1
                else: # If device assigned to this group address
                    if detach:
                        ga["group_devices"].remove(dev_name)
                        logging.info(f"The {dev_name} is removed from device list of group address {group_address} in temporary config dict")
                        if len(ga["group_devices"]) < 1: # If no more devices are linked to this ga
                            del gas_config[g]
                            logging.info(f"The group address {group_address} is removed from temporary config dict because no device is attached to it")
                            return 0
                    return 1
        # If this group address does not exist yet
        new_ga = {"address":group_address, "group_devices":[dev_name]}
        gas_config.append(new_ga)
        logging.info(f"The group address {group_address} is added with {dev_name} attached to it in temporary config dict")


## Pyglet 'on-event' methods
    def on_draw(self):
        ''' Called when the window is redrawn:
            Draw all the elements added to the batch in the window at each event (mouse click, drag,...)'''
        self.clear()
        self.batch.draw()
        #self.push_handlers(self.focus.caret)

    def on_text(self, text):
        ''' Called when the user press a keyboard symbol (all keys except modifiers):
            Add the text input by the user to the text label displayed in the text box '''
        self.input_label.text += text
        #print("on text\n")

    def on_key_press(self, symbol, modifiers):
        from system.tools import configure_system_from_file
        ''' Called when any key is pressed:
            Define special action to modify text, save input text or end the simulation'''
        # Erase a character from the user input textbox
        if symbol == pyglet.window.key.BACKSPACE:
            self.input_label.text = self.input_label.text[:-1] # Remove last character
        # Save the command input by the user and erase it from the text box
        elif symbol == pyglet.window.key.ENTER:
            from system import user_command_parser
            user_command_parser(self.input_label.text, self.room)
            self.switch_sprite()
            self.input_label.text = ''
        # CTRL-ESCAPE to end the simulation
        elif symbol == pyglet.window.key.ESCAPE:
            if modifiers and pyglet.window.key.MOD_CTRL:
                pyglet.app.exit()
        # CTRL-P to Pause/Play simulation
        elif symbol == pyglet.window.key.P:
            if modifiers and pyglet.window.key.MOD_CTRL:
                # self.pause_simulation()
                self.button_pause.activate(self)
                self.button_pause.update_image()
        # CTRL-R to reload simulation from start
        elif symbol == pyglet.window.key.R:
            if modifiers and pyglet.window.key.MOD_CTRL:
                self.reload_simulation()

    def on_key_release(self, symbol, modifiers): # release the ga connecting flag
        ''' Called when a key is released:
            Define actions to take when specific keys are released'''
        # Cancel the Group Adddress linking if CRTL key is released before the connection is established between two devices
        if symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL:
            for room_device in self.room_devices:
                room_device.linking_group_address = False
                room_device.sprite.opacity = OPACITY_DEFAULT
            for button in self.buttons:
                button.widget.sprite.opacity = OPACITY_DEFAULT
        # Cancel the Dimmer ratio setting if SHIFT key is released before the mouse is released to validate the value
        if symbol == pyglet.window.key.LSHIFT or symbol == pyglet.window.key.RSHIFT:
            if hasattr(self, 'dimmer_being_set'):
                self.dimmer_being_set.delete()
                delattr(self, 'dimmer_being_set')

    def on_mouse_press(self, x, y, button, modifiers):
        ''' Called when a mouse button is pressed (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is pressed'''
        if button == pyglet.window.mouse.LEFT:
            # LEFT click + SHIFT : activate functional module (e.g. turn button ON/OFF)
            if modifiers & pyglet.window.key.MOD_SHIFT:
                from devices.device_abstractions import FunctionalModule
                from devices.functional_modules import Button, Dimmer
                for room_device in self.room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if isinstance(room_device.in_room_device.device, FunctionalModule):# == "functional_module": # button,..
                            if isinstance(room_device.in_room_device.device, Dimmer):
                                # Create an object to set the dimmer value, and validate by releasing the mouse with SHIFT pressed
                                self.dimmer_being_set = DimmerSetterWidget(room_device)
                                return
                            elif isinstance(room_device.in_room_device.device, Button):
                                room_device.in_room_device.device.user_input() # user_input will send the telegram with the appropriate payload on the bus
                                self.switch_sprite()
            # LEFT click + CTRL : set up group address between multiple devices
            elif modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if self.room.attach(room_device.in_room_device.device, self.input_label.text): # Test if ga is correct
                            self.update_config_ga(room_device, self.input_label.text)
                        self.display_devices_list()
            # LEFT click on device w/o modifiers : add devices in simulator by dragging them in the Room area, or move room devices, or click on button
            else:
                if not hasattr(self, 'moving_device'): # NOTE: this test should never fail, as before clicking, no devices should be moving (attribute self.moving_device deleted when mouse is released)
                    for device in self.available_devices.devices:
                        # Test if the user clicked on a available device on the side of the GUI (kind of 'library' of available devices)
                        if device.hit_test(x, y):
                            device_class = device.device_class
                            # Add a "moving" instance of the selected device
                            similar_dev_counter = 1
                            for room_device in self.room_devices:
                                if room_device.device_class.lower() in device_class.lower():
                                # if room_device.device_type == device_type:
                                    similar_dev_counter += 1
                            # Create a moving_device attribute
                            self.moving_device = DeviceWidget(x, y, self.batch, device.file_ON, device.file_OFF, group=self.foreground, device_type=device.device_type, device_class=device_class, device_number=str(similar_dev_counter))
                            return
                    for room_device in self.room_devices:
                        # Test if user clicked on a instanciated Room device to ajust its position in the Room
                        if room_device.hit_test(x, y):
                            # Repositioning of the room device object by a moving device object
                            self.moving_device = room_device
                            self.moving_device.update_position(new_x = x, new_y = y)
                for button in self.buttons:
                    if button.widget.hit_test(x, y):
                        button.widget.sprite.opacity = OPACITY_CLICKED
                        button.activate(self)
        if button == pyglet.window.mouse.RIGHT:
            # RIGHT click + CTRL : Remove device from group address
            if modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if self.room.detach(room_device.in_room_device.device, self.input_label.text):
                            self.update_config_ga(room_device, self.input_label.text, detach=True)
                        self.display_devices_list()
            # RIGHT click
            else:
                for button in self.buttons:
                    if button.widget.hit_test(x, y) and isinstance(button, ButtonDefault):
                        self.reload_simulation(empty_config=True)
                        #button.empty_config(self)


    def on_mouse_release(self, x, y, button, modifiers):
        ''' Called when a mouse button is released (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is released'''
        # The LEFT button is used to select and manage devices  (position, group addresses, activation,...)
        if button == pyglet.window.mouse.LEFT:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                if hasattr(self, 'dimmer_being_set'):
                    if not self.dimmer_being_set.being_set: # if mouse was not dragged but only pressed (to turn ON/OFF dimmer)
                        self.dimmer_being_set.room_device_widget.in_room_device.device.user_input(switch_state=True)
                    else: # if mouse was dragged while pressing left button to set dimmer ratio
                        new_ratio = dimmer_ratio_from_mouse_pos(y, self.dimmer_being_set.center_y)
                        self.dimmer_being_set.room_device_widget.in_room_device.device.user_input(state_ratio=new_ratio, keep_on=True)
                    self.switch_sprite()
                    self.dimmer_being_set.delete() # will change ratio and color of it
                    delattr(self, 'dimmer_being_set')

            # If there is a moving device, the release of LEFT button is to place the devce in the room or remove it from the GUI (release outside of the room)
            elif hasattr(self, 'moving_device'):
                # Place the device in the Room if user drop it in the room widget
                if self.room_widget.hit_test(x, y):
                    pos_x, pos_y = x, y
                    # Test if the moving device is not already in the room (if user is not simply changing the position of a room device)
                    if self.moving_device not in self.room_devices:
                        self.add_device_to_simulation(self.room, pos_x, pos_y)
                    else:
                        if not (modifiers & pyglet.window.key.MOD_SHIFT):
                            self.update_device_location(pos_x, pos_y)
                    self.display_devices_list()
                    delattr(self, 'moving_device')
                # If user drop moving device out of room widget
                else:
                    if self.moving_device in self.room_devices:
                        self.replace_moving_device_in_room(x, y)
                    else:
                        self.moving_device.delete()
                    delattr(self, 'moving_device')
            for button in self.buttons:
                if button.widget.hit_test(x, y):
                    if button == self.button_pause:
                        button.update_image()
                button.widget.sprite.opacity = OPACITY_DEFAULT

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        ''' Called when the mouse is dragged:
            Drag device accross the GUI if there is a moving device defined'''
        if (modifiers & pyglet.window.key.MOD_SHIFT):
            if hasattr(self, 'dimmer_being_set'):
                if not self.dimmer_being_set.being_set:
                    self.dimmer_being_set.start_setting_dimmer(self.batch, self.foreground) # Initialize ratio label
                new_ratio = dimmer_ratio_from_mouse_pos(y, self.dimmer_being_set.center_y)
                self.dimmer_being_set.update_ratio(new_ratio)

        else: # if SHIFT pressed, the user only want to activate the device and not move it
            if buttons & pyglet.window.mouse.LEFT:
                if hasattr(self, 'moving_device'):
                    self.moving_device.update_position(new_x = x, new_y = y) # - (self.moving_device.width//2)   - (self.moving_device.length//2)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        ''' Called when the mouse is scrolled:
            scroll in room devices list '''
        if self.devicelist_widget.hit_test(x, y):
            self.display_devices_list(scroll=np.sign(scroll_y))



def update_window(dt, window, speed_factor, start_time): # cannot be a class method because first argument must be dt, and thus cannot be self.
    ''' Functions called with the pyglet scheduler
        Update the Simulation Time displayed and should update the world state'''
    sim_time = str(timedelta(seconds=round(speed_factor*(time() - start_time), 2))) # 2 decimals
    window.simtime_widget.simtime_valuelabel.text = f"{sim_time[:-5]}" #update simulation time  {timedelta(seconds=sim_time)}
    print(f"doing simtime update at {sim_time[:-5]} \n")


# if __name__ == '__main__':
#     speed_factor = 180
#     window = GUIWindow()
#     start_time = time()
#     pyglet.clock.schedule_interval(update_window, 1, window, speed_factor, start_time)
#     pyglet.app.run()
#
#     print("The simulation has been ended.\n")

