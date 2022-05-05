
import pyglet
import logging
import json

from datetime import datetime
from .gui_config import *

# Button widgets
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
        saved_config_path = gui_window.saved_config_path + datetime.now().strftime("%d%m%Y_%H%M%S")
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
    






# Device widgets
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





# Room widget
class RoomWidget(object):
    def __init__(self, width, length, batch, group, label_group, label):
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
        self.batch = batch
        self.shape = pyglet.shapes.BorderedRectangle(self.origin_x_shape, self.origin_y_shape, width+2*ROOM_BORDER, length+2*ROOM_BORDER, border=ROOM_BORDER,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=self.batch, group=group)#, group = group
        self.shape.opacity = OPACITY_ROOM
        self.label = pyglet.text.Label(self.name,
                                    font_name=FONT_SYSTEM_INFO, font_size=75,
                                    x=(self.origin_x + self.width/2), y=(self.origin_y + self.length/2),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.batch, group=label_group)
        self.label.opacity = OPACITY_ROOM_LABEL

    def hit_test(self, x, y): # to check if mouse click is on the Room widget
        return (self.origin_x < x < (self.origin_x + self.width) and
                self.origin_y < y < (self.origin_y + self.length))


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