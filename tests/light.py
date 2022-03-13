#!/usr/bin/env python
#https://www.compuphase.com/electronics/candela_lumen.htm : relationship Lux & Lumen

from typing import List

class Device:
    name = None
    def __init__(self) -> None:
        pass

class Light(Device):
    # Lumen = light intensity, Lux = Lumen/sqmeter
    status = 0
    def turnOn(self):
        self.status = 1

    def turnOff(self):
        self.status = 0

    def getStatus(self):
        print("Status is " + str(self.status) + ", lamp is " + ("on" if self.status == 1 else "off") + ".")

    def lumentoLux(self, lm, area):
        ''' The conversion from Lumens to Lux given the surface area in squared meters '''
        return lm/area

    def luxtoLumen(self, lx, area):
        ''' The conversion from Lux to Lumen given the surface area in squared meters '''
        return area*lx


class LED(Light):
    lm = 800
    def __init__(self, name):
        super().__init__()
        self.name = name
    def __str__(self):
        return f"{self.name} is a LED-light and has {self.lm} lumens of brightness"
    def __repr__(self):
        return f"LED-Light {self.name}"

class Button(Device):
    pressed = 0

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name} is a button"

    def __repr__(self):
        return f"Button {self.name}"

    def press(self):
        if(self.pressed == 1):
            self.pressed = 0
        else:
            self.pressed = 1

    def getStatus(self):
        print("Status is " + str(self.pressed) + ", button is " + ("pressed" if self.status == 1 else "released") + ".")

class RDevice:
    dependencies = []
    address = None
    device: Device = None

    def __init__(self, device, x, y):
        self.device = device
        self.x = x
        self.y = y

    def impactsOn(self, other):
        self.dependencies.append(other)

    def trigger(self):
        if(type(self) is Button):
            Button(self).press()
            for d in self.dependencies:
                if(Button(self).pressed == 0):
                    Light(d).turnOff()
                else:
                    Light(d).turnOn()

    def showDependencies(self):
        print(f"{self} has impact on :")
        for d in self.dependencies:
            print("    " + str(d.__repr__()))

    def __str__(self):
        return f"{self.device.name}, at position {self.x} {self.y} in the room"

    def __repr__(self):
        return f"Device {self.device}"

class Room:

    devices: List[RDevice] = []

    def __init__(self, name, width, length):
        self.name = name
        self.width = width
        self.length = length

    def __str__(self):
        return f"{self.name} is a room of dimensions {self.width} x {self.length} m2"

    def __repr__(self):
        return f"Room {self.name}"

    def containsDevice(self,device):
        for d in self.devices:
            if(d.device == device):
                return True
        return False

    def addDevice(self, device, x, y):
        if(x < 0 or x > self.width or y < 0 or y > self.length):
            print("Cannot add a device that's beyond the room's size!")
        else:
            self.devices.append(RDevice(device, x, y))

    def getDevice(self, device: Device) -> RDevice:
        for d in self.devices:
            if(d.device == device):
                return d
        return None

    def addDependency(self, device: RDevice, other: RDevice):
        if(self.containsDevice(device) and self.containsDevice(other)):
            d1 = self.getDevice(device)
            d2 = self.getDevice(other)

            print(d1)
            print(d2)
            d1.impactsOn(d2)
            print(d1.dependencies)
            print(d2.dependencies)
            print(str(d1.device.name) + " now impacts " + str(d2.device.name) + " in " + str(self.name) + ".")
        else:
            print("Both devices are not in the same room, one cannot impact the other!")

    def showLinks(self):
        for d in self.devices:
            d.showDependencies()

    def area(self):
        return self.width * self.length

### EXAMPLE ###
bedroom = Room("bedroom", 10, 10)
button = Button("button")
light1 = LED("light1")
light2 = LED("light2")

bedroom.addDevice(button, 0, 0)
bedroom.addDevice(light1, 1, 1)
bedroom.addDevice(light2, 9, 9)

bedroom.addDependency(button, light1)
#bedroom.showLinks()
