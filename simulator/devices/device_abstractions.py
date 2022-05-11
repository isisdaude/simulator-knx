"""
Gather the abstract class definitions for the simulated KNX devices.
"""
#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import logging, sys
from abc import ABC, abstractmethod
# from system import Telegram  #IndividualAddress, GroupAddress,

FUNCTIONAL_MODULE_TYPES = ["button", "switch", "dimmer"]
SENSOR_TYPES = ["button", "brightness", "temperature", "humidity", "co2"]
ACTUATOR_TYPES = ["light", "heater", "cooler"]

class Device(ABC):
    """ Root Class module for KNX Devices (Sensors, Actuators and System devices)
    """
    def __init__(self, class_name, name, refid, individual_addr, default_status, dev_type): #The constructor is also a good place for imposing various checks on attribute values
        from system import check_device_config
        self.class_name, self.name, self.refid, self.individual_addr, self.status = check_device_config(class_name, name, refid, individual_addr, default_status)
        
        # List to store the different ga the device is linked to
        self.group_addresses = []

        # #TODO: not necessary because already included in device types:
        # if dev_type in ["actuator", "sensor", "sysdevice", "functional_module"]: #TODO: maybe create a config file, with the list of different types?
        #     self.dev_type = dev_type # usefull when we add device to rooms (e.g. to add a light to the light_soucres list)
        # else:
        #     logging.warning(f"Device type '{dev_type}' unknown")


    def is_enabled(self) -> bool:
        """True if the device is enabled (= active+connected) on the KNX bus"""
        return self.status

    def __repr__(self): # syntax to return when instance is called in the interactive python interpreter
        return f"Device({self.name!r}, {self.refid!r}, status:{self.is_enabled()!r}, {self.individual_addr!r})"

    def __str__(self): # syntax when instance is called with print()
        return f"Device : {self.name}  {self.refid}  status:{self.is_enabled()}  {self.individual_addr} "



    def send_telegram(self, payload, control_field):
        from system import Telegram # Import here to avoid circular import between system ,-> device_abstractions
        for group_address in self.group_addresses:
            telegram = Telegram(control_field, self.individual_addr, group_address, payload)
            #print("knxbus: ", self.knxbus.name)
            try:
                self.knxbus.transmit_telegram(telegram) # Simply send the telegram to all receiving devices connected to the group address
            except AttributeError:
                logging.warning(f"The device '{self.name}' is not connected to the bus, and thus cannot send telegrams")
            except:
                logging.warning(f"Transmission of the telegram from source '{telegram.source}' failed")
        return 0

    def connect_to(self, knxbus): # Connect to the KNX Bus, to be able to send telegrams
        self.knxbus = knxbus # can connect to only one
        # if knxbus not in self.knx_buses: # if we later implement multiple buses
        #     self.knx_buses.append(knxbus)

    def disconnect_from_knxbus(self): #, knxbus): # Remove the observer from the list
        try:
            del self.knxbus
        #     assert (),
        except AttributeError:
            logging.warning(f"The Functional Module '{self.name}' is not connected to this KNX bus, and thus cannot deconnect from it")



class FunctionalModule(Device, ABC):
    def __init__(self, class_name, name, refid, individual_addr, default_status, input_type):
        super().__init__(class_name, name, refid, individual_addr, default_status, "functional_module")
        # if input_type in FUNCTIONAL_MODULE_TYPES:
        #     self.input_type = input_type
        # else:
        #     logging.warning(f"Functional Module input type '{input_type}' unknown")


    @abstractmethod # must be implemented independantly for each particular functional module device
    def user_input(self):
        """ Interpret the user input (set button ON/OFF, set temperature,...)"""

    # should be an abstract method
    def receive_telegram(self, telegram):
        """Function to react to a received telegram from another device"""
        pass

class Sensor(Device, ABC):
    def __init__(self, class_name, name, refid, individual_addr, default_status, sensor_type):
        super().__init__(class_name, name, refid, individual_addr, default_status, "sensor")
        #TODO: necessary?
        # if sensor_type in SENSOR_TYPES:
        #     self.sensor_type = sensor_type  # usefull to differentiate light, temperature, humidity,...
        # else:
        #     logging.warning(f"Sensor type '{sensor_type}' unknown")


class Actuator(Device, ABC):
    def __init__(self, class_name, name, refid, individual_addr, default_status,  actuator_type, default_state=False):
        super().__init__(class_name, name, refid, individual_addr, default_status, "actuator")

        self.state = default_state #=False if not indicated, meaning OFF, some actuator can have a value in addition to their state (dimmed light)
        #TODO: necessary?
        # if actuator_type in ACTUATOR_TYPES:
        #     self.actuator_type = actuator_type
        # else:
        #     logging.warning(f"Actuator type '{actuator_type}' unknown")


    @abstractmethod # must be implemented independantly for each particular actuator state
    def update_state(self, telegram):
        """ Update its state when receiving a telegram"""



class SysDevice(Device, ABC):
    def __init__(self, class_name,  name, refid, individual_addr, default_status):
        super().__init__(class_name, name, refid, individual_addr, default_status, "sys_device")
