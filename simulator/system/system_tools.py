"""
Module thar define usefull classes to simulate the KNX system: Location, Individual and Group Address, and Windows (very similar to a device)
"""

import math

import devices as dev


class Location:
    """Class to represent location"""
    def __init__(self, room, x, y, z):
        from tools import check_location
        self.room = room
        self.min_x, self.max_x = 0, self.room.width
        self.min_y, self.max_y = 0, self.room.length
        self.min_z, self.max_z = 0, self.room.height
        self.bounds = [[ self.min_x, self.max_x], [self.min_y, self.max_y], [self.min_z, self.max_z]]
        # Check that location is correct, replace in the room if out of bounds
        self.x, self.y, self.z = check_location(self.bounds, x, y, z) # to updaqte, erase and recreate
        self.pos = (self.x, self.y, self.z)

    # def update_location(self, new_x=None, new_y=None, new_z=None):
    #     from .check_tools import check_location
    #     x = (new_x or self.x)
    #     y = (new_y or self.y)
    #     z = (new_z or self.z)
    #     self.x, self.y, self.z = check_location(self.bounds, x, y, z)
    #     self.pos = (self.x, self.y, self.z)

    def __str__(self):
        str_repr =  f"Location: {self.room.name}: {self.pos}\n"
        return str_repr

    def __repr__(self):
        return f"Location in {self.room.name} is {self.pos}\n"


class IndividualAddress:
    """Class to represent individual addresses (virtual location on the KNX Bus)"""
    ## Magic Number
    def __init__(self, area, line, main): # area[4bits],  device[8bits], line[4bits]
        from tools import check_individual_address
        self.area, self.line, self.device = check_individual_address(area, line, main)
        self.ia_str = '.'.join([str(self.area), str(self.line), str(self.device)])

    def __eq__(self, other):
        return (self.area == other.area and
                self.line == other.line and
                self.device == self.device)

    def __str__(self): 
        return self.ia_str

    def __repr__(self):
        return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"

    def __repr__(self) -> str:
        return f"{self.area}.{self.line}.{self.device}"
    

class GroupAddress:
    """Class to represent group addresses (devices gathered by functionality)"""
    ## Magic Number

    def __init__(self, encoding_style, main, middle=0, sub=0):
        self.encoding_style = encoding_style
        if self.encoding_style == '3-levels': # main[5bits], middle[3bits], sub[8bits]
            
            self.main = main
            self.middle = middle
            self.sub = sub
            self.name = "/".join((str(main), str(middle), str(sub)))
        elif self.encoding_style == '2-levels': # main[5bits], sub[11bits]
            
            self.main = main
            self.sub = sub
            self.name = "/".join((str(main), str(sub)))
        elif self.encoding_style == 'free': # main[16bits]
            
            self.main = main
            self.name = str(main)

    def __str__(self): 
        return self.name
        

    def __repr__(self): 
        return self.name
        

# __eq__() or __lt__(), "is" operator to check if an instances are of the same type
    def __lt__(self, ga_to_compare): # self is the group addr ref, we want to check if self is smaller than the other ga
        if self.encoding_style == '3-levels':
            ga_ref = self.sub + self.middle<<8 + self.main<<11
            ga_test = ga_to_compare.sub + ga_to_compare.middle<<8 + ga_to_compare.main<<11
            return (ga_ref < ga_test)
        if self.encoding_style == '2-levels':
            ga_ref = self.sub + self.main<<11
            ga_test = ga_to_compare.sub + ga_to_compare.main<<11
            return (ga_ref < ga_test)
        if self.encoding_style == 'free':
            return (self.main < ga_to_compare.main)

    def __eq__(self, ga_to_compare):
        return self.__str__() == str(ga_to_compare)



class Window:
    """Class to represent windows"""
    def __init__(self, window_name, room, wall, location_offset, size):
        from tools import check_window
        ## window img size is 300p wide, for a room of 12.5m=1000p, it corresponds to 3.75m
        ## must scale the window if different size, e.g. if window size = 1m, scale factor x(horizontal) ou y(vertical) = 1/3.75``
        self.WINDOW_PIXEL_SIZE = 300
        ROOM_PIXEL_WIDTH = 1000 ## TODO: take this constant from a config file
        # to copy window instance in compute_distance_from_window()
        self.location_offset = location_offset

        self.initial_size = room.width * self.WINDOW_PIXEL_SIZE / ROOM_PIXEL_WIDTH # 3.75m if room width=12.5 for 1000 pixels
        self.name = window_name
        self.class_name = 'Window'
        self.wall, self.window_loc, self.size  = check_window(wall, location_offset, size, room)   # size[width, height] in meters
        if self.wall is None: # failed check
            raise ValueError("Window object cannot be created, check the error logs")

        self.beam_angle = 180 # arbitrary  but realistic
        self.state = True # state to be compliant with LighActuator's attributes
        self.state_ratio = 100 # change if blinds implemented

        # for the GUI display
        if self.wall in ['north', 'south']:
            self.scale_x = self.size[0] / self.initial_size
        if self.wall in ['east', 'west']:
            self.scale_y = self.size[0] / self.initial_size
        # self.location_out_offset =  # offset for location to consider light source point outside of room, so that with a certain beamangle, all light is considered

    def max_lumen_from_out_lux(self, out_lux):
        self.max_lumen = out_lux * math.prod(self.size) # out_lux*window_area
    
    def effective_lumen(self):
        # Lumen quantity rationized with the state ratio (% of source's max lumens)
        return 0.2*self.max_lumen + 0.8*self.max_lumen*(self.state_ratio/100) # 20% of outdoor light will pass even with blinds closed



    