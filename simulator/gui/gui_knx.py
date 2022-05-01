import pyglet
import copy
import logging
from time import time
from datetime import timedelta


from system.tools import configure_system_from_file, DEV_CLASSES


WIN_WIDTH = 1500
WIN_LENGTH = 1000
WIN_BORDER = 20  # Space between the window border and the Room wodget borders
ROOM_BORDER = 40 # margin to place devices at room boundaries
ROOM_WIDTH = 1000
ROOM_LENGTH = 800

OFFSET_TITLE = 30 # [y axis] Between Titles and Information (e.g. devices list, brightness/temperature values)
OFFSET_LIST_ELEMENT = 20 # [y axis] Between element in list (e.g. devices list in the room)
OFFSET_LABEL_DEVICE = 10 # [y axis] Between Device PNG and label
OFFSET_LABEL_BUTTON = 15 # [y axis] Between Button PNG and label
OFFSET_SENSOR_TITLE = 20 # [y axis] Between sensor label and level
OFFSET_SENSOR_LEVELS = 100 # [x axis] Horizontal distance between sensor elements

BLUENAVY_RGB = (1, 1, 122)
BLUEAIRFORCE_RGB = (75, 119, 190)
BLUEMARINER_RGB = (44, 130, 217)
BLUEMOODY_RGB = (132, 141, 223)
BLUESUMMERSKY_RGB = (30, 140, 211)
BLUEMINSK_RGB = (50, 50, 120)
BLUEJORDY_RGB = (137, 212, 244)
BLUEIRIS_RGB = (0, 176, 221)

FONT_BUTTON = 'Proxima Nova'
FONT_DEVICE = 'Lato'
FONT_SYSTEM_TITLE = 'Open Sans'
FONT_SYSTEM_INFO = 'Lato'
FONT_USER_INPUT = 'Roboto'

OPACITY_DEFAULT = 255
OPACITY_CLICKED = 150
OPACITY_ROOM = 180

BUTTON_RELOAD_PATH = 'png_simulator/reload.png'
BUTTON_PAUSE_PATH = 'png_simulator/pause.png'
BUTTON_PLAY_PATH = 'png_simulator/play.png'
BUTTON_STOP_PATH = 'png_simulator/stop.png'
BUTTON_DEFAULT_PATH = 'png_simulator/default_config.png'
DEVICE_LED_ON_PATH = 'png_simulator/lightbulb_ON.png'
DEVICE_LED_OFF_PATH = 'png_simulator/lightbulb_OFF.png'
DEVICE_SWITCH_ON_PATH = 'png_simulator/switch_ON.png'
DEVICE_SWITCH_OFF_PATH = 'png_simulator/switch_OFF.png'
DEVICE_BRIGHT_SENSOR_PATH = 'png_simulator/brightness_sensor.png'
DEVICE_THERMO_PATH = 'png_simulator/thermo_stable.png'
DEVICE_THERMO_COLD_PATH = 'png_simulator/thermo_cold.png'
DEVICE_THERMO_HOT_PATH = 'png_simulator/thermo_hot.png'
GREEN_PATH = 'png_simulator/green.png'




