# Script API

All command are case-insensitive.

## wait [time]<['h'/'m'/'s']>

waits during [time] seconds (system/computer seconds)

- if 'h', 'hour' or 'hours' is mentioned, time indicated corresponds to simulated hours
- if 'm', 'minute' or 'minutes' is mentioned, time indicated corresponds to simulated minutes
- if 's', 'second' or 'seconds' is mentioned, time indicated corresponds to simulated seconds

## set [device] <['on'/'off']> <[value]>

If device is a Functional Module:

- Turn ON/OFF a actionable device (Functional Module)
- If [value] is given, it sets the actionable device with the value as ratio

If device is a Sensor, no ['on'/'off'] argument (other sensors can not be set individually):

- HumiditySoil Sensor, sets moisture to [value]=(0-100)
- Presence Sensor, sets presence to [value]=(True/False)\

## set [ambient_state][value] <['in'/'out']>

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

## store ['world'/device][ambient/state] [variable_name]

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

## assert [variable_name]['=='/'!='/'<='/'>='][value/variable_name]

Compare a stored variable [variable_name] to a [value] or other variable

## show <[variable_name/'all']>

Prints the value of the variable_name specified.
Prints all stored variable if 'all' given or if nothing is given

## end

Ends the API script and terminate the program
