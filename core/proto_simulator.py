"""
Simple simulator prototype.
"""

from devices.device_abstractions import Sensor, Actuator, SysDevice
# device_type, name, id, location, status, sensor/actuator_type

sensor1 = Sensor('sensor', 'GePro Brightness Sensor', 'M-0091_A111', '1/1/1', 'ON', 'Brightness sensor')

actuator1 = Actuator('actuator', 'GePro Light', 'M-0091_B222', '1/1/1', 'ON', 'Light')

sysdev1 = SysDevice('system', 'Line Coupler', 'M-0000_C333', '1/1/1', 'ON')


print(sensor1)
print(actuator1)
print(sysdev1)
