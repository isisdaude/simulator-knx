"""
Simple simulator prototype.
"""

import functools
import asyncio, aioconsole
import aioreactive as rx
from pynput import keyboard
from datetime import datetime
from contextlib import suppress
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import devices as dev
import simulation as sim
import system as sys
import user_interface as ui



# Declaration of sensors and actuators
led1 = dev.LED("led1", "M-0_L1", "0.0.0", "enabled") #Area 0, Line 0, Device 0
led2 = dev.LED("led2", "M-0_L1", "0.0.1", "enabled")

heater1 = dev.Heater("heater1", "M-0_T1", "0.0.11", "enabled")
cooler1 = dev.Cooler("cooler1", "M-0_T2", "0.0.12", "enabled")

button1 = dev.Button("button1", "M-0_B1", "0.0.20", "enabled")
button2 = dev.Button("button2", "M-0_B2", "0.0.21", "enabled")
bright1 = dev.Brightness("bright1", "M-0_L3", "0.0.5", "enabled")



# Declaration of the physical system
room1 = sys.Room("bedroom1", 20, 20) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
room1.add_device(led1, 5, 5)
room1.add_device(led2, 10, 19)
room1.add_device(button1, 0, 0)
room1.add_device(button2, 0, 1)

room1.add_device(bright1, 20, 20)

room1.add_device(heater1, 0, 5)
room1.add_device(cooler1, 20, 5)

print(room1)

command_help="enter command: \n -Actuators: 'set '+name to switch state ON/OFF\n -Sensors: 'get '+name to read sensor value\n>'q' to exit the simulation, 'h' for help<\n"
print(command_help)


async def user_input_loop():
    while True:
        command = await aioconsole.ainput("What do you want to do?\n")
        if command[:3] == 'set': #Actuator
            name = command[4:]
            for device in room1.devices:
                if device.name == name:
                    device.device.switch_state()
        elif command[:3] == 'get': #Sensor
            name = command[4:]
            if "bright" in name: # brightness sensor
                for device in room1.devices:
                    if device.name == name:
                        print("The brightness received on sensor %s located at (%d,%d) is %.2f" % (name, device.get_x(), device.get_y(), room1.world.ambient_light.read_brightness(device)))
        elif command in ('h', 'H'):
            print(command_help)
        elif command in ('q','Q'):
            break
        else:
            print("Unknown input, please " + command_help)

# async def knx_bus_communication():
#     stream = rx.AsyncSubject()



async def async_main():
    ui_task = loop.create_task(user_input_loop())
    # bus_task = loop.create_task(knx_bus_communication())
    await asyncio.wait([ui_task])


if __name__ == "__main__":
    #TODO: launch the scheduler only when the user inputs the speed factor of the simulation and/or launch the simulation (e.g. with a start button)
    sched = AsyncIOScheduler()
    updateJob = sched.add_job(room1.update_world, 'interval', seconds=20)
    sched.start()
    try:
        loop = asyncio.get_event_loop()
        #app = ui.GraphicalUserInterface(loop)
        #app.mainloop()
        loop.run_until_complete(async_main())

    except (KeyboardInterrupt, SystemExit):
        print("The simulation has been ended.")





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
