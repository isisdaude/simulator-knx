"""
Simple simulator prototype.
"""

import functools
import asyncio, aioconsole
import time, datetime
import aioreactive as rx
import tkinter as tk
from pynput import keyboard
from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import system
import devices as dev
import simulation as sim
import user_interface as ui
from system import IndividualAddress, GroupAddress, Telegram


# Declaration of sensors and actuators
led1 = dev.LED("led1", "M-0_L1", IndividualAddress(0,0,1), "enabled") #Area 0, Line 0, Device 0
led2 = dev.LED("led2", "M-0_L1", IndividualAddress(0,0,2), "enabled")

heater1 = dev.Heater("heater1", "M-0_T1", IndividualAddress(0,0,11), "enabled", 400) #400W max power
cooler1 = dev.AC("cooler1", "M-0_T2", IndividualAddress(0,0,12), "enabled", 400)

button1 = dev.Button("button1", "M-0_B1", IndividualAddress(0,0,20), "enabled")
button2 = dev.Button("button2", "M-0_B2", IndividualAddress(0,0,21), "enabled")
bright1 = dev.Brightness("bright1", "M-0_L3", IndividualAddress(0,0,5), "enabled")

temp_controller = dev.TemperatureController("tempc", "M-0_TC1", IndividualAddress(0,0,3), "enabled") #TODO: should not we set it to True?





# Declaration of the physical system
room1 = system.Room("bedroom1", 20, 20, 3) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
room1.add_device(led1, 5, 5, 1)
room1.add_device(led2, 10, 19, 1)
room1.add_device(button1, 0, 0, 1)
room1.add_device(button2, 0, 1, 1)

room1.add_device(bright1, 20, 20, 1)

room1.add_device(heater1, 0, 5, 1)
room1.add_device(cooler1, 20, 5, 1)

room1.add_device(temp_controller, 0, 0, 2)

print(room1)

# Group addresses # '3-levels', '2-levels' or 'free'
ga1 = GroupAddress('3-levels', main = 1, middle = 1, sub = 1)
room1.knxbus.attach(led1, ga1) # Actuator is linked to the group address ga1 through the KNXBus
room1.knxbus.attach(button1, ga1)

temperature_communication = GroupAddress('3-levels', main=2, middle=0, sub=0)
room1.knxbus.attach(temp_controller, temperature_communication)
room1.knxbus.attach(heater1, temperature_communication)





command_help = "enter a command for:\n"
command_help +=" - FunctionalModules: 'set [name]' to act on it\n"
command_help +=" - Sensors: 'get [name]' to read sensor value\n"
command_help +=" > 'q' to exit the simulation, 'h' for help <\n"
print(command_help)


async def user_input_loop():
    while True:
        command: str = await aioconsole.ainput(">>> What do you want to do?\n")
        command = command.split(' ')
        query = command[0]

        if query in ('h', 'H'):
            print(command_help)
        elif query in ('q','Q'):
            break

        if(len(command) < 2):
            print(f"[ERROR] Usage is: set/get device_name [input_value]")
            break
    
        name = command[1]
        
        for in_room_device in room1.devices:
            if in_room_device.name == name:
                if query == 'set': # We are interacting with a functional module
                    
                        if not isinstance(in_room_device.device, dev.FunctionalModule):
                            print("[ERROR] Users can only act on a Functional Module")
                            break
                        if isinstance(in_room_device.device, dev.Button):
                            in_room_device.device.user_input()
                        elif isinstance(in_room_device.device, dev.TemperatureController):
                            try:
                                in_room_device.device.user_input(command[2])
                            except IndexError:
                                print(f"[ERROR] You did not specify the wished temperature for the controller.")

                elif query == 'get': # We are getting a sensor value
                    if 'bright' in name: # Brightness sensor
                        print("\n=> The brightness received on sensor %s located at (%d,%d) is %.2f\n" % (name, in_room_device.get_x(), in_room_device.get_y(), room1.world.ambient_light.read_brightness(in_room_device)))
                else:
                    print("[ERROR] Unknown input, please " + command_help)
                    break

        # if command[:3] == 'set': #FunctionalModule
        #     name = command[4:]
        #     for in_room_device in room1.devices:
        #         if in_room_device.name == name:
        #             if not isinstance(in_room_device.device, dev.FunctionalModule):
        #                 print("[ERROR] Users can only act on a Functional Module")
        #                 break
        #             if isinstance(in_room_device.device, dev.Button):
        #                 in_room_device.device.user_input()
        #             elif isinstance(in_room_device.device, dev.TemperatureController):
        #                 in_room_device.device.user_input()
        # elif command[:3] == 'get': #Sensor
        #     name = command[4:]
        #     if "bright" in name: # brightness sensor
        #         for in_room_device in room1.devices:
        #             if in_room_device.name == name:
        #                 print("\n=> The brightness received on sensor %s located at (%d,%d) is %.2f\n" % (name, in_room_device.get_x(), in_room_device.get_y(), room1.world.ambient_light.read_brightness(in_room_device)))
        # elif command in ('h', 'H'):
        #     print(command_help)
        # elif command in ('q','Q'):
        #     break
        # else:
        #     print("[ERROR] Unknown input, please " + command_help)

