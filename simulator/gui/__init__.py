""" 
GUI Package to visualize the simulated KNX system in a graphical window. 
GUIWindow is used to initialize the Graphical window in simulator.py,
update_gui_window is called in room.py after updating sensors values.
"""

from .gui_knx import GUIWindow, update_gui_window
from .gui_config import ROOM_WIDTH, ROOM_LENGTH
