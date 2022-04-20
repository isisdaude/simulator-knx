import pyglet
from time import time
from datetime import timedelta

WIN_WIDTH = 1500
WIN_HEIGHT = 1000
BORDER = 10  # Space between the window border and the Room wodget borders


class DeviceWidget(object):
    def __init__(self, x, y, batch, img_file_ON, img_file_OFF, group, device_type):
        self.name = ''
        self.device_type = device_type
        self.in_motion = False # Temporary flag to inform that the device widget is being moved
        self.linking_group_address = False # Temporary flag to establish a group address connection between two devices
        self.is_on = False # devices turned ON/OFF
        self.group_addresses = [] # will store the group addresses, can control the number e.g. for sensors
        self.file_ON = img_file_ON
        self.file_OFF = img_file_OFF #usefull to create a moving instance of the available devices
        self.x = x
        self.y = y
        self.batch = batch
        self.img_ON = pyglet.image.load(self.file_ON)
        self.img_OFF = pyglet.image.load(self.file_OFF)
        self.width, self.height = self.img_ON.width, self.img_ON.height #ON/OFF images have the same width
        self.sprite = pyglet.sprite.Sprite(self.img_OFF, x=self.x, y=self.y, batch=self.batch, group=group)

    def hit_test(self, x, y): # to check if mouse click is inside a text box
        return (0 < abs(x - self.x) < self.width and
                0 < abs(y - self.y) < self.height)

    def update_position(self,x, y):
        self.x = x
        self.y = y
        self.sprite.update(x=x, y=y)

class RoomWidget(object):
    def __init__(self, width, height, batch, group):
        self.x = WIN_WIDTH - width - BORDER
        self.y = BORDER
        self.width = width
        self.height = height
        self.batch = batch
        self.shape = pyglet.shapes.BorderedRectangle(self.x, self.y, width, height, border=3,
                                            color=(50, 180, 140), border_color=(200, 180, 140),
                                            batch=self.batch, group=group)#, group = group
        self.shape.opacity = 100

        self.devices = []

    def hit_test(self, x, y): # to check if mouse click is inside a text box
        return (self.x < x < (self.x + self.width) and
                self.y < y < (self.y + self.height))

    def add_device(self, device):
        self.devices.append(device)


class AvailableDevices(object): # library of devices availables, presented on the left side on the GUI
    def __init__(self, batch, group):
        self.in_motion = False
        self.devices = []
        self.lightbulb = DeviceWidget(50, 750, batch, 'png_simulator/lightbulb_ON.png', 'png_simulator/lightbulb_OFF.png', group, "actuator")
        self.devices.append(self.lightbulb)
        self.switch = DeviceWidget(30, 700, batch, 'png_simulator/switch_ON.png', 'png_simulator/switch_OFF.png', group, "functional_module")
        self.devices.append(self.switch)
## Make the difference between actuators, functional modules and sensors


