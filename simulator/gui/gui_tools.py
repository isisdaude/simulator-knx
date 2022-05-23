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
        self.box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, self.topleft_y-self.length, DEVICE_LIST_BOX_WIDTH, self.length, border=WIN_BORDER/2,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=batch, group=self.__group_box)

        self.deviceslist_title = pyglet.text.Label("Devices in the Room:",
                                    font_name=FONT_SYSTEM_TITLE, font_size=15, bold=True,
                                    x=x, y=y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group_label)
    
    def update_box(self, new_length):
        new_length = new_length if new_length>0 else OFFSET_DEVICELIST_BOX_TOP
        self.length = new_length + OFFSET_DEVICELIST_BOX_TOP+OFFSET_DEVICELIST_BOX_BOTTOM
        self.box_shape.delete()
        self.box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, self.topleft_y-self.length, DEVICE_LIST_BOX_WIDTH, height=self.length, border=WIN_BORDER/2,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=self.__batch, group=self.__group_box)
    
    def hit_test(self, x, y): # to check if mouse click is on the Device list widget
        # print(f"x: {self.box_shape.x} < {x} < {(self.box_shape.x + DEVICE_LIST_BOX_WIDTH)}")
        # print(f"y: {self.box_shape.y} < {y} < {(self.box_shape.y + self.length)}")
        return (self.box_shape.x < x < (self.box_shape.x + DEVICE_LIST_BOX_WIDTH) and
                self.box_shape.y < y < (self.box_shape.y + self.length))


