# KNX Smart Home Simulator

The **KNX Smart Home Simulator** is a development tool that can be used when designing smart infrastructures, such as smart buildings.


This simulator software represents a [KNX system](https://www.knx.org/knx-en/for-professionals/index.php), without real physical devices but virtual ones, and models its evolution through time in response to user interactions and to a simulated physical world's influences. With this simulator, one user can configure a KNX system with visual feedback, interact with it and even test applications developed with [**SVSHI**](https://github.com/dslab-epfl/svshi) (**S**ecure and **V**erified **S**mart **H**ome **I**nfrastructure) before implementing them in a real physical KNX system.

It provides a [CLI](#cli), a [GUI](#gui) to easily interact  with the platform and a script [API](#api) to run automated tests.

## Installation

In order to work, the simulator needs Python 3.9 or newer ([download here](https://www.python.org/downloads/)). 

You can then download the simulator by either downloading the repository or cloning it. You can also download [SVSHI](https://github.com/dslab-epfl/svshi), as it already includes the simulator.

Being at the root of the simulator (**simulator-knx/**), you can install all the necessary requirements with the following command:
```
pip3 install -r requirements/requirements.txt
```

## Configuration
The system configuration can be done either by:
- Parsing a JSON file provided by the user **<-- RECOMMENDED**:
You can configure the configuration file by copying the template from *simulator-knx/config/empty_config.json* and modifying the fields according to your needs.
- Calling configuration functions and methods in the source code by directly modifying `configure_system` in *simulator-knx/tools/config_tools*,
- Dynamically interacting with the system through the Graphical User Interface described in [GUI](#gui),
- Combining these approaches


## Running

You can start the simulator by being at the root of the simulator (**simulator-knx/**) and running `python3 run.py` with the options according to your needs.

You can run `python3 run.py -h` in the folder to display the following:

```
usage: run.py [-h] [-l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}] [-i {gui,cli}]
              [-c {script,cli}] [-f FILESCRIPT_NAME] [-C {file,default,empty,dev}] [-F FILECONFIG_NAME]
              [-s] [-t]

Process Interface, Command, Config and Logging modes.

options:
  -h, --help            show this help message and exit
  -l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}, --log {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
                        Provide logging level.
                        Example '-l debug' or '--log=DEBUG'
                        -> default='WARNING'.
  -i {gui,cli}, --interface {gui,cli}
                        Provide user interface mode.
                        Example '-i cli' or '--interface=cli'
                        -> default='gui'.
  -c {script,cli}, --command-mode {script,cli}
                        Provide command mode (only if interface mode is CLI).
                        Example '-c script' or '--command-mode=script'
                        -> default='cli'
  -f FILESCRIPT_NAME, --filescript-name FILESCRIPT_NAME
                        Provide script file name (without .txt extension).
                        Example '-F full_script' or '--file-name=full_script'
                        -> default='full_script'
  -C {file,default,empty,dev}, --config-mode {file,default,empty,dev}
                        Provide configuration mode.
                        Example '-C file' or '--command-mode=empty'
                        -> default='file'
  -F FILECONFIG_NAME, --fileconfig-name FILECONFIG_NAME
                        Provide configuration file name (without .json extension).
                        Example '-F sim_config_bedroom' or '--file-name=sim_config_bedroom'
                        -> default='sim_config_bedroom'
  -s, --svshi-mode      Specifies that SVSHI program will be used, start a thread to communicate with it.
  -t, --telegram-logging
                        Specifies that the telegrams sent and received should be logged in a file located in logs/ folder

```
## CLI

### `set [device] <['ON'/'OFF'][value]>`

[device] must be an activable device = Functional Module \
[value] should be a percentage (0-100)

- If only [device] is mentioned, switch its state
- If 'ON'/'OFF' specified, put the activable device in the corresponding state
- If [value] is given, it sets the activable device with the value as ratio (0-100) if the device accepts it (e.g., a button can only have 2 states and specifying a ratio won't be taken into account)

### `getvalue [device]`

[device] must be a Sensor

Prints a dict representation of the physical state measured by the sensor (e.g. Temperature, Humidity, Soil Moisture, Presence,...)

### `getinfo <[system component][option]>`

- If `getinfo` alone, print dict representations of the World, the Room and the KNX Bus
- [system component] can be:

  - `world`:
    - If [option] = 'time', print a dict representation of the **simulation time** and **speed factor**
    - If [option] = 'temperature', print a dict representation of the system **temperature** indoor and outdoor, with **simtime** as time reference
    - If [option] = 'humidity', print a dict representation of the system **humidity** indoor and outdoor, with **simtime** as time reference (soil moisture can be get through the sensor device)
    - If [option] = 'co2', print a dict representation of the system **co2** levels indoor and outdoor, with **simtime** as time reference
    - If [option] = 'brightness', print a dict representation of the system **brightness** indoor and outdoor, with **simtime** as time reference
    - If [option] = 'weather', prints a dict representation of the system **weather**, with **simtime** as time reference
    * If [option] = 'out', print a dict representation of the system outdoor states (**brightness**, **co2**, **humidity** and **temperature**), of **room insulation** and **simtime** as time reference
    - If no options or if [option] is 'all': print a dict representation of all the world state, indoor and outdoor, and room insulation
  - `room`: Prints a dict repesentation of the Room, composed of:
    - List of Room devices
    - Insulation
    - Room name
    - Dimensions Width/Length/Height
    - Volume
  - `bus`: Prints a dict repesentation of the Room, composed of:
    - Group addresses encoding style (free, 2-levels or 3-levels)
    - Dict representation of all group addresses and the devices connected to them, ordered by device type (Actuator, Functional Module or Sensor)
    - Name of the Bus
  - `dev` or directly [device_name]: Prints a dict representation of the device's info:

    - Class Name: name of the class constructor if this instance (e.g. LED, BUTTON,...)
    - Device Name
    - Individual Address
    - Location
    - Reference ID
    - Room Name in which the device is located
    - Status: if the device is 'enabled' or 'disabled'
    - More specific info per device class:

        - **Button / Dimmer**:
            - State
            - State Ratio for Dimmer

        - **Switch**:
            - State

        - **LED**:
            - State
            - State Ratio
            - Beam Angle : angle describing how light gets out from the source
            - Max Lumen
            - Effective Lumen

        - **Heater / AC**:
            - State
            - State Ratio
            - Max Power
            - Effective Power
            - Update_Rule : number of degrees gained(lost if <0) per hour at max power 

        - **Sensors**: 
        They have one additional field for their respective measured value:
            - Temperature, CO2 level and Humidity for AirSensor, and respectively for Thermometer, CO2Sensor and HumidityAir sensors
            - Soil Moisture for HumiditySoil sensor
            - Brightness for Brightness sensors

## GUI

### Main Buttons:

- Play/Pause [CTRL+P] : pause the simulation time
- Stop [CTRL+ESCAPE] : Stop the simulation and terminate the program
- Reload [CTRL+R] : Reload the simulation from the initial config file (or None if None was given)
- Save : Save the current system configuration (devices, their location and group addresses) to a JSON file
- Default :
  - LEFT click : reload with a default config (~3 devices)
  - RIGHT click : reload with an empty config (no devices)

### Command Box:

Write any CLI command (set, get,...) and press enter to get the result either in the GUI or in the terminal window where the process is running

### Device configuration/Management

#### **Add device**:

LEFT click on a devices from the available devices box on the left, and drag it to the desired location in the room widget

#### **Replace exisiting device in room**

LEFT click and existing device in room and drop it at the desired location

#### **Add a group address to a device**:

1. Write the group address using the keyboard (it will appear in the 'command' white box at the top right corner)
2. While pressing [CTRL], LEFT click on the desired device

#### **Remove a group address from a device**:

2. While pressing [CTRL], Right click on the desired device

#### **Activate a device**:

While pressing [SHIFT], LEFT click on a activable device (Functional Modules)

- Dimmer : [SHIFT] + LEFT click and drag up/down to set the ratio

#### **See all devices present in the room**

Scroll up/down with the mouse above the devices' list on bottom left of the window

### Special actions

- Soil Humidity sensor : [SHIFT] + LEFT click to "water" the plants
- Presence sensor :
  - [ALT/OPTION] + LEFT click in room to add a person in the simulation
  - [ALT/OPTION] + RIGHT click in room to remove a person from the simulation
- Vacuum cleaner :
  - [ALT/OPTION] + [SPACE] to toggle vacuum cleaner presence

## Script API

### `wait [time]<['h']>`

waits during [time] seconds (system/computer seconds)

- if 'h' is mentionned, time indicated corresponds to simulated hours

### `set [device] <['on'/'off']> <[value]>`

If device is a Functional Module:

- Turn ON/OFF a activable device (Functional Module)
- If [value] is given, it sets the activable device with the value as ratio

If device is a Sensor, no ['on'/'off'] argument (other sensors can not be set individually):

- HumiditySoil Sensor, sets moisture to [value]=(0-100)
- Presence Sensor, sets presence to [value]=(True/False/ON/OFF)\


### `set [ambient_state][value] <['in'/'out']>`

- Sets an [ambient sate] to a value, [ambient_state] can be:
  - Temperature (in/out): sets temperature for all sensors
  - Humidity (in/out): sets humidity for all sensors
  - CO2 (in/out): sets co2 for all sensors
  - Presence: sets presence for all sensors
    - [value] must be 'True' or 'False', as if we add/remove a person from the simulation
    - there should be no ['in'/'out'] argument
  - Weather
    - [value] must be 'clear', 'overcast' or 'dark'
    - there should be no ['in'/'out'] argument

### `store ['world'/device][ambient/state] [variable_name]`

Store a system value into the [variable_name], to check it later in the script

- world : [ambient] can be 'SimTime', 'Temperature', 'Humidity', 'CO2', 'Brightness', 'Weather'
- device : [device] is the device's name, [state] can be the state (ON/OFF) of the device, or a characteristic attribute of this device. Possible attributes:
  - **Temperature Actuators**: state, max_power, effective_power, state_ratio
  - **Light Actuator** : state, max_lumen, effective_lumen, state_ratio, beam_angle
  - **Switch** : state
  - **Dimmer/Button FunctionalModule** : state, state_ratio
  - **Brightness Sensor** : brightness
  - **Thermometer Sensor** : temperature
  - **HumiditySoil Sensor** : humiditysoil
  - **HumidityAir Sensor** : humidity
  - **CO2Sensor** : co2level
  - **AirSensor** : temperature, humidity, co2level
  - **PresenceSensor** : state

### `assert [variable_name]['=='/'!='/'<='/'>='][value/variable_name]`

Compare a stored variable [variable_name] to a [value] or other variable

### `show <[variable_name/'all']>`

Prints the value of the variable_name specified.
Prints all stored variable if 'all' given or if nothing is given

### `end`

Ends the API script and terminate the program



when modifying classes:
-> modify the `__init__.py` files

When adding new devices types ("light",...):
-> modify the list in devices.abstractions

Config file json:
-> keys are names (area0, line0, led1, switch1,...)


launch pytest command
pytest -q --log-cli-level error simulator/tests/

Code conventions: black formatting (for alignement mainly), PEP8(spaces and names conventions) and PEP257 (docstring), PEP526 (variable typing)