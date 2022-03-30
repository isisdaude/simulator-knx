"""
Gather the abstract class definitions for the simulated KNX devices.
"""

from abc import ABC, abstractmethod
# from system import Telegram  #IndividualAddress, GroupAddress,


class Device(ABC):
    """ Root Class module for KNX Devices (Sensors, Actuators and System devices)
    """
    def __init__(self, name, refid, individual_addr, default_status, dev_type): #The constructor is also a good place for imposing various checks on attribute values
        self.name = name
        self.refid = refid
        self.status: bool = default_status  # enable/disable status determine if sensor is activated or not, kind of power switch

        # Init addresses
        self.individual_addr = individual_addr

        #TODO: not necessary because already included in device types:
        if dev_type in ["actuator", "sensor", "sysdevice", "functional_module"]: #TODO: maybe create a config file, with the list of different types?
            self.dev_type = dev_type # usefull when we add device to rooms (e.g. to add a light to the light_soucres list)
        else:
            print("[ERROR] Device type unknown") # -> Cannot happen because we give th epossible types


    def is_enabled(self) -> bool:
        """True if the device is enabled (= active+connected) on the KNX bus"""
        return self.status

    def __repr__(self): # syntax to return when instance is called in the interactive python interpreter
        return f"Device({self.name!r}, {self.refid!r}, status:{self.is_enabled()!r}, {self.individual_addr!r})"

    def __str__(self): # syntax when instance is called with print()
        return f"Device : {self.name}  {self.refid}  status:{self.is_enabled()}  {self.individual_addr} "


class FunctionalModule(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status, input_type):
        super().__init__(name, refid, individual_addr, default_status, "functional_module")
        if input_type in ["button", "dimmer"]:
            self.input_type = input_type
        else:
            print("[ERROR] Input type unknown") #TODO: write an error handling code

        # Store the different ga the device is linked to
        self.group_addresses = []


    def send_telegram(self, payload, control_field):
        from system import Telegram # Import here to avoid circular import between system ,-> device_abstractions
        for group_address in self.group_addresses:
            telegram = Telegram(control_field, self.individual_addr, group_address, payload)
            #print("knxbus: ", self.knxbus.name)
            try:
                self.knxbus.transmit_telegram(telegram) # Simply send the telegram to all receiving devices connected to the group address
            except AttributeError:
                print(f"[ERROR] The device {self.name} is not connected to the bus, and thus cannot send telegrams")
            except:
                print(f"[ERROR] Transmission of the telegram from source ({telegram.source}) failed")
        return 0

    def connect_to(self, knxbus): # Connect to the KNX Bus, to be able to send telegrams
        self.knxbus = knxbus # can connect to only one 
        # if knxbus not in self.knx_buses: # if we later implement multiple buses
        #     self.knx_buses.append(knxbus)

    def deconnect_from(self): #, knxbus): # Remove the observer from the list
        try:
            del self.knxbus
        #     assert (), "This Functional Module is not connected to this KNX bus, and thus cannot deconnect from it"
        except AttributeError as msg:
            print(msg)



class Sensor(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status, sensor_type):
        super().__init__(name, refid, individual_addr, default_status, "sensor")
        self.group_address = 0 # sensors can communicate with only one group address
        #TODO: necessary?
        if sensor_type in ["button", "brightness", "temperature"]:
            self.sensor_type = sensor_type  # usefull to differentiate light, temperature, humidity,...
        else:
            print("[ERROR] Sensor type unknown")#TODO: write an error handling code


class Actuator(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status,  actuator_type, default_state=False):
        super().__init__(name, refid, individual_addr, default_status, "actuator")

        self.state = default_state #=False if not indicated, meaning OFF, some actuator can have a value in addition to their state (dimmed light)
        self.group_addresses = [] # Actuators can receive telegrams from multiple group addresses
        #TODO: necessary?
        if actuator_type in ["light", "heater", "cooler"]:
            self.actuator_type = actuator_type
        else:
            print("[ERROR] Actuator type unknown")


    @abstractmethod # must be implemented independantly for each particular actuator state
    def update_state(self, telegram):
        """ Update its state when receiving a telegram"""



class SysDevice(Device, ABC):
    def __init__(self, name, refid, individual_addr, default_status):
        super().__init__(name, refid, individual_addr, default_status, "sys_device")
