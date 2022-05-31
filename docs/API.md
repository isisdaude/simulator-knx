# Script API

## wait [time]
waits during [time] seconds (system/computer seconds)

## set [device] ['ON'/'OFF'] ([value])
if device is a Functional Module:
* Turn ON/OFF a activable device (Functional Module) 
* If [value] is given, it sets the activable device with the value as ratio

<!-- if device is a Sensor:
* Turn ON/OFF the sending of telegrams
*  -->


## set [ambient_state] [value] (['in'/'out'])
* sets an [ambient sate] (Temperature, Humidity, CO2 level, Brightness) to a [value] 
* If [ambient sate] is 'weather',  value should be 'clear', 'overcast' or 'dark' and there should not be ['in'/'out'] argument

## store ['world'/'device'] [ambient/state] [variable_name]
store a system value into the [variable_name], to check it later in the script
* world : [ambient] can be Temperature, Humidity, CO2, Brightness, Weather
* device : [state] can be the state (ON/OFF) of the device, or a characteristic attribute of this device. Possible attributes:
    - **Temperature Actuators**: state, max_power, effective_power, state_ratio
    - **Light Actuator** : state, max_lumen, effective_lumen, state_ratio
    - **Dimmer FunctionalModule** : state, state_ratio
    - **Brightness Sensor** : brightness
    - **Thermometer Sensor** : temperature
    - **HumiditySoil Sensor** : humiditysoil
    - **HumidityAir Sensor** : humidity
    - **CO2Sensor** : co2
    - **AirSensor** : temperature, humidity, co2
    - **PresenceSensor** : state

## assert [variable_name] [value] 
test if a stored variable [variable_name] is at a wanted [value]

## end
end the API script and terminate the program
