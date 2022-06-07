# User Guide GUI

## Main Buttons:

- Play/Pause [CTRL+P] : pause the simulation time
- Stop [CTRL+ESCAPE] : Stop the simulation and terminate the program
- Reload [CTRL+R] : Reload the simulation from the initial config file (or None if None was given)
- Save : Save the current system configuration (devices, their location and group addresses) to a JSON file
- Default :
  - LEFT click : reload with a default config (~3 devices)
  - RIGHT click : reload with an empty config (no devices)

## Command Box:

Write any CLI command (set, get,...) and press enter to get the result either in the GUI or in the terminal window where the process is running

## Device configuration/Management

### **Add device**:

LEFT click on a devices from the available devices box on the left, and drag it to the desired location in the room widget

### **Replace exisiting device in room**

LEFT click and existing device in room and drop it at the desired location

### **Add a group address to a device**:

1. Write the group address using the keyboard (it will appear in the 'command' white box at the top right corner)
2. While pressing [CTRL], LEFT click on the desired device

### **Remove a group address from a device**:

2. While pressing [CTRL], Right click on the desired device

### **Activate a device**:

While pressing [SHIFT], LEFT click on a activable device (Functional Modules)

- Dimmer : [SHIFT] + LEFT click and drag up/down to set the ratio

### **See all devices present in the room**

Scroll up/down with the mouse above the devices' list on bottom left of the window

## Special actions

- Soil Humidity sensor : [SHIFT] + LEFT click to "water" the plants
- Presence sensor :
  - [ALT/OPTION] + LEFT click in room to add a person in the simulation
  - [ALT/OPTION] + RIGHT click in room to remove a person from the simulation
- Vacuum cleaner :
  - [ALT/OPTION] + [SPACE] to toggle vacuum cleaner presence
