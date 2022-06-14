"""
Class definitions usefull to simulate the KNX system: Location, Individual and Group Address, and Windows (very similar to a device)
"""

import math
from typing import Union, Tuple

import devices as dev

ROOM_WIDTH, ROOM_LENGTH = 1000, 800  # GUI dimensions of room,


class Location:
    """Class to represent location"""

    def __init__(self, room, x: float, y: float, z: float) -> None:
        """
        Initialization of a location object.

        room : Room object
        """
        from tools import check_location

        self.room = room
        self.min_x, self.max_x = 0, self.room.width
        self.min_y, self.max_y = 0, self.room.length
        self.min_z, self.max_z = 0, self.room.height
        self.bounds = [
            [self.min_x, self.max_x],
            [self.min_y, self.max_y],
            [self.min_z, self.max_z],
        ]
        # Check that location is correct, replace in the room if out of bounds
        self.x, self.y, self.z = check_location(self.bounds, x, y, z)
        self.pos = (self.x, self.y, self.z)

    def __str__(self):
        str_repr = f"Location: {self.room.name}: {self.pos}\n"
        return str_repr

    def __repr__(self):
        return f"Location in {self.room.name} is {self.pos}\n"


class IndividualAddress:
    """Class to represent individual addresses (virtual location on the KNX Bus)"""

    def __init__(
        self, area: Union[str, int], line: Union[str, int], main: Union[str, int]
    ) -> None:
        from tools import check_individual_address

        self.area, self.line, self.device = check_individual_address(area, line, main)
        self.ia_str = ".".join([str(self.area), str(self.line), str(self.device)])

    def __eq__(self, other):
        return (
            self.area == other.area
            and self.line == other.line
            and self.device == self.device
        )

    def __str__(self):
        return self.ia_str

    def __repr__(self):
        return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"

    def __repr__(self) -> str:
        return f"{self.area}.{self.line}.{self.device}"


class GroupAddress:
    """Class to represent group addresses (devices gathered by functionality)"""

    def __init__(
        self, encoding_style: str, main: int, middle: int = 0, sub: int = 0
    ) -> None:
        """
        Initialization of a group address object.

        encoding_style should be 'free', '2-levels' or '3-levels'.
        """
        self.encoding_style = encoding_style
        if self.encoding_style == "3-levels":
            self.main = main
            self.middle = middle
            self.sub = sub
            self.name = "/".join((str(main), str(middle), str(sub)))
        elif self.encoding_style == "2-levels":
            self.main = main
            self.sub = sub
            self.name = "/".join((str(main), str(sub)))
        elif self.encoding_style == "free":
            self.main = main
            self.name = str(main)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, ga_to_compare):  # ga_to_compare : GroupAddress
        return self.__str__() == str(ga_to_compare)


class Window:
    """Class to represent room windows."""

    def __init__(
        self,
        window_name: str,
        room,
        wall: str,
        location_offset: float,
        size: Tuple[float, float],
        test_mode: bool = False,
    ) -> None:  # room : Room
        """
        Initialization of a window object.
        in GUI, window img size is 300p wide, for a room of 12.5m=1000p, it corresponds to 3.75m
        necessary to scale the window if different size, 
        e.g. if window size = 1m, scale factor x(horizontal) ou y(vertical) = 1/3.75

        wall : 'north', 'south', 'east' or 'west', indicate where th winwod is located
        location_offset : location in meters from beginning of wall 
        (left side of north/south walls, bottom side of east/west walls)
        size : window [width, height] in meters
        """
        from tools import check_window

        self.WINDOW_PIXEL_SIZE = 300  # from png img library (folder png_simulator/)
        ROOM_PIXEL_WIDTH = ROOM_WIDTH
        self.location_offset = location_offset

        self.initial_size = room.width * self.WINDOW_PIXEL_SIZE / ROOM_PIXEL_WIDTH
        self.name = window_name
        self.wall, self.window_loc, self.size = check_window(
            wall, location_offset, size, room
        )
        if self.wall is None:
            raise ValueError("Window object cannot be created, check the error logs")

        self.beam_angle = 180  # arbitrary  but realistic
        self.state = True  # state to be compliant with LighActuator's attributes
        self.state_ratio = 100  # change if blinds implemented (not the case for now)
        # for the GUI display
        if self.wall in ["north", "south"]:
            self.scale_x = self.size[0] / self.initial_size
        if self.wall in ["east", "west"]:
            self.scale_y = self.size[0] / self.initial_size

    def max_lumen_from_out_lux(self, out_lux: float) -> None:
        """Compute max_lumen value based on out luminosity in lux and window's area."""
        self.max_lumen = out_lux * math.prod(self.size)

    def effective_lumen(self) -> float:
        """Lumen quantity adjusted with the state ratio (% of source's max lumens) represented by blinds (if implemented)"""
        return 0.2 * self.max_lumen + 0.8 * self.max_lumen * (
            self.state_ratio / 100
        )  # 20% of outdoor light will pass even with blinds closed
