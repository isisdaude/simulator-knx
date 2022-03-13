"""
Simple simulator prototype.
"""

import devices as dev
import simulation as sim
import system as sys


# Declaration of sensors and actuators
led1 = dev.LED("led1", "M-0_A1", "0.0.0", "enabled") #Area 0, Line 0, Device 0
led2 = dev.LED("led2", "M-0_A2", "0.0.1", "enabled") #Area 0, Line 0, Device 0

button1 = dev.Button("button1", "M-0_B2", "0.0.5", "enabled") #Area 0, Line 0, Device 1
bright1 = dev.Brightness("brightness_sensor1", "M-0_C3", "0.0.10", "enabled") #Area 0, Line 0, Device 2

# Declaration of the physical system
room1 = sys.Room("bedroom1", 20, 20) #creation of a room of 20*20m2, we suppose the origin of the room (right-bottom corner) is at (0, 0)
room1.add_device(led1, 5, 5)
room1.add_device(led1, 10, 19)
room1.add_device(bright1, 20, 20)

# Declaration of functions/group addresses
# led1.set_group_addr("1/0/1")
# led2.set_group_addr("1/0/1")
# button1.set_group_addr("1/0/1")

print(led1)
print(button1)
print(bright1)
print(room1)

print("The brightness received on sensor %s located at (%d,%d) is %.2f" % ("bright1", bright1.loc_x, bright1.loc_y, room1.world.ambiant_light.get_brightness(bright1)))







# device_type, name, id, location, status, sensor/actuator_type
