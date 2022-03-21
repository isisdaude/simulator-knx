import math
from core.system.room import InRoomDevice

class Location:
    """Class to represent location"""
    def __init__(self, room, x, y):
        self.room = room
        self.pos = (x, y)
        self.x = x
        self.y = y

    def __str__(self):
        str_repr =  f"Location: {self.room}: {self.pos}\n"
        return str_repr

    def __repr__(self):
        return f"Location in {self.room} is {self.pos}\n"


def compute_distance(source: InRoomDevice, sensor: InRoomDevice) -> float:
    """ Computes euclidian distance between a sensor and a actuator"""
    delta_x = abs(source.location.x - sensor.location.x)
    delta_y = abs(source.location.y - sensor.location.y)
    dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor
    return dist