async def async_main(loop):
    ui_task = loop.create_task(user_input_loop())
    # clock = DigitalClock(interval = 0.2)
    # clock_task = loop.create_task(clock.update())
    #gui_task = loop.create_task()
    await asyncio.wait([ui_task])  #, clock_task


if __name__ == "__main__":
    # launch the scheduler only when the user inputs the speed factor of the simulation and/or launch the simulation (e.g. with a start button)
    # sim_time will manage the scheduler
    while(True): # waits for the input to be a correct speed factor, before starting the simulation
        try:
            simulation_speed_factor = float(input(">>> What speed would you like to set for the simulation?  [real time = speed * simulation time]\n"))
            break
        except ValueError:
            print("[ERROR] The simulation speed should be a number")
            pass

    sim_time = sim.Time(simulation_speed_factor)
    sim_time.scheduler_init()
    sim_time.scheduler_add_job(room1.update_world) # we pass the update function as argument to the Time class object
    sim_time.scheduler_start()
    # updateJob = scheduler.add_job(room1.update_world, 'interval', seconds=20)
    # sim_time.scheduler_start()
    try:
        loop = asyncio.get_event_loop()
        #app = ui.GraphicalUserInterface(loop)
        #app.mainloop()
        loop.run_until_complete(async_main(loop))

    except (KeyboardInterrupt, SystemExit):
        print("The simulation has been ended.")



#### Tkinter clock #####
# class DigitalClock(tk.Tk):
#     def __init__(self, interval = 0.2):
#         super().__init__()
#         self.loop = loop
#         self.interval = interval
#         self.start_time = time.time()
#         # configure the root window
#         self.title('Digital Clock')
#         self.resizable(0, 0)
#         self.geometry('250x80')
#         self['bg'] = 'black'
#
#         # change the background color to black
#         self.style = tk.ttk.Style(self)
#         self.style.configure(
#             'TLabel',
#             background='black',
#             foreground='red')
#
#         # label
#         self.label = tk.ttk.Label(
#             self,
#             text=self.time_string(),
#             font=('Digital-7', 40))
#
#         self.label.pack(expand=True)
#
#         # schedule an update every 1 second
#         #self.label.after(1000, self.update)
#     def time_string(self):
#         sim_time = time.time() - self.start_time
#         str_sim_time = str(datetime.timedelta(seconds=sim_time))
#         return str_sim_time
#
#     async def update(self):
#         """ update the label every interval second """
#         while True:
#             self.label.configure(text=self.time_string())
#             await asyncio.sleep(self.interval)


# Declaration of functions/group addresses
# led1.set_group_addr("1/0/1")
# led2.set_group_addr("1/0/1")
# button1.set_group_addr("1/0/1")

# print(led1)
# print(button1)
# print(bright1)




# # Keyboard Listener for better user_interaction

# def on_press(key):
#     if key == keyboard.Key.esc:
#         return False  # stop listener
#     try:
#         k = key.char  # single-char keys
#     except:
#         k = key.name  # other keys
#     if k in ['1', '2', 'left', 'right']:  # keys of interest
#         # self.keys.append(k)  # store it in global-like variable
#         print('Key pressed: ' + k)
#         return False  # stop listener; remove this if want more keys
#
# listener = keyboard.Listener(on_press=on_press)
# listener.start()  # start to listen on a separate thread
# listener.join()  # remove if main thread is polling self.keys




# device_type, name, id, location, status, sensor/actuator_type