class SimTimeWidget(object):
    def __init__(self, x, y, batch, group_label, group_box):
        self.box_shape = pyglet.shapes.BorderedRectangle(x-OFFSET_SIMTIME_BOX, y-SIMTIME_BOX_LENGTH/2, SIMTIME_BOX_WIDTH, SIMTIME_BOX_LENGTH, border=WIN_BORDER/2,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=batch, group=group_box)
        self.simtime_titlelabel = pyglet.text.Label("Simulation Time:", # init the simulation time title
                                    font_name=FONT_SYSTEM_TITLE, font_size=20, bold=True,
                                    x=x, y=y,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group_label)
        self.simtime_valuelabel = pyglet.text.Label("0", # init the simulation time display
                                    font_name=FONT_SYSTEM_TITLE, font_size=20, bold=True,
                                    x=x, y=y-OFFSET_SIMTIME_TITLE,
                                    anchor_x='left', anchor_y='bottom',
                                    batch=batch, group=group_label)


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
        self.clicked = True

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
                                    font_name=FONT_DIMMER_RATIO, font_size=30,
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
    def __init__(self, pos_x, pos_y, batch, img_file_ON, img_file_OFF, group, device_type, device_class, device_number, available_device=False):
        ''' docstring'''
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
        if available_device: # available devices for a manual import (displayed outside of the GUI)
            self.origin_x, self.origin_y = self.pos_x, self.pos_y
        else:
            self.origin_x, self.origin_y = self.pos_x - self.width//2, self.pos_y - self.length//2
        self.__batch = batch
        self.group = group
        self.sprite = pyglet.sprite.Sprite(self.img_OFF, x=self.origin_x, y=self.origin_y, batch=self.__batch, group=self.group) # x,y of sprite is bottom left of image
        self.label = pyglet.text.Label(self.label_name,
                                    font_name=FONT_DEVICE, font_size=10,
                                    x=(self.origin_x+self.width//2), y=(self.origin_y-OFFSET_LABEL_DEVICE),
                                    anchor_x='center', anchor_y='center',
                                    batch=self.__batch, group=self.group)

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
            self.in_room_device.update_location(new_x=self.loc_x, new_y=self.loc_y)
            logging.info(f"Location of {self.label_name} is updated to {self.loc_x}, {self.loc_y}")

    def delete(self):
        self.sprite.delete()
        self.label.delete()


class AvailableDevices(object): # library of devices availables, presented on the left side on the GUI
    def __init__(self, batch, group_dev, group_box):
        self.in_motion = False
        self.devices = []

        self.box_shape = pyglet.shapes.BorderedRectangle(WIN_BORDER/2, OFFSET_AVAILABLEDEVICES_LINE2-OFFSET_AVAILABLE_DEVICES-WIN_BORDER/2, AVAILABLE_DEVICES_BOX_WIDTH, AVAILABLE_DEVICES_BOX_LENGTH, border=WIN_BORDER/2,
                                            color=BLUESUMMERSKY_RGB, border_color=BLUEMINSK_RGB,
                                            batch=batch, group=group_box)

        # Line 1
        self.led = DeviceWidget(WIN_BORDER, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_LED_ON_PATH, DEVICE_LED_OFF_PATH, group_dev, "actuator", "LED", '', available_device=True)
        self.devices.append(self.led)
        next_image_offset_x = self.led.pos_x + self.led.width + OFFSET_AVAILABLE_DEVICES
        self.button = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_BUTTON_ON_PATH, DEVICE_BUTTON_OFF_PATH, group_dev, "functional_module", "Button", '', available_device=True)
        self.devices.append(self.button)
        next_image_offset_x = self.button.pos_x + self.button.width + OFFSET_AVAILABLE_DEVICES
        self.dimmer = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_DIMMER_ON_PATH, DEVICE_DIMMER_OFF_PATH, group_dev, "functional_module", "Dimmer", '', available_device=True)
        self.devices.append(self.dimmer)
        next_image_offset_x = self.dimmer.pos_x + self.dimmer.width + OFFSET_AVAILABLE_DEVICES
        self.brightness = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_BRIGHT_SENSOR_PATH, DEVICE_BRIGHT_SENSOR_PATH, group_dev, "sensor", "Brightness", '', available_device=True)
        self.devices.append(self.brightness)
        next_image_offset_x = self.brightness.pos_x + self.brightness.width + OFFSET_AVAILABLE_DEVICES
        self.thermometer = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE1, batch, DEVICE_THERMO_COLD_PATH, DEVICE_THERMO_HOT_PATH, group_dev, "sensor", "Thermometer", '', available_device=True)
        self.devices.append(self.thermometer)
        # Line 2
        self.heater = DeviceWidget(WIN_BORDER, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_HEATER_ON_PATH, DEVICE_HEATER_OFF_PATH, group_dev, "actuator", "Heater", '',  available_device=True)
        self.devices.append(self.heater)
        next_image_offset_x = self.heater.pos_x + self.heater.width + 0.5*OFFSET_AVAILABLE_DEVICES
        self.ac = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_AC_ON_PATH, DEVICE_AC_OFF_PATH, group_dev, "actuator", "AC", '',  available_device=True)
        self.devices.append(self.ac)
        next_image_offset_x = self.ac.pos_x + self.ac.width + OFFSET_AVAILABLE_DEVICES
        self.presence = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_PRESENCE_ON_PATH, DEVICE_PRESENCE_OFF_PATH, group_dev, "sensor", "PresenceSensor", '',  available_device=True)
        self.devices.append(self.presence)
        next_image_offset_x = self.presence.pos_x + self.presence.width + OFFSET_AVAILABLE_DEVICES
        self.switch = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_SWITCH_ON_PATH, DEVICE_SWITCH_OFF_PATH, group_dev, "actuator", "Switch", '', available_device=True)
        self.devices.append(self.switch)
        next_image_offset_x = self.switch.pos_x + self.switch.width + 0.2*OFFSET_AVAILABLE_DEVICES
        self.airsensor = DeviceWidget(next_image_offset_x, OFFSET_AVAILABLEDEVICES_LINE2, batch, DEVICE_AIRSENSOR_PATH, DEVICE_AIRSENSOR_PATH, group_dev, "actuator", "AirSensor", '', available_device=True)
        self.devices.append(self.airsensor)
        
        




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