class GUIWindow(pyglet.window.Window):
    ''' Class to define the GUI window, the widgets and text displayed in it and the functions reactign to the user actions (mouse click, input text,...) '''
    def __init__(self):
        super(GUIWindow, self).__init__(WIN_WIDTH, WIN_HEIGHT, caption='KNX Simulation Window', resizable=False)
        # Configure the window size
        self.width = WIN_WIDTH
        self.height = WIN_HEIGHT
        #self.set_minimum_size(1200, 1000) #minimum window size
        #self.set_minimum_size(1300, 1100) #minimum window size
        #self.push_handlers(on_resize=self.local_on_resize) #to avoid redefining the on_resize handler
        # Configure batch of modules to draw on events (mouse click, moving,...)
        self.batch = pyglet.graphics.Batch()
        # Create multiple layers to superpose the graphical elements
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        #document = pyglet.text.document.UnformattedDocument()
        # Array to store the devices added to the room (by dragging them for instance)
        self.room_devices = []
        # Initialize the room widget to draw in the window
        self.room = RoomWidget(1000, 800, self.batch, group=self.background)
        # Initialize the Available devices widgets to draw them on the left size, s that a user can drag them in the room
        self.available_devices = AvailableDevices(self.batch, self.foreground)
        # Define the position of the text elements and the text box to interact with the user
        self.commandlabel_pos = (98*(self.width//100), 95*(self.height//100))
        self.simlabel_pos = (2*(self.width//100), 95*(self.height//100))
        self.textbox_pos = (85*(self.width//100), 90*(self.height//100))
        # Create the text labels and the textbox to display to the user
        self.command_label = pyglet.text.Label('Enter your command',
                                  font_name='Times New Roman',
                                  font_size=20,
                                  x=self.commandlabel_pos[0], y=self.commandlabel_pos[1],
                                  anchor_x='right', anchor_y='bottom', batch=self.batch, group=self.foreground)
        self.simtime_label = pyglet.text.Label("Simulation Time: 0", # init the simulation time display
                                  font_name='Times New Roman',
                                  font_size=20,
                                  x=self.simlabel_pos[0], y=self.simlabel_pos[1],
                                  anchor_x='left', anchor_y='bottom', batch=self.batch, group=self.foreground)
        self.text_box = pyglet.shapes.Rectangle(self.textbox_pos[0], self.textbox_pos[1], 200, 40, color=(255, 255, 255),
                                        batch=self.batch, group=self.background)
        # Initialize the text box label to display the user input in the textbox
        self.input_label = pyglet.text.Label("",
                                  font_name='Times New Roman',
                                  font_size=15,
                                  color=(10, 10, 10, 255),
                                  x=(self.text_box.x+10), y=(self.text_box.y+20),
                                  anchor_x='left', anchor_y='center', batch=self.batch, group=self.foreground)
    # def local_on_resize(self, width, height):
    #     # self.width = width
    #     # self.height = height
    #     print(f"The window was resized to {width}x{height}")
    def is_group_address(self, text): ## TODO: verify if the group address entered in text box is correct
        ''' Verify that the group address entered by the user is correct (2, 3-levels or free) '''
        return True

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
        ''' Called when any key is pressed:
            Define special action to modify text, save input text or end the simulation'''
        # Erase a character from the user input textbox
        if symbol == pyglet.window.key.BACKSPACE:
            self.input_label.text = self.input_label.text[:-1] # Remove last character
        #TODO: Save the command input by the user and erase it from the text box
        elif symbol == pyglet.window.key.ENTER:
            print("Command is saved\n")
            self.input_label.text = ''
        # CTRL-ESCAPE to end the simulation
        elif symbol == pyglet.window.key.ESCAPE:
            if modifiers and pyglet.window.key.MOD_CTRL:
                # print("The simulation has been ended.")
                pyglet.app.exit()

    def on_mouse_motion(self, x, y, dx, dy): # NOTE: for now, just a POC but ,ay be interestng to use it to highlight widgets
        ''' Called when the mouse is moving over the window (whithout button clicked):
            Change color appearance of the Room widget to highlight it when hovering over it
            x, y: position of the mouse
            dx, dy: displacement since last observation (time delta between observations defined by the library, can be changed but not usefull in this project)'''
        # Test if the mouse is over the Room widget
        if self.room.hit_test(x, y):
            self.room.shape.opacity = 150
            # print(f"mouse is at x:{x} y:{y}, has moved of dx:{dx} dy:{dy}\n")
        else:
            self.room.shape.opacity = 100

    def on_mouse_press(self, x, y, button, modifiers):
        ''' Called when a mouse button is pressed (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is pressed'''
        # The RIGHT button is used to delete devices from the Room
        if button == pyglet.window.mouse.RIGHT:
            for room_device in self.room_devices:
                # Test if the mouse is over a room device widget when clicked
                if room_device.hit_test(x, y):
                    # Delete the widget's sprite (graphical representation of the device)
                    room_device.sprite.delete()
                    # Remove the device from the Room's device list
                    self.room_devices.remove(room_device)
                    print("Device removed from the room\n")
                    return # Exit the function to differentiate when the user is doign a rightclick on the Room and not a device
            # Test if the mouse is over the Room widget when clicked
            if self.room.hit_test(x, y): #TODO: Implement a scrolling menu or something similar
                print("rightclick room\n")
        # The LEFT button is used to select and manage devices  (position, group addresses, activation,...)
        if button == pyglet.window.mouse.LEFT:
            #LEFT click + CTRL : set up of group address between two devices
        # TODO: make possible to link multiple devices with the same ga, by checking if the ga is already linked to a selected device, or to other devices
        # TODO: bug whith the display (opacity) when setting group addresses
            if modifiers & pyglet.window.key.MOD_CTRL: # If we click on a device with CTRL, we are assigning a group address and linking two devices
                #TODO Test if the user input is a group address valid
                if self.is_group_address(self.input_label.text):
                    group_address = self.input_label.text
                    for room_device in self.room_devices:
                        # Test if the user clicked on a room device instanciated
                        if room_device.hit_test(x, y):
                            # Test if the device is not currently being linked to a group address
                            if room_device.linking_group_address == False:
                                room_device.linking_group_address = True
                                room_device.sprite.opacity = 150 # Visual feedback of the linking state
                                device_selected = room_device # We select the first device to link to this group address
                                for room_device_bis in self.room_devices:
                                    # Search for another device waiting for connection
                                    if room_device_bis != device_selected and room_device_bis.linking_group_address == True: # we find another device waiting to connect with a group address
                                        # We add the group address to devices' ga list to be able to link them when activating the functional modules
                                        # TODO: display all active group adddresses in the window
                                        if group_address not in device_selected.group_addresses:
                                            device_selected.group_addresses.append(group_address)
                                        else:
                                            print("group address already assigned to the first device")
                                        if group_address not in room_device_bis.group_addresses:
                                            room_device_bis.group_addresses.append(group_address)
                                        else:
                                            print("group address already assigned to the second device")
                                        # Resetting of the linking state to False #NOTE bug is probably here for opacity when setting the ga
                                        room_device_bis.linking_group_address = False
                                        device_selected.linking_group_address = False
                                        room_device_bis.sprite.opacity = 255
                                        print(f"Group address {group_address} is assigned between the two devices\n")
                                        self.input_label.text = ''
                                        break
                                # if there are no device waiting for connection, the selected device put itself in waitng state
                                # device_selected.linking_group_address = True

                            else: # the user click again on the same device, to cancel the connection
                            ## TODO : later, implement the possibility to remove ga without removing the device
                            ## NOTE or bug is here for opacity when setting the ga
                                device_selected.linking_group_address = False
                                device_selected.sprite.opacity = 255 # the user wants to cancelled its group address connection
            # LEFT click + SHIFT : activate functional module (e.g. turn switch ON/OFF)
            elif modifiers & pyglet.window.key.MOD_SHIFT:
                for room_device in self.room_devices:
                    # Test if the user clicked on a room device instanciated
                    if room_device.hit_test(x, y):
                        if room_device.device_type == "functional_module": # button, switch,..
                            functional_device = room_device
                            for room_device_bis in self.room_devices:
                                # Search for a actuator that would react to a user input on a functional module = that is connected to the same ga
                                if room_device_bis.device_type == "actuator":
                                    #TODO: create a list of devices connected to the group address
                                    if shared_group_address(functional_device, room_device_bis):
                                        print("corresponding group address")
                                        # TODO: make a function that swtich between ON/OFF
                                        if not functional_device.is_on:
                                            functional_device.is_on = True
                                            room_device_bis.is_on = True
                                            # Replace the OFF image by the ON image (=sprite)
                                            room_device_bis.sprite.delete()
                                            room_device_bis.sprite = pyglet.sprite.Sprite(room_device_bis.img_ON, x=room_device_bis.x, y=room_device_bis.y, batch=self.batch, group=self.foreground)
                                            functional_device.sprite.delete()
                                            functional_device.sprite = pyglet.sprite.Sprite(functional_device.img_ON, x=functional_device.x, y=functional_device.y, batch=self.batch, group=self.foreground)
                                            break
                                        elif functional_device.is_on:
                                            functional_device.is_on = False
                                            room_device_bis.is_on = False
                                            room_device_bis.sprite.delete()
                                            room_device_bis.sprite = pyglet.sprite.Sprite(room_device_bis.img_OFF, x=room_device_bis.x, y=room_device_bis.y, batch=self.batch, group=self.foreground)
                                            functional_device.sprite.delete()
                                            functional_device.sprite = pyglet.sprite.Sprite(functional_device.img_OFF, x=functional_device.x, y=functional_device.y, batch=self.batch, group=self.foreground)
                                            break

            # LEFT click on device w/o modifiers : add devices in simulator by dragging them in the Room area
            else:
                # Test if there is no moving devices
                if not hasattr(self, 'moving_device'):
                    for device in self.available_devices.devices:
                        # Test if the user clicked on a available device on the side of the GUI (kind of 'library' of available devices)
                        if device.hit_test(x, y):
                            device_type = device.device_type
                            # Add a "moving" instance of the selected device
                            self.moving_device = DeviceWidget(x, y, self.batch, device.file_ON, device.file_OFF, group=self.foreground, device_type=device_type)
                    for room_device in self.room_devices:
                        # Test if user clicked on a instanciated Room device to ajust its position in the Room
                        if room_device.hit_test(x, y):
                            # Replacement of the room device object by a moving device object
                            self.moving_device = room_device
                            self.room_devices.remove(room_device)
                            self.moving_device.update_position(x = x - (self.moving_device.width//2), y = y - (self.moving_device.height//2))

    def on_mouse_release(self, x, y, button, modifiers):
        ''' Called when a mouse button is released (LEFT, RIGHT or MIDDLE):
            Define multiple action to do when one of the mouse button is released'''
        # The LEFT button is used to select and manage devices  (position, group addresses, activation,...)
        if button == pyglet.window.mouse.LEFT:
            # If there is a moving device, the release of LEFT button is to place the devce in the room or remove it from the GUI (release outside of the room)
            if hasattr(self, 'moving_device'):
                if self.room.hit_test(x, y):
                    self.moving_device.update_position(x = x - (self.moving_device.width//2), y = y - (self.moving_device.height//2))
                    self.room_devices.append(self.moving_device)
                    delattr(self, 'moving_device')
                else:
                    self.moving_device.sprite.delete()
                    delattr(self, 'moving_device')


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        ''' Called when the mouse is dragged:
            Drag device accross the GUI if there is a moving device defined'''
        if buttons & pyglet.window.mouse.LEFT:
            if hasattr(self, 'moving_device'):
                self.moving_device.update_position(x = x - (self.moving_device.width//2), y = y - (self.moving_device.height//2))


    def on_key_release(self, symbol, modifiers): # release the ga connecting flag
        ''' Called when a key is released:
            Define actions to take when specific keys are released'''
        # Cancel the Group Adddress linking if CRTL key is released before the connection is established between two devices
        if symbol == pyglet.window.key.LCTRL or symbol == pyglet.window.key.RCTRL:
            print("ctrl is released")
            for room_device in self.room_devices:
                room_device.linking_group_address = False
                room_device.sprite.opacity = 255



def shared_group_address(functional_module, actuator):
    '''Test if two devices have a group address in common'''
    for ga in functional_module.group_addresses:
        if ga in actuator.group_addresses:
            return True
    return False


def update_window(dt, window, speed_factor, start_time):
    ''' Functions called with the pyglet scheduler
        Update the Simulation Time displayed and should update the world state'''
    sim_time = str(timedelta(seconds=round(speed_factor*(time() - start_time), 2))) # 2 decimals
    window.simtime_label.text = f"Simulation Time: {sim_time[:-5]}" #update simulation time  {timedelta(seconds=sim_time)}
    print(f"doing update at {sim_time} \n")


if __name__ == '__main__':
    speed_factor = 180
    window = GUIWindow()
    start_time = time()
    pyglet.clock.schedule_interval(update_window, 1, window, speed_factor, start_time)
    pyglet.app.run()

    print("The simulation has been ended.\n")


# pyglet.clock.schedule_interval(update, 1)
#pyglet.clock.schedule(update)  ## schedule to run the fct at the highest frequency possible
# Dismiss the dialog after 5 seconds.
#pyglet.clock.schedule_once(dismiss_dialog, 5.0)  ## for one-shot events
#pyglet.clock.unschedule(update)  ## to remove the fct from the scheduler list
