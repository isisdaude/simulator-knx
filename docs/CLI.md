# CLI commands

## set [device] <['ON'/'OFF'][value]>

[device] must be an actionable device = Functional Module \
[value] should be a percentage (0-100)

- If only [device] is mentioned, switch its state
- If 'ON'/'OFF' specified, put the actionable device in the corresponding state
- If [value] is given, it sets the actionable device with the value as ratio (0-100) if the device accepts it (e.g., a button can only have 2 states and specifying a ratio won't be taken into account)

## getvalue [device]

[device] must be a Sensor

Prints a dict representation of the physical state measured by the sensor (e.g. Temperature, Humidity, Soil Moisture, Presence,...)

## getinfo <[system component][option]>

- If 'getinfo' alone, print dict representations of the World, the Room and the KNX Bus
- [system component] can be:

  - 'world':
    - If [option] = 'time', print a dict representation of the **simulation time** and **speed factor**
    - If [option] = 'temperature', print a dict representation of the system **temperature** indoor and outdoor, with **simtime** as time reference
    - If [option] = 'humidity', print a dict representation of the system **humidity** indoor and outdoor, with **simtime** as time reference (soil moisture can be get through the sensor device)
    - If [option] = 'co2', print a dict representation of the system **co2** levels indoor and outdoor, with **simtime** as time reference
    - If [option] = 'brightness', print a dict representation of the system **brightness** indoor and outdoor, with **simtime** as time reference
    - If [option] = 'weather', prints a dict representation of the system **weather**, with **simtime** as time reference
    * If [option] = 'out', print a dict representation of the system outdoor states (**brightness**, **co2**, **humidity** and **temperature**), of **room insulation** and **simtime** as time reference
    - If no options or if [option] is 'all': print a dict representation of all the world state, indoor and outdoor, and room insulation
  - 'room': Prints a dict repesentation of the Room, composed of:
    - List of Room devices
    - Insulation
    - Room name
    - Dimensions Width/Length/Height
    - Volume
  - 'bus': Prints a dict repesentation of the Room, composed of:
    - Group addresses encoding style (free, 2-levels or 3-levels)
    - Dict representation of all group addresses and the devices connected to them, ordered by device type (Actuator, Functional Module or Sensor)
    - Name of the Bus
  - 'dev' or directly [device_name]: Prints a dict representation of the device's info:

    - Class Name: name of the class constructor if this instance (e.g. LED, BUTTON,...)
    - Device Name
    - Individual Address
    - Location
    - Reference ID
    - Room Name in which the device is located
    - Status: if the device is 'enabled' or 'disabled'
    - More specific info per device class:

      - Button / Dimmer:
        - State
        - State Ratio for Dimmer
      - Switch:
        - State
      - LED:
        - State
        - State Ratio
        - Beam Angle : angle describing how light gets out from the source
        - Max Lumen
        - Effective Lumen
      - Heater / AC:

        - State
        - State Ratio
        - Max Power
        - Effective Power
        - Update_Rule : number of degrees gained(lost if <0) per hour at max power

      - Sensors: They have one additional field for their respective measured value:
        - Temperature, CO2 level and Humidity for AirSensor, and respectively for Thermometer, CO2Sensor and HumidityAir sensors
        - Soil Moisture for HumiditySoil sensor
        - Brightness for Brightness sensors