class DeviceWidget(object):
    def __init__(self, pos_x, pos_y, batch, img_file_ON, img_file_OFF, group, device_type, device_class, device_number, available_device=False):
        ''' docstring'''
        self.device_class = device_class
        self.label_name = self.device_class.lower()+device_number
        # self.name = label_name
        self.device_type = device_type
        self.in_motion = False # Temporary flag to inform that the device widget is being moved
        self.linking_group_address = False # Temporary flag to establish a group address connection between two devices
        self.sprite_state = False # devices turned ON/OFF
        # self.group_addresses = [] # will store the group addresses, can control the number e.g. for sensors
        self.file_ON = img_file_ON
        self.file_OFF = img_file_OFF #usefull to create a moving instance of the available devices
        self.pos_x, self.pos_y = pos_x, pos_y # Center of the image, simulated position on room
        self.img_ON, self.img_OFF = pyglet.image.load(self.file_ON), pyglet.image.load(self.file_OFF)
        self.width, self.length = self.img_ON.width, self.img_ON.height #ON/OFF images have the same width, height of image is called length in this program
        if available_device: # available devices for a manual import (displayed outside of the GUI)
            self.origin_x, self.origin_y = self.pos_x, self.pos_y
        else:
            self.origin_x, self.origin_y = self.pos_x - self.width//2, self.pos_y - self.length//2
        self.batch = batch
        self.group = group
        self.sprite = pyglet.sprite.Sprite(self.img_OFF, x=self.origin_x, y=self.origin_y, batch=self.batch, group=self.group) # x,y of sprite is bottom left of image
        self.label = pyglet.text.Label(self.label_name,
                                    font_name=FONT_DEVICE, font_size=10,
                                    x=(self.origin_x+self.width//2), y=(self.origin_y-OFFSET_LABEL_DEVICE),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.batch, group=self.group)

    def __eq__(self, device_to_compare):
        return self.label_name == device_to_compare.label_name


    def hit_test(self, x, y): # to check if mouse click is on a device image
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
            self.in_room_device.location.update_location(new_x=self.loc_x, new_y=self.loc_y)
            logging.info(f"Location of {self.label_name} is updated to {self.loc_x}, {self.loc_y}")

    def delete(self):
        self.sprite.delete()
        self.label.delete()


class ButtonReload(object):
    def __init__(self, x, y, batch, button_file, group):
        self.widget = ButtonWidget(x, y, batch, button_file, group=group, label_text='RELOAD')

    def activate(self, gui_window):
        gui_window.reload_simulation()

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

class ButtonDefault(object):
    def __init__(self, x, y, batch, button_file, group):
        self.default_file = button_file
        self.widget = ButtonWidget(x, y, batch, self.default_file, group=group, label_text='DEFAULT')

    def activate(self, gui_window):
        gui_window.reload_simulation(default_config = True)


class ButtonWidget(object):
    def __init__(self, x, y, batch, button_file, group, label_text=''):
        self.img = pyglet.image.load(button_file)
        self.width, self.length = self.img.width, self.img.height
        self.pos_x, self.pos_y = x, y
        self.batch, self.group = batch, group
        self.sprite = pyglet.sprite.Sprite(self.img, self.pos_x, self.pos_y, batch=self.batch, group=self.group)
        self.label = pyglet.text.Label(label_text,
                                    font_name=FONT_BUTTON, font_size=10,
                                    x=(self.pos_x+self.width//2), y=(self.pos_y-OFFSET_LABEL_BUTTON),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.batch, group=self.group)

    def hit_test(self, x, y): # to check if mouse click is on the Button widget
        return (self.pos_x < x < (self.pos_x + self.width) and
                self.pos_y < y < (self.pos_y + self.length))


class RoomWidget(object):
    def __init__(self, width, length, batch, group):
        # Coordinates to draw room rectangle shape
        self.origin_x_shape = WIN_WIDTH - width - WIN_BORDER - 2*ROOM_BORDER
        self.origin_y_shape = WIN_BORDER
        # Cordinates to represent the actual room dimensions (border is a margin for devices on boundaries)
        self.origin_x = WIN_WIDTH - width - WIN_BORDER - ROOM_BORDER
        self.origin_y = WIN_BORDER + ROOM_BORDER
        # Actual dimensions of the room, not the rectangle shape
        self.width = width
        self.length = length
        self.batch = batch
        self.shape = pyglet.shapes.BorderedRectangle(self.origin_x_shape, self.origin_y_shape, width+2*ROOM_BORDER, length+2*ROOM_BORDER, border=ROOM_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=self.batch, group=group)#, group = group
        self.shape.opacity = OPACITY_ROOM

        self.devices = []

    def hit_test(self, x, y): # to check if mouse click is on the Room widget
        return (self.origin_x < x < (self.origin_x + self.width) and
                self.origin_y < y < (self.origin_y + self.length))

    def add_device(self, device):
        self.devices.append(device)


class AvailableDevices(object): # library of devices availables, presented on the left side on the GUI
    def __init__(self, batch, group):
        self.in_motion = False
        self.devices = []
        self.led = DeviceWidget(100, 800, batch, DEVICE_LED_ON_PATH, DEVICE_LED_OFF_PATH, group, "actuator", "LED", '', available_device=True)
        self.devices.append(self.led)
        self.switch = DeviceWidget(30, 800, batch, DEVICE_SWITCH_ON_PATH, DEVICE_SWITCH_OFF_PATH, group, "functional_module", "Switch", '', available_device=True)
        self.devices.append(self.switch)
        self.brightness = DeviceWidget(170, 800, batch, DEVICE_BRIGHT_SENSOR_PATH, DEVICE_BRIGHT_SENSOR_PATH, group, "sensor", "Brightness", '', available_device=True)
        self.devices.append(self.brightness)
        self.thermometer = DeviceWidget(280, 800, batch, DEVICE_THERMO_COLD_PATH, DEVICE_THERMO_HOT_PATH, group, "sensor", "Thermometer", '', available_device=True)
        self.devices.append(self.thermometer)

## Make the difference between actuators, functional modules and sensors

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




class GUIWindow(pyglet.window.Window):
    ''' Class to define the GUI window, the widgets and text displayed in it and the functions reactign to the user actions (mouse click, input text,...) '''
    def __init__(self, config_path, default_config_path, rooms=None):
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
        self.foreground = pyglet.graphics.OrderedGroup(1)
        #document = pyglet.text.document.UnformattedDocument()
        # STore the initial configuration file path if the user wants to reload the simulation
        self.CONFIG_PATH = config_path
        self.DEFAULT_CONFIG_PATH = default_config_path
        # Room object to represent the KNX System
        try:
            self.room = rooms[0]
        except TypeError:
            logging.info("No room is defined, the rooms default characteristics are applied")
            self.room = configure_system_from_file(self.DEFAULT_CONFIG_PATH)

        # Array to store the devices added to the room (by dragging them for instance)
        self.room_devices = []
        # Default individual addresses when adding devices during simulation
        self.individual_address_default = [0,0,100]
        # Flag to set up group addresses
        self.linking_group_address = True
        # Initialize the room widget to draw in the window
        self.room_widget = RoomWidget(ROOM_WIDTH, ROOM_LENGTH, self.batch, group=self.background)
        # Array to store labels to display in room devices list
        self.room_devices_labels = []
        # Array to store brightnesses & temperature in the room
        self.room_brightness_labels = []
        self.room_brightness_levels = []
        self.room_temperature_labels = []
        self.room_temperature_levels = []
        # Initialize the Available devices widgets to draw them on the left size, s that a user can drag them in the room
        self.available_devices = AvailableDevices(self.batch, self.foreground)
        # Define the position of the text elements and the text box to interact with the user
        self.commandlabel_pos = (98*(self.width//100), 96*(self.length//100))
        self.simlabel_pos = (2*(self.width//100), 95*(self.length//100))
        self.textbox_pos = (85*(self.width//100), 91*(self.length//100))
        self.devicelist_pos = (2*(self.width//100), 40*(self.length//100))
        self.brightness_label_pos = (2*(self.width//100), 70*(self.length//100))
        self.brightness_level_pos = self.brightness_label_pos[0], self.brightness_label_pos[1]-20
        self.temperature_label_pos = (2*(self.width//100), 60*(self.length//100))
        self.temperature_level_pos = self.temperature_label_pos[0], self.temperature_label_pos[1]-20
        # Define the position of the buttons to interact with the user
        self.button_pause_pos = (45*(self.width//100), 93*(self.length//100)) # 
        self.button_stop_pos = (51*(self.width//100), 93*(self.length//100))
        self.button_reload_pos = (57*(self.width//100), 93*(self.length//100))
        self.button_default_pos = (63*(self.width//100), 93*(self.length//100))
        # Create the text labels and the textbox to display to the user
        self.command_label = pyglet.text.Label('Enter your command',
                                    font_name=FONT_SYSTEM_TITLE, font_size=20, bold=True,
                                    x=self.commandlabel_pos[0], y=self.commandlabel_pos[1],
                                    anchor_x='right', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
        self.simtime_label = pyglet.text.Label("Simulation Time: 0", # init the simulation time display
                                    font_name=FONT_SYSTEM_TITLE, font_size=20, bold=True,
                                    x=self.simlabel_pos[0], y=self.simlabel_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch, group=self.foreground)
        # self.simtime_label.bold = True
        self.text_box = pyglet.shapes.Rectangle(self.textbox_pos[0], self.textbox_pos[1], 200, 40, color=(255, 255, 255),
                                    batch=self.batch, group=self.background)
        # Initialize the text box label to display the user input in the textbox
        self.input_label = pyglet.text.Label("",
                                    font_name=FONT_USER_INPUT, font_size=15,
                                    color=(10, 10, 10, 255),
                                    x=(self.text_box.x+10), y=(self.text_box.y+20),
                                    anchor_x='left', anchor_y='center',
                                    batch=self.batch, group=self.foreground)
        # Initialize the list of devices in the room
        self.deviceslist_label = pyglet.text.Label("Devices in the Room:",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15, bold=True,
                                    x=self.devicelist_pos[0], y=self.devicelist_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch)

        self.brightness_label = pyglet.text.Label("Brightness in the Room (lumens):",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.brightness_label_pos[0], y=self.brightness_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch)
        self.temperature_label = pyglet.text.Label("Temperature in the Room (°C):",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15,  bold=True,
                                    x=self.temperature_label_pos[0], y=self.temperature_label_pos[1],
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch)

        # GUI buttons
        self.buttons = []
        # Reload Button to re-initialize the simulation
        self.button_reload = ButtonReload(self.button_reload_pos[0], self.button_reload_pos[1], self.batch, BUTTON_RELOAD_PATH, group=self.foreground)
        self.buttons.append(self.button_reload)
        self.button_pause = ButtonPause(self.button_pause_pos[0], self.button_pause_pos[1], self.batch, BUTTON_PAUSE_PATH, BUTTON_PLAY_PATH, group=self.foreground)
        self.buttons.append(self.button_pause)
        self.button_stop = ButtonStop(self.button_stop_pos[0], self.button_stop_pos[1], self.batch, BUTTON_STOP_PATH, group=self.foreground)
        self.buttons.append(self.button_stop)
        self.button_default = ButtonDefault(self.button_default_pos[0], self.button_default_pos[1], self.batch, BUTTON_DEFAULT_PATH, group=self.foreground)
        self.buttons.append(self.button_default)


    def initialize_system(self):
        from devices import Switch, LED, Brightness
        self.room.window = self # same for the GUi window object, but to room1 object
        pyglet.clock.schedule_interval(self.room.update_world, interval=1, gui_mode=True) # update every 1seconds, corresponding to 1 * speed_factor real seconds
        # ratio to translate room physical (simulated) size in pixels to place correctly devices
        self.room_width_ratio = ROOM_WIDTH / self.room.width
        self.room_length_ratio = ROOM_LENGTH / self.room.length

        # self.green_img = pyglet.image.load(GREEN_PATH)
        # self.green_sprite = pyglet.sprite.Sprite(self.green_img, x=80, y=0, batch=self.batch, group=self.foreground)

        for in_room_device in self.room.devices:
            device = in_room_device.device
            if isinstance(device, Brightness):
                brightness_sensor = self.available_devices.brightness
                # x, y = in_room_device.location.x, in_room_device.location.y
                # x = int(self.room_widget.x + self.room_width_ratio * x)
                # y = int(self.room_widget.y + self.room_length_ratio * y)
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, brightness_sensor.file_ON, brightness_sensor.file_OFF, group=self.foreground, device_type='sensor', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)

            if isinstance(device, Switch):
                switch = self.available_devices.switch
                # x, y = in_room_device.location.x, in_room_device.location.y
                # x = int(self.room_widget.x + self.room_width_ratio * x)
                # y = int(self.room_widget.y + self.room_length_ratio * y)
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, switch.file_ON, switch.file_OFF, group=self.foreground, device_type='functional_module', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)

            if isinstance(device, LED):
                led = self.available_devices.led
                # x, y = in_room_device.location.x, in_room_device.location.y
                # x = int(self.room_widget.x + self.room_width_ratio * x)
                # y = int(self.room_widget.y + self.room_length_ratio * y)
                pos_x, pos_y = system_loc_to_gui_pos(in_room_device.location.x, in_room_device.location.y, self.room_width_ratio, self.room_length_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                print(f"{device.name} ({in_room_device.location.x}, {in_room_device.location.y}) is at  {pos_x},{pos_y}")
                device_widget = DeviceWidget(pos_x, pos_y, self.batch, led.file_ON, led.file_OFF, group=self.foreground, device_type='actuator', device_class=device.name[:-1], device_number=device.name[-1])
                device_widget.in_room_device = in_room_device
                self.room_devices.append(device_widget)

        self.display_devices_list()
        self.display_brightness_labels()
        self.display_temperature_labels()


    def display_devices_list(self):
        # Re-Initialisation of the room devices list
        for room_device_label in self.room_devices_labels:
            room_device_label.delete()
        self.room_devices_labels = []
        room_devices_counter = 0
        list_x = self.deviceslist_label.x
        list_y = self.deviceslist_label.y - OFFSET_TITLE
        # Display the current room devices name in list
        for room_device in self.room_devices:
            room_dev_x = list_x
            room_dev_y = list_y - room_devices_counter*OFFSET_LIST_ELEMENT # display device name below main label
            room_dev_gas = room_device.in_room_device.device.group_addresses
            ga_text = '  --  (' + ', '.join([str(ga) for ga in room_dev_gas]) + ')'
            label_text = room_device.label.text + ga_text
            room_device_label = pyglet.text.Label(label_text,
                                font_name=FONT_SYSTEM_INFO, font_size=15,
                                x=room_dev_x, y=room_dev_y,
                                anchor_x='left', anchor_y='bottom',
                                batch=self.batch)
            self.room_devices_labels.append(room_device_label)
            room_devices_counter += 1

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
                room_temperature_label = pyglet.text.Label('Thermo'+room_device.label.text[-1],
                                    font_name=FONT_SYSTEM_INFO, font_size=15,
                                    x=room_temp_x, y=room_temp_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch)
                self.room_temperature_labels.append(room_temperature_label)

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
                                    font_name=FONT_SYSTEM_INFO, font_size=15,
                                    x=room_bright_x, y=room_bright_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch)
                self.room_brightness_labels.append(room_brightness_label)



    def display_brightness_levels(self, bright_name, brightness):
        room_brightness_counter = 0
        for room_brightness_label in self.room_brightness_labels:
            if bright_name[-1] == room_brightness_label.text[-1]: #check only the digit
                bright_level_x = room_brightness_label.x #+ room_brightness_counter*OFFSET_SENSOR_LEVELS
                bright_level_y = room_brightness_label.y - OFFSET_SENSOR_TITLE
                bright_level_label = str(brightness) # + ' lm'
                room_brightness_level = pyglet.text.Label(bright_level_label,
                                    font_name=FONT_SYSTEM_INFO, font_size=13,
                                    x=bright_level_x, y=bright_level_y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=self.batch)
                self.room_brightness_levels.append(room_brightness_level)
            room_brightness_counter +=1

    def update_sensors(self, brightness_levels, temperature_levels):
        # Re-Initialisation of the room sensors list
        for room_brightness_level in self.room_brightness_levels:
            room_brightness_level.delete()
        self.room_brightness_levels = []
        for room_temperature_level in self.room_temperature_levels:
            room_temperature_level.delete()
        self.room_temperature_levels = []
        for bright in brightness_levels:
            bright_name, brightness = bright[0], round(bright[1],1)
            self.display_brightness_levels(bright_name, brightness)

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
            except AttributeError: #if no state attribute (e.g. sensor)
                pass

    def reload_simulation(self, default_config = False):
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
        else:
            self.room = configure_system_from_file(self.CONFIG_PATH)[0] # only one room for now
        self.room.world.time.start_time = time()
        self.initialize_system()


    def group_address_format_check(self, text): ## TODO: verify if the group address entered in text box is correct
        from system.tools import GroupAddress
        ''' Verify that the group address entered by the user is correct (2, 3-levels or free) '''
        text_split = text.split('/')
        if self.room.group_address_style == '3-levels':
            if len(text_split) == 3:
                main, middle, sub = int(text_split[0]), int(text_split[1]), int(text_split[2])
                try: # test if the group address has the correct format
                    assert (main >= 0 and main <= 31 and middle >= 0 and middle <= 7 and sub >= 0 and sub <= 255)
                    return GroupAddress('3-levels', main = main, middle = middle, sub = sub)
                except AssertionError:
                    logging.warning("'3-levels' group address is out of bounds, should be in 0/0/0 -> 31/7/255")
                    return None
            else:
                logging.warning("'3-levels' style is not respected, possible addresses: 0/0/0 -> 31/7/255")
                return None
        elif self.room.group_address_style == '2-levels':
            if len(text_split) == 2:
                main, sub = int(text_split[0]), int(text_split[1])
                try: # test if the group address has the correct format
                    assert (main >= 0 and main <= 31 and sub >= 0 and sub <= 2047)
                    return GroupAddress('2-levels', main = main, sub = sub)
                except AssertionError:
                    logging.warning("'2-levels' group address is out of bounds, should be in 0/0 -> 31/2047")
                    return None
            else:
                logging.warning("'2-levels' style is not respected, possible addresses: 0/0 -> 31/2047")
                return None
        elif self.room.group_address_style == 'free':
            if len(text_split) == 1:
                main = int(text_split[0]),
                try: # test if the group address has the correct format
                    assert (main >= 0 and main <= 65535)
                    return GroupAddress('free', main = main)
                except AssertionError:
                    logging.warning("'free' group address is out of bounds, should be in 0 -> 65535")
                    return None


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

    def pause_simulation(self):
        self.room.simulation_status = not self.room.simulation_status
        if not self.room.simulation_status:
            logging.info("The simulation is paused")
            self.room.world.time.pause_time = time() # save current time to update start_time when
        else:
            logging.info("The simulation is resumed")
            paused_time = time() - self.room.world.time.pause_time
            self.room.world.time.start_time += paused_time

    def on_key_press(self, symbol, modifiers):
        from system.tools import configure_system_from_file
        ''' Called when any key is pressed:
            Define special action to modify text, save input text or end the simulation'''
        # Erase a character from the user input textbox
        if symbol == pyglet.window.key.BACKSPACE:
            self.input_label.text = self.input_label.text[:-1] # Remove last character
        #TODO: Save the command input by the user and erase it from the text box
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

    def on_mouse_press(self, x, y, button, modifiers):
        from system.tools import GroupAddress
        ''' Called when a mouse button is pressed (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is pressed'''
        if button == pyglet.window.mouse.LEFT:
            # LEFT click + SHIFT : activate functional module (e.g. turn switch ON/OFF)
            if modifiers & pyglet.window.key.MOD_SHIFT:
                for room_device in self.room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if room_device.device_type == "functional_module": # button, switch,..
                            functional_device = room_device
                            room_device.in_room_device.device.user_input() ###TODO: add the user cmmand input (e.g., temperature,...)
                            self.switch_sprite()

            # LEFT click + CTRL : set up group address between multiple devices
            elif modifiers & pyglet.window.key.MOD_CTRL:
                for room_device in self.room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        ga = self.group_address_format_check(self.input_label.text)
                        if ga:
                            print(room_device.in_room_device.device)
                            self.room.knxbus.attach(room_device.in_room_device.device, ga)
                            self.display_devices_list()

            # LEFT click on device w/o modifiers : add devices in simulator by dragging them in the Room area, or move room devices
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
                        ga = self.group_address_format_check(self.input_label.text)
                        if ga:
                            if ga in room_device.in_room_device.device.group_addresses:
                                room_device.in_room_device.device.group_addresses.remove(ga)
                                self.room.knxbus.detach(room_device.in_room_device.device, ga)
                            self.display_devices_list()


    def add_device(self):
        from system.tools import IndividualAddress
        device_class = self.moving_device.device_class
        individual_address = IndividualAddress(self.individual_address_default[0],
                                                self.individual_address_default[1],
                                                self.individual_address_default[2])
        refid = "M-O_X" + str(self.individual_address_default[2])
        if self.individual_address_default[2] >= 255:
            self.individual_address_default[2] = 0
            self.individual_address_default[1] += 1
        self.individual_address_default[2] += 1
        similar_devices_counter = 1
        for device in self.room_devices:
            if device_class.lower() in device.device_class.lower():
                print(f"---+++--- device similar: {device.label_name}, {device_class}")
                similar_devices_counter +=1
        device_name = device_class.lower()+str(similar_devices_counter)
        print(f"device_name: {device_name}")
        # Creation of the device object
        device = DEV_CLASSES[device_class](device_name, refid, individual_address, "enabled")
        loc_x, loc_y = gui_pos_to_system_loc(self.moving_device.pos_x, self.moving_device.pos_y,
                                                self.room_width_ratio, self.room_length_ratio,
                                                self.room_widget.origin_x, self.room_widget.origin_y)

        self.moving_device.in_room_device = self.room.add_device(device, loc_x, loc_y, 1) # 1 is default height z
        self.room_devices.append(self.moving_device)
        self.display_brightness_labels()
        self.display_temperature_labels()


    def on_mouse_release(self, x, y, button, modifiers):
        from system import Location
        ''' Called when a mouse button is released (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is released'''
        # The LEFT button is used to select and manage devices  (position, group addresses, activation,...)
        if button == pyglet.window.mouse.LEFT:
            # If there is a moving device, the release of LEFT button is to place the devce in the room or remove it from the GUI (release outside of the room)
            if hasattr(self, 'moving_device'):
                # Place the device in the Room if user drop it in the room widget
                if self.room_widget.hit_test(x, y):
                    pos_x, pos_y = x, y
                    loc_x, loc_y = gui_pos_to_system_loc(pos_x, pos_y, self.room_width_ratio, self.room_width_ratio, self.room_widget.origin_x, self.room_widget.origin_y)
                    # Test if the moving device is not already in the room (if user is not simply changing the position of a room device)
                    if self.moving_device not in self.room_devices:
                        self.add_device()
                        self.moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
                    else:
                        if not (modifiers & pyglet.window.key.MOD_SHIFT):
                            self.moving_device.update_position(pos_x, pos_y, loc_x, loc_y, update_loc=True)
                    

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

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        ''' Called when the mouse is dragged:
            Drag device accross the GUI if there is a moving device defined'''
        if not (modifiers & pyglet.window.key.MOD_SHIFT): # if SHIFT pressed, the user only want to activate the device and not move it
            if buttons & pyglet.window.mouse.LEFT:
                if hasattr(self, 'moving_device'):
                    self.moving_device.update_position(new_x = x, new_y = y) # - (self.moving_device.width//2)   - (self.moving_device.length//2)


    def on_key_release(self, symbol, modifiers): # release the ga connecting flag
        ''' Called when a key is released:
            Define actions to take when specific keys are released'''
        # Cancel the Group Adddress linking if CRTL key is released before the connection is established between two devices
        if symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL:
            print("ctrl is released")
            for room_device in self.room_devices:
                room_device.linking_group_address = False
                room_device.sprite.opacity = OPACITY_DEFAULT
            for button in self.buttons:
                button.widget.sprite.opacity = OPACITY_DEFAULT



def update_window(dt, window, speed_factor, start_time):
    ''' Functions called with the pyglet scheduler
        Update the Simulation Time displayed and should update the world state'''
    sim_time = str(timedelta(seconds=round(speed_factor*(time() - start_time), 2))) # 2 decimals
    window.simtime_label.text = f"Simulation Time: {sim_time[:-5]}" #update simulation time  {timedelta(seconds=sim_time)}
    print(f"doing update at {sim_time} \n")


# if __name__ == '__main__':
#     speed_factor = 180
#     window = GUIWindow()
#     start_time = time()
#     pyglet.clock.schedule_interval(update_window, 1, window, speed_factor, start_time)
#     pyglet.app.run()
#
#     print("The simulation has been ended.\n")


# pyglet.clock.schedule_interval(update, 1)
#pyglet.clock.schedule(update)  ## schedule to run the fct at the highest frequency possible
# Dismiss the dialog after 5 seconds.
#pyglet.clock.schedule_once(dismiss_dialog, 5.0)  ## for one-shot events
#pyglet.clock.unschedule(update)  ## to remove the fct from the scheduler list
