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
    def __init__(self, config_path, default_config_path, empty_config_path, saved_config_path, rooms=None):
        super(GUIWindow, self).__init__(WIN_WIDTH, WIN_LENGTH, caption='KNX Simulation Window', resizable=False)
        from system import configure_system_from_file
        # Configure the window size
        self.__width = WIN_WIDTH
        self.__length = WIN_LENGTH
        #self.set_minimum_size(1200, 1000) #minimum window size
        #self.set_minimum_size(1300, 1100) #minimum window size
        #self.push_handlers(on_resize=self.local_on_resize) #to avoid redefining the on_resize handler
        # Configure batch of modules to draw on events (mouse click, moving,...)
        self.__batch = pyglet.graphics.Batch()
        # Create multiple layers to superpose the graphical elements
        self.__background = pyglet.graphics.OrderedGroup(0)
        self.__middlebackground = pyglet.graphics.OrderedGroup(1)
        self.__middleground = pyglet.graphics.OrderedGroup(2)
        self.__foreground = pyglet.graphics.OrderedGroup(3)
        #document = pyglet.text.document.UnformattedDocument()
        # STore the initial configuration file path if the user wants to reload the simulation
        self.__CONFIG_PATH = config_path
        self.__DEFAULT_CONFIG_PATH = default_config_path
        self.__EMPTY_CONFIG_PATH = empty_config_path
        self.SAVED_CONFIG_PATH = saved_config_path + "saved_config_" # used by Save Button
        # Room object to represent the KNX System
        try:
            self.room = rooms[0]
        except TypeError:
            logging.info("No room is defined, the rooms default characteristics are applied")
            self.room = configure_system_from_file(self.__DEFAULT_CONFIG_PATH)

        # Array to store the devices added to the room (by dragging them for instance)
        self.__room_devices = [] # DeviceWidget instances 
        self.__devices_scroll = 0
        # Default individual addresses when adding devices during simulation
        self.__individual_address_default = [0,0,100] # we suppose no more than 99 devices on area0/line0, and no more than 155 new manually added devices
        # Initialize the room widget to draw in the window
        self.__room_widget = RoomWidget(ROOM_WIDTH, ROOM_LENGTH, self.__batch, group_bg=self.__background, group_mg=self.__middlebackground, label=self.room.name, label_group=self.__middleground)
        # Array to store labels to display in room devices list
        self.__room_devices_labels = []
        # Array to store brightnesses & temperature in the room
        self.__room_brightness_labels = []
        self.__room_brightness_levels = []
        self.__room_temperature_labels = []
        self.__room_temperature_levels = []
        self.__room_airquality_labels = []
        self.__room_airquality_levels = []

        # Initialize the Available devices widgets to draw them on the left size, s that a user can drag them in the room
        self.__available_devices = AvailableDevices(self.__batch, group_dev=self.__foreground, group_box=self.__background)
        # Define the position of the text elements and the text box to interact with the user
        self.__commandlabel_pos = (self.__width-WIN_BORDER, 96*(self.__length//100))
        self.__simlabel_pos = (WIN_WIDTH-ROOM_WIDTH-WIN_BORDER-ROOM_BORDER, 95*(self.__length//100))  #2*(self.__width//100)
        self.__textbox_pos = (80*(self.__width//100), 91*(self.__length//100))
        self.__devicelist_pos = (WIN_BORDER, 50*(self.__length//100))  #2*(self.__width//100)
        self.__brightness_label_pos = (WIN_BORDER, 95*(self.__length//100)) #2*(self.__width//100)
        self.__temperature_label_pos = (WIN_BORDER, 89*(self.__length//100))  #2*(self.__width//100)
        self.__airsensor_label_pos = (WIN_BORDER, 83*(self.__length//100))
        # Define the position of the buttons to interact with the user
        self.__button_pause_pos = (INITIAL_POSITION_BUTTON*(self.__width//100), 93*(self.__length//100)) # 
        self.__button_stop_pos = ((OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.__width//100), 93*(self.__length//100))
        self.__button_reload_pos = ((2*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.__width//100), 93*(self.__length//100))
        self.__button_save_pos = ((3*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.__width//100), 93*(self.__length//100))
        self.__button_default_pos = ((4*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(self.__width//100), 93*(self.__length//100))
        # Create the text labels and the textbox to display to the user
        self.__command_label = pyglet.text.Label('Enter your command',font_name=FONT_SYSTEM_TITLE, font_size=20, bold=True,
                                    x=self.__commandlabel_pos[0], y=self.__commandlabel_pos[1],
                                    anchor_x='right', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
        self.simtime_widget = SimTimeWidget(self.__simlabel_pos[0], self.__simlabel_pos[1], self.__batch, group_label=self.__foreground, group_box=self.__background)
        self.__text_box = pyglet.shapes.Rectangle(self.__textbox_pos[0], self.__textbox_pos[1], self.__width-self.__textbox_pos[0]-WIN_BORDER, 40, color=(255, 255, 255),
                                    batch=self.__batch, group=self.__background)
        # Initialize the text box label to display the user input in the textbox
        self.__input_label = pyglet.text.Label("",
                                    font_name=FONT_USER_INPUT, font_size=15,
                                    color=(10, 10, 10, 255),
                                    x=(self.__text_box.x+10), y=(self.__text_box.y+20),
                                    anchor_x='left', anchor_y='center',
                                    batch=self.__batch, group=self.__foreground)
        # Initialize the list of devices in the room
        self.__devicelist_widget = DeviceListWidget(self.__devicelist_pos[0], self.__devicelist_pos[1], self.__batch, group_label=self.__foreground, group_box=self.__background)
        self.__sensors_box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, OFFSET_SENSOR_LEVELS_BOX_Y, SENSOR_LEVELS_BOX_WIDTH, WIN_LENGTH - OFFSET_SENSOR_LEVELS_BOX_Y- WIN_BORDER/2, border=WIN_BORDER/2,
                                    color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                    batch=self.__batch, group=self.__background)
        self.__brightness_label = pyglet.text.Label("Brightness (lumens):",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.__brightness_label_pos[0], y=self.__brightness_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
        self.__temperature_label = pyglet.text.Label("Temperature (°C):",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.__temperature_label_pos[0], y=self.__temperature_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
        self.__airquality_label = pyglet.text.Label("Air quality - T(°C) / CO2(ppm) / RH(%):",  #350-1,000 ppm, 
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.__airsensor_label_pos[0], y=self.__airsensor_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
        # GUI buttons
        self.__buttons = []
        # Reload Button to re-initialize the simulation
        self.__button_pause = ButtonPause(self.__button_pause_pos[0], self.__button_pause_pos[1], self.__batch, BUTTON_PAUSE_PATH, BUTTON_PLAY_PATH, group=self.__foreground)
        self.__buttons.append(self.__button_pause)
        self.__button_stop = ButtonStop(self.__button_stop_pos[0], self.__button_stop_pos[1], self.__batch, BUTTON_STOP_PATH, group=self.__foreground)
        self.__buttons.append(self.__button_stop)
        self.__button_reload = ButtonReload(self.__button_reload_pos[0], self.__button_reload_pos[1], self.__batch, BUTTON_RELOAD_PATH, group=self.__foreground)
        self.__buttons.append(self.__button_reload)
        self.__button_save = ButtonSave(self.__button_save_pos[0], self.__button_save_pos[1], self.__batch, BUTTON_SAVE_PATH, group=self.__foreground)
        self.__buttons.append(self.__button_save)
        self.__button_default = ButtonDefault(self.__button_default_pos[0], self.__button_default_pos[1], self.__batch, BUTTON_DEFAULT_PATH, group=self.__foreground)
        self.__buttons.append(self.__button_default)

## Private methods ##
### Display methods ###
    def __display_devices_list(self, scroll=0):
        """ Re-Initialisation of the room devices list """
        for room_device_label in self.__room_devices_labels:
            room_device_label.delete()
        self.__room_devices_labels = []
        room_devices_counter = 0
        list_x = self.__devicelist_widget.deviceslist_title.x
        list_y = self.__devicelist_widget.deviceslist_title.y - OFFSET_DEVICESLIST_TITLE
        # To scroll in devices list
        self.__devices_scroll = max(0, self.__devices_scroll+scroll)
        # max scroll to limit how deep a user can go down in the list, we keep MAX_SIZE_DEVICE_LIST devices visible at least
        max_scroll = len(self.__room_devices) - MAX_SIZE_DEVICE_LIST
        if max_scroll > 0: # if enough devices 
            self.__devices_scroll = int(min(self.__devices_scroll, max_scroll))
        # Display the current room devices name in list
        for room_device in self.__room_devices[self.__devices_scroll:]:
            room_dev_x = list_x
            room_dev_y = list_y - room_devices_counter*(OFFSET_LIST_DEVICE) # display device name below main label
            room_dev_ia_y = room_dev_y - OFFSET_INDIVIDUAL_ADDR_LABEL 
            ia_label = room_device.in_room_device.device.individual_addr.ia_str
            room_dev_gas = room_device.in_room_device.device.group_addresses
            ga_text = ' -- (' + ', '.join([str(ga) for ga in room_dev_gas]) + ')'
            label_text = room_device.label.text + ga_text
            room_device_label = pyglet.text.Label(label_text,
                                font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_DEVICESLIST,
                                x=room_dev_x, y=room_dev_y,
                                anchor_x='left', anchor_y='bottom',
                                batch=self.__batch, group=self.__foreground)
            room_device_ia_label = pyglet.text.Label(ia_label,
                                font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_INDIVIDUAL_ADDR,
                                x=room_dev_x, y=room_dev_ia_y,
                                anchor_x='left', anchor_y='bottom',
                                batch=self.__batch, group=self.__foreground)
            self.__room_devices_labels.append(room_device_label) 
            self.__room_devices_labels.append(room_device_ia_label) 
            room_devices_counter += 1
        self.__devicelist_widget.update_box(new_length=room_devices_counter*OFFSET_LIST_DEVICE)

    def __display_brightness_labels(self):
        """ Re-Initialisation of the room brightness sensor labels """
        for room_brightness_label in self.__room_brightness_labels:
            room_brightness_label.delete()
        self.__room_brightness_labels = []
        room_brightness_counter = 0
        bright_x = self.__brightness_label.x
        bright_y = self.__brightness_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.__room_devices:
            if 'bright' in room_device.label.text.lower():
                room_bright_x = bright_x + room_brightness_counter*OFFSET_SENSOR_LEVELS
                room_bright_y = bright_y
                room_brightness_counter += 1
                room_brightness_label = pyglet.text.Label('bright'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LABEL,
                                    x=room_bright_x, y=room_bright_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
                self.__room_brightness_labels.append(room_brightness_label)

    def __display_temperature_labels(self):
        """ Re-Initialisation of the room temperature sensor labels """
        for room_temperature_label in self.__room_temperature_labels:
            room_temperature_label.delete()
        self.__room_temperature_labels = []
        room_temperature_counter = 0
        temp_x = self.__temperature_label.x
        temp_y = self.__temperature_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.__room_devices:
            if 'thermometer' in room_device.label.text.lower():
                room_temp_x = temp_x + room_temperature_counter*OFFSET_SENSOR_LEVELS
                room_temp_y = temp_y
                room_temperature_counter += 1
                room_temperature_label = pyglet.text.Label('thermo'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LABEL,
                                    x=room_temp_x, y=room_temp_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
                self.__room_temperature_labels.append(room_temperature_label)
    
    def __display_airquality_labels(self):
        """ Re-Initialisation of the room air quality sensor labels """
        for room_airquality_label in self.__room_airquality_labels:
            room_airquality_label.delete()
        self.__room_airquality_labels = []
        room_airquality_counter = 0
        air_x = self.__airquality_label.x
        air_y = self.__airquality_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.__room_devices:
            if 'airsensor' in room_device.label.text.lower():
                room_air_x = air_x + room_airquality_counter*OFFSET_SENSOR_LEVELS
                room_air_y = air_y
                room_airquality_counter += 1
                room_airquality_label = pyglet.text.Label('airsens'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LABEL,
                                    x=room_air_x, y=room_air_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
                self.__room_airquality_labels.append(room_airquality_label)

    
    def __display_airquality_levels(self, airsensor_dict):
        """ Display levels of air quality (T, H, CO2) for corresponding labels (sensors) """
        for airsensor in airsensor_dict: # airsensor are the keys
            temp = hum = co2 = None
            airquality_level_text = ''
            room_airsensor_counter = 0
            for room_airquality_label in self.__room_airquality_labels:
                if airsensor[-1] == room_airquality_label.text[-1]:
                    air_level_x = room_airquality_label.x
                    air_level_y = room_airquality_label.y - OFFSET_SENSOR_TITLE
                    if "temperature" in airsensor_dict[airsensor]:
                        temp = airsensor_dict[airsensor]["temperature"]
                        airquality_level_text += str(temp)+'/'
                    else:
                        airquality_level_text += '-/'
                    if "co2level" in airsensor_dict[airsensor]:
                        co2 = airsensor_dict[airsensor]["co2level"]
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
                                    batch=self.__batch, group=self.__foreground)
                    self.__room_airquality_levels.append(room_airquality_level)
                room_airsensor_counter += 1


    def __display_brightness_level(self, bright_name, brightness):
        """ Display levels of brightness for corresponding labels (sensors) """
        room_brightness_counter = 0
        for room_brightness_label in self.__room_brightness_labels:
            if bright_name[-1] == room_brightness_label.text[-1]: #check only the digit
                bright_level_x = room_brightness_label.x #+ room_brightness_counter*OFFSET_SENSOR_LEVELS
                bright_level_y = room_brightness_label.y - OFFSET_SENSOR_TITLE
                bright_level_text = str(brightness) # + ' lm'
                room_brightness_level = pyglet.text.Label(bright_level_text,
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LEVEL,
                                    x=bright_level_x, y=bright_level_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
                self.__room_brightness_levels.append(room_brightness_level)
            room_brightness_counter +=1

    def __display_temperature_level(self, temp_name, temperature):
        """ Display levels of temperature for corresponding labels (sensors) """
        room_temperature_counter = 0
        for room_temperature_label in self.__room_temperature_labels:
            if temp_name[-1] == room_temperature_label.text[-1]: #check only the digit
                temp_level_x = room_temperature_label.x #+ room_brightness_counter*OFFSET_SENSOR_LEVELS
                temp_level_y = room_temperature_label.y - OFFSET_SENSOR_TITLE
                temp_level_text = str(temperature) # + ' lm'
                room_temperature_level = pyglet.text.Label(temp_level_text,
                                    font_name=FONT_SYSTEM_INFO, font_size=FONT_SIZE_SENSOR_LEVEL,
                                    x=temp_level_x, y=temp_level_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.__batch, group=self.__foreground)
                self.__room_temperature_levels.append(room_temperature_level)
            room_temperature_counter +=1

    def __switch_sprite(self):
        """ Switch devices' sprite (image) if their state has changed"""
        for room_device in self.__room_devices:
            try:
                if room_device.sprite_state != room_device.in_room_device.device.state: # sprite representation is not the same as real state
                    room_device.sprite_state = not room_device.sprite_state
                    room_device.sprite.delete()
                    if room_device.sprite_state: # device turned ON
                        room_device.sprite = pyglet.sprite.Sprite(room_device.img_ON, x=room_device.origin_x, y=room_device.origin_y, batch=self.__batch, group=self.__foreground)
                    else: # device turned OFF
                        room_device.sprite = pyglet.sprite.Sprite(room_device.img_OFF, x=room_device.origin_x, y=room_device.origin_y, batch=self.__batch, group=self.__foreground)
                if room_device.sprite_state and room_device.sprite_state_ratio != room_device.in_room_device.device.state_ratio: # dimmmer changed state_ratio of e.g. a light that is ON
                    room_device.sprite_state_ratio = room_device.in_room_device.device.state_ratio
                    new_opacity = OPACITY_MIN + (OPACITY_DEFAULT-OPACITY_MIN) * room_device.sprite_state_ratio/100
                    room_device.sprite.opacity = new_opacity
            except AttributeError: #if no state attribute (e.g. sensor)
                pass
    
### Devices and configuration file management methods ###
    def __add_device_to_simulation(self, room, pos_x, pos_y):
        """ Add a device to the system after user added it via the GUI"""
        from system.tools import IndividualAddress
        new_device_class = self.__moving_device.device_class
        area, line, dev_number = [self.__individual_address_default[i] for i in range(3)]#, self.__individual_address_default[1], self.__individual_address_default[2]
        individual_address = IndividualAddress(area, line, dev_number)
        new_refid = "M-O_X" + str(self.__individual_address_default[2])
        self.__individual_address_default[2] += 1
        if self.__individual_address_default[2] > 255:
            self.__individual_address_default[2] = 0
            self.__individual_address_default[1] += 1
            if self.__individual_address_default[1] > 15:
                self.__individual_address_default[1] = 0
                self.__individual_address_default[0] = max(self.__individual_address_default[0]+1, 15)
        similar_devices_counter = 1
        for device in self.__room_devices:
            if new_device_class.lower() in device.device_class.lower():
                similar_devices_counter +=1
        new_device_name = new_device_class.lower()+str(similar_devices_counter)
        # Creation of the device object
        new_status = "enabled"
        device = DEV_CLASSES[new_device_class](new_device_name, new_refid, individual_address, new_status)
        loc_x, loc_y = gui_pos_to_system_loc(pos_x, pos_y, self.__room_width_ratio, self.__room_length_ratio,
                                            self.__room_widget.origin_x, self.__room_widget.origin_y)
        loc_z = 1 # 1 is default height z
        self.__moving_device.in_room_device = room.add_device(device, loc_x, loc_y, loc_z)
        self.__moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
        self.__room_devices.append(self.__moving_device)
        self.__add_device_to_config(new_device_name, new_device_class, new_refid, str(area), str(line), str(dev_number), new_status, loc_x, loc_y, loc_z, room.name)
        self.__display_brightness_labels()
        self.__display_temperature_labels()
        self.__display_airquality_labels()


    def __update_device_location(self, pos_x, pos_y):
        """ Update the device location in the GUI"""
        loc_x, loc_y = gui_pos_to_system_loc(pos_x, pos_y, self.__room_width_ratio, self.__room_width_ratio, self.__room_widget.origin_x, self.__room_widget.origin_y)
        self.__moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
        self.__update_config_loc(loc_x, loc_y, self.room.name)
    

    def __replace_moving_device_in_room(self, x, y):
        """ Replace the device at the closest point in the room if user drops it outside the GUI room widget"""
        from system import Location
        x_min = self.__room_widget.origin_x #+ self.__moving_device.width//2
        x_max = self.__room_widget.origin_x + self.__room_widget.width #- self.__moving_device.width//2
        y_min = self.__room_widget.origin_y #+ self.__moving_device.length//2
        y_max = self.__room_widget.origin_y + self.__room_widget.length #- self.__moving_device.length//2

        new_x = (x_min if x<x_min else x)
        new_x = (x_max if x_max<new_x else new_x)
        new_y = (y_min if y<y_min else y)
        new_y = (y_max if y_max<new_y else new_y)
        loc_x, loc_y = gui_pos_to_system_loc(new_x, new_y, self.__room_width_ratio, self.__room_width_ratio, self.__room_widget.origin_x, self.__room_widget.origin_y)
        self.__moving_device.update_position(new_x, new_y, loc_x, loc_y, update_loc = True)
        self.__update_config_loc(loc_x, loc_y, self.room.name)


    def __add_device_to_config(self,dev_name, dev_class, dev_refid, area, line, dev_number, dev_status, loc_x, loc_y, loc_z, room_name):
        """ Update the configuration dict respresenting the system with new devices"""
        # KNX config
        knx_config = self.system_config_dict["knx"]
        area_key = 'area' + area
        line_key = 'line' + line
        knx_loc = '.'.join([area, line, dev_number])
        line_devices = knx_config[area_key][line_key]["devices"]
        line_devices[dev_name] = {"class":dev_class, "refid":dev_refid, "knx_location":knx_loc, "status":dev_status}
        # World config
        world_config = self.system_config_dict["world"]
        for room in world_config["rooms"]:
            if world_config["rooms"][room]["name"] == room_name:
                world_config["rooms"][room]["room_devices"][dev_name] = [loc_x, loc_y, loc_z]

    def __update_config_loc(self, loc_x, loc_y, room_name:str):
        """ Update the configuration file with new devices location """
        loc_z = 1
        dev_name = self.__moving_device.in_room_device.device.name
        world_config = self.system_config_dict["world"]
        for room in world_config["rooms"]:
            if world_config["rooms"][room]["name"] == room_name:
                world_config["rooms"][room]["room_devices"][dev_name] = [loc_x, loc_y, loc_z]
    
    def __update_config_ga(self, room_device, group_address:str, detach = False):
        """ Update the configuration file with new group address and/or new device members """
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

    
## Public methods ##
    def initialize_system(self, save_config=False, config_path=None, system_dt=1):
        """ Initialize gui system from room configuration """
        from devices import Button, LED, Brightness, Dimmer, Heater, AC, Thermometer, AirSensor # ,PresenceSensor
        self.room.window = self # same for the GUi window object, but to room1 object
        if save_config: # stor the saved config path only at first call, not when user reload the system
            # Save the system also when reloading to default or empty system
            # We save the system dictionary from config file to update it as the user add devices
            if config_path is None: # If system initialisation, we take the normal config path
                config_path = self.__CONFIG_PATH
                self.__SYSTEM_DT = system_dt # we store the system dt giuven from simulator
            # else, teh congif path would either be default or empty config
            with open(config_path, "r") as config_file:
                self.system_config_dict = json.load(config_file)
        pyglet.clock.schedule_interval(self.room.update_world, interval=system_dt, gui_mode=True) # update every 1seconds, corresponding to 1 * speed_factor real seconds
        # ratio to translate room physical (simulated) size in pixels to place correctly devices
        self.__room_width_ratio = ROOM_WIDTH / self.room.width
        self.__room_length_ratio = ROOM_LENGTH / self.room.length

        print(" ------- Initialization of the KNX System's GUI representation ------- ")
        for in_room_device in self.room.devices:
            # Supported instances: Button, Dimmer, LED, Heater, AC, Brightness, Thermometer, AirSensor Humidity? CO2?
            gui_device = getattr(self.__available_devices, in_room_device.device.class_name.lower())
            pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.__room_width_ratio, self.__room_length_ratio, self.__room_widget.origin_x, self.__room_widget.origin_y)
            print(f"{in_room_device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
            device_widget = DeviceWidget(pos_x, pos_y, self.__batch, gui_device.file_ON, gui_device.file_OFF, group=self.__foreground, device_type='sensor', device_class=in_room_device.name[:-1], device_number=in_room_device.name[-1])
            device_widget.in_room_device = in_room_device
            self.__room_devices.append(device_widget)
        self.__display_devices_list()
        self.__display_brightness_labels()
        self.__display_temperature_labels()
        self.__display_airquality_labels()
    

    def update_sensors(self, brightness_levels, temperature_levels, humidity_levels, co2_levels):
        """ Re-Initialisation of the room sensors list with new values"""
        for room_brightness_level in self.__room_brightness_levels:
            room_brightness_level.delete()
        self.__room_brightness_levels = []
        for room_temperature_level in self.__room_temperature_levels:
            room_temperature_level.delete()
        self.__room_temperature_levels = []
        for room_airquality_level in self.__room_airquality_levels:
            room_airquality_level.delete()
        self.__room_airquality_levels = []
        airsensor_dict = {}

        for bright in brightness_levels:
            bright_name, brightness = bright[0], round(bright[1],1)
            self.__display_brightness_level(bright_name, brightness)
        for temp in temperature_levels:
            temp_name, temperature = temp[0], round(temp[1],2)
            if 'air' in temp_name:
                try:
                    airsensor_dict[temp_name]["temperature"] = temperature
                except KeyError:
                    airsensor_dict[temp_name] = {}
                    airsensor_dict[temp_name]["temperature"] = temperature
            self.__display_temperature_level(temp_name, temperature)
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
            co2_name, co2level = co2[0], co2[1]
            if 'air' in co2_name:
                try:
                    airsensor_dict[co2_name]["co2level"] = co2level
                except KeyError:
                    airsensor_dict[co2_name] = {}
                    airsensor_dict[co2_name]["co2level"] = co2level
        # Display all air quality sensors at once
        if len(airsensor_dict) > 0:
            self.__display_airquality_levels(airsensor_dict)


    def reload_simulation(self, default_config = False, empty_config = False):
        """ Reload the simulation from initial configuration file """
        
        # Remove the update function from schedule
        pyglet.clock.unschedule(self.room.update_world)
        # Re-Initialisation of the room devices list
        for room_device in self.__room_devices:
            room_device.delete()
        self.__room_devices = []
        # Re-Initialisation of the room brightness labels list
        for room_brightness_label in self.__room_brightness_labels:
            room_brightness_label.delete()
        self.__room_brightness_labels = []
        # Re-Initialisation of the room device labels list
        for room_device_label in self.__room_devices_labels:
            room_device_label.delete()
        self.__room_devices_labels = []
        # Re-initialization of Pause button
        self.__button_pause.update_image(reload=True)
        # Re configuration of the room and simulation time
        if default_config:
            config_path = self.__DEFAULT_CONFIG_PATH
        elif empty_config:
            config_path = self.__EMPTY_CONFIG_PATH
        else:
            config_path = self.__CONFIG_PATH
        self.room = configure_system_from_file(config_path)[0] # only one room for now
        self.room.world.time.start_time = time()
        self.initialize_system(save_config=True, config_path = config_path, system_dt=self.__SYSTEM_DT)


    def pause_simulation(self):
        """ Method called when pressing pause button, stores the time of the pause to resume with the correct simtime"""
        self.room.simulation_status = not self.room.simulation_status
        if not self.room.simulation_status:
            logging.info("The simulation is paused")
            self.room.world.time.pause_time = time() # save current time to update start_time when
        else:
            logging.info("The simulation is resumed")
            paused_time = time() - self.room.world.time.pause_time
            self.room.world.time.start_time += paused_time
            delattr(self.room.world.time, 'pause_time')


## Pyglet 'on-event' methods ##
    def on_draw(self):
        ''' Called when the window is redrawn:
            Draw all the elements added to the batch in the window on each event (mouse click, drag,...)'''
        self.clear()
        self.__batch.draw()

    def on_text(self, text):
        ''' Called when the user press a keyboard symbol (all keys except modifiers):
            Add the text input by the user to the text label displayed in the text box '''
        self.__input_label.text += text

### Key events ###
    def on_key_press(self, symbol, modifiers):
        # from system.tools import configure_system_from_file
        ''' Called when any key is pressed:
            Define special action to modify text, save input text or end the simulation'''
        # BACKSPACE to erase a character from the user input textbox
        if symbol == pyglet.window.key.BACKSPACE:
            self.__input_label.text = self.__input_label.text[:-1] # Remove last character
        # ENTER to parse the command input by the user and erase it from the text box
        elif symbol == pyglet.window.key.ENTER:
            from system import user_command_parser
            user_command_parser(self.__input_label.text, self.room)
            self.__switch_sprite()
            self.__input_label.text = ''
        # CTRL-ESCAPE to end the simulation
        elif symbol == pyglet.window.key.ESCAPE:
            if modifiers and pyglet.window.key.MOD_CTRL:
                pyglet.app.exit()
        # CTRL-P to Pause/Play simulation
        elif symbol == pyglet.window.key.P:
            if modifiers and pyglet.window.key.MOD_CTRL:
                self.__button_pause.activate(self)
                self.__button_pause.update_image()
        # CTRL-R to reload simulation from start
        elif symbol == pyglet.window.key.R:
            if modifiers and pyglet.window.key.MOD_CTRL:
                self.reload_simulation()

    def on_key_release(self, symbol, modifiers): 
        ''' Called when a key is released:
            Define actions to take when specific keys are released'''
        # Cancel the Group Adddress linking if CRTL key is released 
        if symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL:
            for room_device in self.__room_devices:
                room_device.sprite.opacity = OPACITY_DEFAULT
            for button in self.__buttons:
                button.widget.sprite.opacity = OPACITY_DEFAULT
        # Cancel the Dimmer ratio setting if SHIFT key is released before the mouse is released to validate the value
        if symbol == pyglet.window.key.LSHIFT or symbol == pyglet.window.key.RSHIFT:
            if hasattr(self, 'dimmer_being_set'):
                self.__dimmer_being_set.delete()
                delattr(self, 'dimmer_being_set')

### Mouse events ###
    def on_mouse_press(self, x, y, button, modifiers):
        ''' Called when a mouse button is pressed (LEFT, RIGHT or MIDDLE):
            Defines multiple action to do when one of the mouse button is pressed'''
        if button == pyglet.window.mouse.LEFT:
            # LEFT click + SHIFT : activate functional module (e.g. turn button ON/OFF)
            if modifiers & pyglet.window.key.MOD_SHIFT:
                from devices.device_abstractions import FunctionalModule
                from devices.functional_modules import Button, Dimmer
                for room_device in self.__room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if isinstance(room_device.in_room_device.device, FunctionalModule):
                            if isinstance(room_device.in_room_device.device, Dimmer):
                                # Create an object to set the dimmer value, and validate by releasing the mouse with SHIFT pressed
                                self.__dimmer_being_set = DimmerSetterWidget(room_device)
                                return
                            elif isinstance(room_device.in_room_device.device, Button):
                                # user_input() will send the telegram with the appropriate payload on the bus
                                room_device.in_room_device.device.user_input() 
                                self.__switch_sprite()
            # LEFT click + CTRL : assign a group address to a device
            elif modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.__room_devices:
                    if room_device.hit_test(x, y):
                        if self.room.attach(room_device.in_room_device.device, self.__input_label.text): # Test if ga is correct
                            self.__update_config_ga(room_device, self.__input_label.text)
                        self.__display_devices_list()
            # LEFT click on device w/o modifiers : click on GUI Buttons or move/add devices in room
            else:
                if not hasattr(self, 'moving_device'): # NOTE: this test should never fail, as before clicking, no devices should be moving (attribute self.__moving_device deleted when mouse is released)
                    for device in self.__available_devices.devices:
                        if device.hit_test(x, y): 
                            device_class = device.device_class
                            # Cuunt number of exisiting devices with same class to assign a device number (e.g. led4)
                            similar_dev_counter = 1
                            for room_device in self.__room_devices:
                                if room_device.device_class.lower() in device_class.lower():
                                    similar_dev_counter += 1
                            # Create a moving_device attribute
                            self.__moving_device = DeviceWidget(x, y, self.__batch, device.file_ON, device.file_OFF, group=self.__foreground, device_type=device.device_type, device_class=device_class, device_number=str(similar_dev_counter))
                            return
                    for room_device in self.__room_devices:
                        if room_device.hit_test(x, y):
                            # Repositioning of the room device object by a moving device object to change its GUI position
                            self.__moving_device = room_device
                            self.__moving_device.update_position(new_x = x, new_y = y)
                # Check if user clicked on GUI Buttons
                for button in self.__buttons:
                    if button.widget.hit_test(x, y):
                        button.widget.sprite.opacity = OPACITY_CLICKED
                        button.activate(self)
        if button == pyglet.window.mouse.RIGHT:
            # RIGHT click + CTRL : Remove device from group address entered in the command box
            if modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.__room_devices:
                    if room_device.hit_test(x, y):
                        if self.room.detach(room_device.in_room_device.device, self.__input_label.text):
                            self.__update_config_ga(room_device, self.__input_label.text, detach=True)
                        self.__display_devices_list()
            # RIGHT click : Empty config from default Button NOTE or remove device?
            else:
                for button in self.__buttons:
                    if button.widget.hit_test(x, y) and isinstance(button, ButtonDefault):
                        self.reload_simulation(empty_config=True)

    def on_mouse_release(self, x, y, button, modifiers):
        ''' Called when a mouse button is released (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is released'''
        # The LEFT button is used to select and manage devices  (position, group addresses, activation,...)
        if button == pyglet.window.mouse.LEFT:
            # LEFT + SHIFT
            if modifiers & pyglet.window.key.MOD_SHIFT:
                if hasattr(self, 'dimmer_being_set'):
                    # If mouse was not dragged but only pressed (to turn ON/OFF dimmer)
                    if not self.__dimmer_being_set.being_set: 
                        self.__dimmer_being_set.room_device_widget.in_room_device.device.user_input(switch_state=True)
                    else: # If mouse was dragged while pressing left button to set dimmer ratio
                        new_ratio = dimmer_ratio_from_mouse_pos(y, self.__dimmer_being_set.center_y)
                        self.__dimmer_being_set.room_device_widget.in_room_device.device.user_input(state_ratio=new_ratio, keep_on=True)
                    self.__switch_sprite()
                    self.__dimmer_being_set.delete()
                    delattr(self, 'dimmer_being_set')

            # If there is a moving device, the release of LEFT button places the device in the room if dropped in it
            elif hasattr(self, 'moving_device'):
                if self.__room_widget.hit_test(x, y):
                    pos_x, pos_y = x, y
                    if self.__moving_device not in self.__room_devices:
                        self.__add_device_to_simulation(self.room, pos_x, pos_y)
                    else: # Device already in room, user was simply repositioning it
                        if not (modifiers & pyglet.window.key.MOD_SHIFT):
                            self.__update_device_location(pos_x, pos_y)
                    self.__display_devices_list()
                    delattr(self, 'moving_device')
                else: # If user drop moving device out of room widget
                    if self.__moving_device in self.__room_devices:
                        self.__replace_moving_device_in_room(x, y)
                    else:
                        self.__moving_device.delete()
                    delattr(self, 'moving_device')
            # Check if user released mouse on GUI Buttons
            for button in self.__buttons:
                # if button.widget.hit_test(x, y):
                if button == self.__button_pause and hasattr(self.__button_pause, 'clicked'):
                    button.update_image()
                    delattr(self.__button_pause, 'clicked')
                button.widget.sprite.opacity = OPACITY_DEFAULT

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        ''' Called when the mouse is dragged:
            Drag device accross the GUI if there is a moving device defined'''
        # Mouse drag + SHIFT : to set the dimmer ratio after clicking on it
        if (modifiers & pyglet.window.key.MOD_SHIFT):
            if hasattr(self, 'dimmer_being_set'):
                if not self.__dimmer_being_set.being_set:
                    # Initialize ratio label
                    self.__dimmer_being_set.start_setting_dimmer(self.__batch, self.__foreground) 
                new_ratio = dimmer_ratio_from_mouse_pos(y, self.__dimmer_being_set.center_y)
                self.__dimmer_being_set.update_ratio(new_ratio)
        # Mouse drag w/o modifiers to move 'moving' device 
        else: 
            if buttons & pyglet.window.mouse.LEFT:
                if hasattr(self, 'moving_device'):
                    self.__moving_device.update_position(new_x = x, new_y = y) 

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        ''' Called when the mouse is scrolled:
            scroll in room devices list '''
        if self.__devicelist_widget.hit_test(x, y):
            self.__display_devices_list(scroll=np.sign(scroll_y))


# Cannot be a class method because first argument must be dt, and thus cannot be self.
def update_window(dt, window, current_str_simulation_time): 
    ''' Functions called with the pyglet scheduler
        Update the Simulation Time displayed and should update the world state'''
    sim_time = current_str_simulation_time
    window.simtime_widget.simtime_valuelabel.text = f"{sim_time}" 
    print(f"doing simtime update at {sim_time[:-5]} \n")


# if __name__ == '__main__':
#     speed_factor = 180
#     window = GUIWindow()
#     start_time = time()
#     pyglet.clock.schedule_interval(update_window, 1, window, speed_factor, start_time)
#     pyglet.app.run()
#
#     print("The simulation has been ended.\n")

