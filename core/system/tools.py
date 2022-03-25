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


