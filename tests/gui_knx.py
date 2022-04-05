import pyglet
from time import time
from datetime import timedelta

WIN_WIDTH = 1500
WIN_HEIGHT = 1000
BORDER = 10


class DeviceWidget(object):
    def __init__(self, x, y, batch, img_file_ON, img_file_OFF, group, device_type):
        self.device_type = device_type
        self.in_motion = False
        self.linking_group_address = False # Temporary flag to establish a group address connection between two devices
        self.group_addresses = [] # will store the group addresses, can control the number e.g. for sensors
        self.file_ON = img_file_ON
        self.file_OFF = img_file_OFF
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
    def __init__(self):
        super(GUIWindow, self).__init__(WIN_WIDTH, WIN_HEIGHT, caption='KNX Simulation Window', resizable=False)
        self.width = WIN_WIDTH
        self.height = WIN_HEIGHT
        # self.set_minimum_size(1200, 1000) #minimum window size
        # self.set_minimum_size(1300, 1100) #minimum window size
        # self.push_handlers(on_resize=self.local_on_resize) #to avoid redefining the on_resize handler
        self.batch = pyglet.graphics.Batch() #
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        #document = pyglet.text.document.UnformattedDocument()

        self.room_devices = []
        self.room = RoomWidget(1000, 800, self.batch, group=self.background)
        self.available_devices = AvailableDevices(self.batch, self.foreground)

        self.commandlabel_pos = (98*(self.width//100), 95*(self.height//100))
        self.simlabel_pos = (2*(self.width//100), 95*(self.height//100))
        self.textbox_pos = (85*(self.width//100), 90*(self.height//100))

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
        self.input_label = pyglet.text.Label("", # init the simulation time display
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
        return True

    def on_draw(self):
        self.clear()
        self.batch.draw()
        # self.push_handlers(self.focus.caret)

    def on_text(self, text):
        self.input_label.text += text
        print("on text\n")

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.BACKSPACE:
            self.input_label.text = self.input_label.text[:-1] # remove last character
        elif symbol == pyglet.window.key.ENTER: # save command
            print("Command is saved\n")
            self.input_label.text = ''
        elif symbol == pyglet.window.key.ESCAPE: #CTRL-ESCAPE to quit the simulation
            if modifiers and pyglet.window.key.MOD_CTRL:
                pyglet.app.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        if self.room.hit_test(x, y):
            self.room.shape.opacity = 150
            # print(f"mouse is at x:{x} y:{y}, has moved of dx:{dx} dy:{dy}\n")
        else:
            self.room.shape.opacity = 100

    def on_mouse_press(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.RIGHT:
            for room_device in self.room_devices:
                print("room device\n")
                if room_device.hit_test(x, y):
                    room_device.sprite.delete() # removal of the device from the room
                    self.room_devices.remove(room_device)
                    print("remove\n")
            if self.room.hit_test(x, y):  # right click on the room
                print("rightclick room\n")

        if button == pyglet.window.mouse.LEFT:
            if modifiers & pyglet.window.key.MOD_CTRL: #if we click on a device with CTRL, we are assigning a group address and linking two devices
                if self.is_group_address(self.input_label.text):
                    group_address = self.input_label.text
                    for room_device in self.room_devices:
                        if room_device.hit_test(x, y): # the device on which the user has clicked on
                            if room_device.linking_group_address == False:
                                device_selected = room_device # new device selected (2nd)
                                for room_device_bis in self.room_devices: # we search for the device wiating for a connection
                                    if room_device_bis.linking_group_address == True: # we find a device waiting to connect with a group address
                                        if group_address not in device_selected.group_addresses:
                                            device_selected.group_addresses.append(group_address)
                                        else:
                                            print("group address already assigned to this device__")
                                        if group_address not in room_device_bis.group_addresses:
                                            room_device_bis.group_addresses.append(group_address)
                                        else:
                                            print("group address already assigned to this device")
                                        room_device_bis.linking_group_address = False
                                        room_device_bis.sprite.opacity = 255
                                        print(f"Group address {group_address} is assigned between the two devices\n")
                                        self.input_label.text = ''
                                        break
                                # if there are no device waiting for connection, the selected device put itself in waitng state
                                device_selected.linking_group_address = True
                                device_selected.sprite.opacity = 150 # visual feedback of the linking state
                            else: # the user click again on the same device, to cancel the connection
                            ## TODO : later, implement the possibility to remove ga without removing the device
                                device_selected.linking_group_address = False
                                device_selected.sprite.opacity = 255 # the user wants to cancelled its group address connection
            # if the user activate the device
            elif modifiers & pyglet.window.key.MOD_SHIFT:
                print("shift")
                for room_device in self.room_devices:
                    if room_device.hit_test(x, y):
                        print("device hitted")
                        if room_device.device_type == "functional_module": # if user pressed a button, switch,..
                            print("button pressed")
                            functional_device = room_device
                            for room_device_bis in self.room_devices:
                                if room_device_bis.device_type == "actuator":  #TODO: create a list of devices connected to the group address
                                    print("actuator found")
                                    for ga in room_device_bis.group_addresses:
                                        if ga in functional_device.group_addresses: # we found a pair functional_module-actuator connected with the same group address
                                            print("corresponfing group address")
                                            room_device_bis.sprite.delete()
                                            room_device_bis.sprite = pyglet.sprite.Sprite(room_device_bis.img_ON, x=room_device_bis.x, y=room_device_bis.y, batch=self.batch, group=self.foreground)
                                            functional_device.sprite.delete()
                                            functional_device.sprite = pyglet.sprite.Sprite(functional_device.img_ON, x=functional_device.x, y=functional_device.y, batch=self.batch, group=self.foreground)
                                            break

            else:
                for device in self.available_devices.devices:
                    if device.hit_test(x, y): # if user click on an available device
                        if device.in_motion == False:
                            device.in_motion = True  # set the "moving" flag to indicate a displacement
                            device_type = device.device_type
                            self.moving_device = DeviceWidget(x, y, self.batch, device.file_ON, device.file_OFF, group=self.foreground, device_type=device_type) # we add a "moving" instance of the selected device
                            #pyglet.sprite.Sprite(device.img_OFF, x=x, y=y, batch=self.batch, group=self.foreground) #create a second instance
                        else:
                            pass # if already in motion, we don't want to add another instance of the device
                for room_device in self.room_devices:
                    if room_device.hit_test(x, y):
                        if room_device.in_motion == False: # Should always not be in motion but we never know
                            room_device.in_motion = True
                            room_device.update_position(x=x, y=y)



## do the case where ctrl is released but not on a device : cancelled everything



    def on_mouse_release(self, x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            for device in self.available_devices.devices:
                if device.in_motion == True:
                    if self.room.hit_test(x, y): # if the device was being placed by the user in the room
                        self.moving_device.update_position(x=x - (device.width//2), y=y - (device.height//2))# update of the sprite object
                        device.in_motion = False # release of the device
                        self.room_devices.append(self.moving_device) #we add the DeviceWidget object to be able to call hit_test()
                    else:
                        self.moving_device.sprite.delete()
                        device.in_motion = False
            for room_device in self.room_devices:
                if room_device.in_motion == True:
                    if self.room.hit_test(x, y): # if the device was being placed by the user in the room
                        room_device.update_position(x=x - (room_device.width//2), y=y - (room_device.height//2))# update of the sprite object
                        room_device.in_motion = False # release of the device
                    else:
                        room_device.sprite.delete()
                        self.room_devices.remove(room_device)
                        room_device.in_motion = False


    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            for device in self.available_devices.devices:
                if device.in_motion == True: # if image is in motion, we delete change the position of the instance
                    self.moving_device.update_position(x=x, y=y) # update of the sprite object and the device position
            for room_device in self.room_devices:
                if room_device.in_motion == True: # if image is in motion, we delete change the position of the instance
                    room_device.update_position(x=x, y=y) # update of the actual room_device position

        #print(f"mouse is at x:{x} y:{y}, has moved of dx:{dx} dy:{dy} in dt:{dt}\n")


start_time = time()

def update_window(dt, window, speed_factor):
    sim_time = str(timedelta(seconds=round(speed_factor*(time() - start_time), 2))) # 2 decimals
    window.simtime_label.text = f"Simulation Time: {sim_time[:-5]}" #update simulation time  {timedelta(seconds=sim_time)}
    print(f"doing update at {sim_time} \n")


if __name__ == '__main__':
    speed_factor = 180
    window = GUIWindow()
    pyglet.clock.schedule_interval(update_window, 1, window, speed_factor)
    pyglet.app.run()

# pyglet.clock.schedule_interval(update, 1)
#pyglet.clock.schedule(update)  ## schedule to run the fct at the highest frequency possible
# Dismiss the dialog after 5 seconds.
#pyglet.clock.schedule_once(dismiss_dialog, 5.0)  ## for one-shot events
#pyglet.clock.unschedule(update)  ## to remove the fct from the scheduler list

# pyglet.app.run()

print("pyglet is finished\n")
