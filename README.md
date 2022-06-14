# KNX Smart Home Simulator

- [KNX Smart Home Simulator](#KNX-Smart-Home-Simulator)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running](#running)
    - [With SVSHI](#with-svshi)
  - [CLI](#cli)
  - [GUI](#gui)
  - [Script API](#script-api)
  - [Details for developers](#details-for-developers)
    - [Physical world modeling](#physical-world-modeling)
    - [Configuration JSON file](#configuration-json-file)
    - [GUI Implementation details](#gui-implementation-details)

The **KNX Smart Home Simulator** is a development tool that can be used when designing smart infrastructures, such as smart buildings.


This simulator software represents a [KNX system](https://www.knx.org/knx-en/for-professionals/index.php), without real physical devices but virtual ones instead, and models its evolution through time in response to user interactions and to a simulated physical world's influences. With this simulator, one user can configure a KNX system with visual feedback, interact with it and even test applications developed with [**SVSHI**](https://github.com/dslab-epfl/svshi) (**S**ecure and **V**erified **S**mart **H**ome **I**nfrastructure) before implementing them in a real physical KNX system. 

It provides a [CLI](#cli), a [GUI](#gui) to easily interact  with the platform and a script [Script API](#script-api) to run automated tests.

&nbsp;
## Installation

In order to work, the simulator needs Python 3.9 or newer ([download here](https://www.python.org/downloads/)). 

You can then download the simulator by either downloading the repository or cloning it. You can also download [SVSHI](https://github.com/dslab-epfl/svshi), as it already includes the simulator.

Being at the root of the simulator (**simulator-knx/**), you can install all the necessary requirements with the following command:
```
pip3 install -r requirements/requirements.txt
```
&nbsp;
## Configuration
The system configuration can be done either by:
- Parsing a JSON file provided by the user **<-- RECOMMENDED**:\
You can configure the configuration file by copying the template from *simulator-knx/config/empty_config.json* and modifying the fields according to your needs. Other more complete templates are accessible in config/ folder.\
  - To use this configuration mode, the following options should be set in argument:\
    -C=file             : indicate that a config file will be used (although it is the default setting)\
    -F=fileconfig_name  : specify name of the config file to use (without .json) 
- Calling configuration functions and methods in the source code by directly modifying `configure_system()` in *simulator-knx/tools/config_tools*,
  - To use this mode, the following options should be set in argument:\
  -C=dev : indicate that the configuration will be done in developper mode, with python functions and methods
- Dynamically interacting with the system through the Graphical User Interface described in [GUI](#gui),
  - To use this mode, the following options should be set in argument:\
  -i=cli or gui
  -c=cli : indicates that CLI commands can be used, opposed to script mode 
- Combining these approaches

&nbsp;
## Running

You can start the simulator by being at the root of the simulator (**simulator-knx/**) and running `python3 run.py` with the options according to your needs.

You can run `python3 run.py -h` to display the following help:

```
usage: run.py [-h] [-l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}] [-i {gui,cli}]
              [-c {script,cli}] [-f FILESCRIPT_NAME] [-C {file,default,empty,dev}] [-F FILECONFIG_NAME]
              [-s] [-t]

Process Interface, Command, Config and Logging modes.

optional arguments:
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
&nbsp;
### With SVSHI
If you want to run the simulator with SVSHI, here are the steps:

1. Run the command `python3 run.py -s` (you can add other options if you want to couple SVSHI mode with the GUI, CLI, script API...)
The simulator will start waiting for a connection with SVSHI at the address that it prints on the terminal.
2. Configure a SVSHI app and start SVSHI (either through CLI or GUI, you can refer to more detailed explanations [here](https://github.com/dslab-epfl/svshi) for running SVSHI), when running SVSHI you have to make sure that:
    - The address given to SVSHI for the interface corresponds to the one displayed by our simulator when started.
    - You assigned group addresses to the devices according to the ones SVSHI generated with your application. If not, you can assign group addresses dynamically when using the GUI, or restart the simulator in CLI mode with the correct group addresses configuration.
3. Wait for the connection between the simulator and SVSHI to be completed, and then enjoy!

An example app can be found in foler simulator-knx/svshi_apps. It has a basic functioning: the button turn on the heater, and the light is turned on when the temperature reach 21°C. The prototypical file and main app are in the folder. The assignements can be downloaded from [**SVSHI**](https://github.com/dslab-epfl/svshi) directly.

&nbsp;
## CLI
The CLI command are usable during simulation, through shell if interface_mode=CLI, or through the GUI command box if interface_mode=GUI. \
They are not callable in script_mode.\
To make use of CLI commands, the following options can be set in argument:\
-i=cli or gui : in both interface_mode, CLI commands are usable\
-c=cli : CLI commands are not usable in script mode\


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

&nbsp;
## GUI
To launch the simulation in GUI mode, the following options must be set in argument:\
-i=gui : choose the interface_mode GUI to visualize the system\
SVSHI can be run in parrallel and this can be indicated to the simulator by using:\
-s : indicate use of SVSHI\
-t : activate log of telegrams exchanged between svshi and the simulator

### **Main Buttons:**

- Play/Pause [CTRL+P] : pause the simulation time
- Stop [CTRL+ESCAPE] : Stop the simulation and terminate the program
- Reload [CTRL+R] : Reload the simulation from the initial config file (or None if None was given)
- Save : Save the current system configuration (devices, their location and group addresses) to a JSON file
- Default :
  - LEFT click : reload with a default config (~3 devices)
  - RIGHT click : reload with an empty config (no devices)

### **Command Box:**

Write any CLI command (set, get,...) and press enter to get the result either in the GUI or in the terminal window where the process is running

### **Device configuration/Management**

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

### **Special actions**

- Soil Humidity sensor : [SHIFT] + LEFT click to "water" the plants
- Presence sensor :
  - [ALT/OPTION] + LEFT click in room to add a person in the simulation
  - [ALT/OPTION] + RIGHT click in room to remove a person from the simulation
- Vacuum cleaner :
  - [ALT/OPTION] + [SPACE] to toggle vacuum cleaner presence

&nbsp;
## Script API
The API commands should be written in a script .txt file, that should be located in the scripts/ folder. The script terminates when the script is finished, an 'end' command is met or an 'assert' is False, and the program terminates also.\
To launch the simulation in script_mode, the following options must be set in argument:\
-i=cli          : choose shell interface (opposed to GUI)\
-c=script       : choose script command mode (opposed to cli, to call CLI command for instance)\
-f=script_name  : specify the name of teh script to run (without .txt extension)

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
  - **CO2Sensor** : co2
  - **AirSensor** : temperature, humidity, co2
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

&nbsp;
## Details for developers

This section is destined to future developers willing to improve or modify the code. It aim is to demystify som subtilities in teh code, the configuration and the global functioning.

### Physical world modeling
One important aspcet of this simulator is the modeling of physical states evolution in time (Brightness, Temperature, Humidity, CO2). For instance, If users turn ON a heater, the temperature should rise, but there is no heating sources, and the outdoor temperature is lower than indoor's, the temperature should decrease.

We based the logic on online references, physical knowledge and intuition, but it can in no case be considered as a 100% truthful representation of the world states. This project only waits for one thing, thta a physicist improve the modeling of physical states :) In the mean time, we provide a arbitrarly acceptable modeling of these states, allowing users to test application involving temperature value for instance.

### Configuration JSON file
The configuration using a json prototype is the most easy way to configure the system. Nevertheless, there are many fields. Let's detail some of them:
- **simulation_speed_factor** and **system_dt**: system_dt corresponds to th etime interval between two consecutive updates, the speed factor allows to compute the concrete simulated time during this interval.
- inside and outside values can be set be the user to configure the intial system state
- **datetime**: indicate when the simulation is launched, possible values are: 
  - 'today', 'yesterday', 'one_week_ago', 'one_month_ago'
  - datetime can also be indicated using format 'YYYY/MM/DD/HH/MM'
  - this config will be integrated to the simulator using a datetime.datetime object
- **weather**: indicates the outdoor weather during the simulation, supposed to be constant (except in script mode), possible values are:
  - 'clear', 'overcast', 'dark'
  - each weather, associated to the datetime, allows to define the outdoor brightness, which can be used to compute indoor resulting brightness on sensors if teh room has windows imlemented.
- **insulation**: represents the room's insulation quality, it will have an effect on evolution of temperature, humidity and co2. Possible values are:
  -  'perfect', 'good', 'average', 'bad'
  - The impact of each insulation type is arbitrarly define through a ratio in world/world_tools.py module.
- **windows' location offset**: define the offset of window's location from start of the wall.
  - windows are defined on walls ('north', 'south', 'east', 'west')
  - the origin of the offset is the south-west room's corner
  - the location offset represnts the distance between this origin and window's location.
  - Take precaution when defining windows, as they should fit in the room or they will be discarded.
- **devices' names**: For usability and understandability of teh code and the system, it is reauired to inser the lower-case class name of a device in its name, associated with a number.

### GUI implementation details
A little detail to note is the difference between the pyglet 'height' and the simulator 'height'.\
The simulation, although it is represented in 2D, implements a room in 3D. The simulator 'height' is thus logically the 3rd axis z getting out of the plan (in GUI mode).\
For pyglet, 'height' is the 2nd axis y (vertical) on the screen plan. Be aware that we call 'length' the pyglet 'height' in the wole code.\
For instance, a Room is defined by its width, length and height.


