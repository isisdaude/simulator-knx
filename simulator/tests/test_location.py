#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import devices as dev

def test_correct_location():
    simulation_speed_factor = 180
    room1 = system.Room("bedroom1", 20, 20, 3, simulation_speed_factor, '3-levels')
    