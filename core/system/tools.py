import math
#from .room import InRoomDevice not useful, but if used, put it on the class / function directly # to avoid circular import room <-> tools




class Location:
    """Class to represent location"""
    def __init__(self, room, x, y, z):
        self.room = room
        self.pos = (x, y, z)
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        str_repr =  f"Location: {self.room}: {self.pos}\n"
        return str_repr

    def __repr__(self):
        return f"Location in {self.room} is {self.pos}\n"


def compute_distance(source, sensor) -> float:
    """ Computes euclidian distance between a sensor and a actuator"""
    delta_x = abs(source.location.x - sensor.location.x)
    delta_y = abs(source.location.y - sensor.location.y)
    dist = math.sqrt(delta_x**2 + delta_y**2) # distance between light sources and brightness sensor
    return dist




class Telegram:
    """Class to represent KNX telegrams and store its fields"""
    def __init__(self, control_field, source_individual_addr, destination_group_addr, payload):
        self.control_field = control_field
        self.source = source_individual_addr
        self.destination = destination_group_addr
        self.payload = payload

    def __str__(self): # syntax when instance is called with print()
        return f" --- -- Telegram -- ---\n-control_field: {self.control_field} \n-source: {self.source}  \n-destination: {self.destination}  \n-payload: {self.payload}\n --- -------------- --- "
        #return f" --- -- Telegram -- ---\n {self.control} | {self.source} | {self.destination} | {self.payload}"



class IndividualAddress:
    """Class to represent individual addresses (virtual location on the KNX Bus)"""
    ## Magic Number
    def __init__(self, area, line, device): # area[4bits], line[4bits], device[8bits]
        try: # test if the group address has the correct format
            assert (area >= 0 and area <= 15 and line >= 0 and line <= 15 and device >= 0 and device <= 255), 'Individual address is out of bounds.'
        except AssertionError as msg:
            print(msg)
        self.area = area
        self.line = line
        self.device = device

    def __str__(self): # syntax when instance is called with print()
        return f" Individual Address(area:{self.area}, line:{self.line}, device:{self.device})"



class GroupAddress:
    """Class to represent group addresses (devices gathered by functionality)"""
    ## Magic Number

    def __init__(self, encoding_style, main, middle=0, sub=0):
        self.encoding_style = encoding_style
        if self.encoding_style == '3-levels': # main[5bits], middle[3bits], sub[8bits]
            try: # test if the group address has the correct format
                assert (main >= 0 and main <= 31 and middle >= 0 and middle <= 7 and sub >= 0 and sub <= 255), "[ERROR] '3-levels' group address is out of bounds.'"
            except AssertionError as msg:
                print(msg)
            self.main = main
            self.middle = middle
            self.sub = sub
        elif self.encoding_style == '2-levels': # main[5bits], sub[11bits]
            try: # test if the group address has the correct format
                assert (main >= 0 and main <= 31 and sub >= 0 and sub <= 2047), "[ERROR] '2-levels' group address is out of bounds."
            except AssertionError as msg:
                print(msg)
            self.main = main
            self.sub = sub
        elif self.encoding_style == 'free': # main[16bits]
            try: # test if the group address has the correct format
                assert (main >= 0 and main <= 65535), "[ERROR] 'free' style group address is out of bounds."
            except AssertionError as msg:
                print(msg)
            self.main = main

    def __str__(self): # syntax when instance is called with print()
        if self.encoding_style == '3-levels':
            return f" Group Address(main:{self.main}, middle:{self.middle}, sub:{self.sub})"
        elif self.encoding_style == '2-levels':
            return f" Group Address(main:{self.main}, sub:{self.sub})"
        elif self.encoding_style == 'free':
            return f" Group Address(main:{self.main}) "

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
        if self.main == ga_to_compare.main:
            if self.encoding_style == 'free':
                return True
            else: # if encoding style is 2 or 3-levels
                if self.sub == ga_to_compare.sub:
                    if self.encoding_style == '2-levels':
                        return True
                    else: # if encoding style is 3-levels
                        if self.middle == ga_to_compare.middle:
                            return True
                        else:
                            return False
