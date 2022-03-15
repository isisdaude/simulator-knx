"""
Simple simulator prototype.
"""

import functools
import asyncio
from contextlib import suppress

import devices as dev
import simulation as sim
import system as sys
import user_interaction as ui



# Declaration of sensors and actuators
led1 = dev.LED("led1", "M-0_L1", "0.0.0", "enabled") #Area 0, Line 0, Device 0
led2 = dev.LED("led2", "M-0_L1", "0.0.1", "enabled")

heater1 = dev.Heater("heater1", "M-0_T1", "0.0.11", "enabled")
cooler1 = dev.Cooler("cooler1", "M-0_T2", "0.0.12", "enabled")

button1 = dev.Button("button1", "M-0_B1", "0.0.20", "enabled")
bright1 = dev.Brightness("bright1", "M-0_L3", "0.0.5", "enabled")



# Declaration of the physical system
room1 = sys.Room("bedroom1", 20, 20) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
room1.add_device(led1, 5, 5)
room1.add_device(led2, 10, 19)
room1.add_device(bright1, 20, 20)

room1.add_device(heater1, 0, 5)
room1.add_device(cooler1, 20, 5)

print(room1)

command_help="enter command: \n -Actuators: 'set '+name to switch state ON/OFF\n -Sensors: 'get '+name to read sensor value\n>'q' to exit the simulation, 'h' for help<\n"
print(command_help)

while True:
    command = input()
    if command[:3] == 'set': #Actuator
        name = command[3:]
        for device in room1.devices:
            if device.name == name:
                device.switch_state()
    elif command[:3] == 'get': #Sensor
        name = command[3:]
        if "bright" in name: # brightness sensor
            for device in room1.devices:
                if device.name == name:
                    print("The brightness received on sensor %s located at (%d,%d) is %.2f" % (name, device.loc_x, device.loc_y, room1.world.ambient_light.get_brightness(device)))
    elif command in ('h', 'H'):
        print(command_help)
    elif command in ('q','Q'):
        break

print("The simulation has been ended.")


# Declaration of functions/group addresses
# led1.set_group_addr("1/0/1")
# led2.set_group_addr("1/0/1")
# button1.set_group_addr("1/0/1")

# print(led1)
# print(button1)
# print(bright1)






# device_type, name, id, location, status, sensor/actuator_type
