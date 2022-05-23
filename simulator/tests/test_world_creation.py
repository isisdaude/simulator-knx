#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import simulation as sim


def test_correct_world_creation():
    width, length, height = 12.5, 10, 3
    room_volume = 12.5*10*3
    speed_factor = 360
    system_dt = 1
    update_rule_ratio = 0.1
    insulation = 'good'
    temp_out, hum_out, co2_out = 20.0, 55, 300
    p_sat = 2339.32074966 # NOTE: to change if temp init ≠ 20.0
    vapor_pressure = 818.76226238 # NOTE: to change if temp init ≠ 20.0 and hum inti ≠ 35
    world = sim.World(width, length, height, speed_factor, system_dt, insulation, temp_out, hum_out, co2_out)
    assert hasattr(world, 'time')
    assert world.time.speed_factor == speed_factor
    assert hasattr(world, 'room_insulation')
    assert world.room_insulation == insulation
    assert (world.temp_out, world.hum_out, world.co2_out) == (temp_out, hum_out, co2_out)
    assert hasattr(world, 'update_rule_ratio')
    assert world.time.update_rule_ratio == update_rule_ratio
    assert hasattr(world, 'ambient_temperature')
    assert world.ambient_temperature.update_rule_ratio == update_rule_ratio
    assert world.ambient_temperature.temperature == world.ambient_temperature.outside_temperature == temp_out # NOTE: to change if temp init ≠ temp_out in room
    assert world.ambient_temperature.room_insulation == insulation
    assert world.ambient_temperature.room_volume == room_volume
    assert hasattr(world, 'ambient_light')
    assert hasattr(world, 'ambient_humidity')
    assert world.ambient_humidity.temp == temp_out # NOTE: to change if temp init ≠ temp_out in room
    assert world.ambient_humidity.humidity_out == hum_out
    assert world.ambient_humidity.room_insulation == insulation
    assert world.ambient_humidity.saturation_vapour_pressure == p_sat
    assert world.ambient_humidity.humidity == 35 # NOTE: to change if humidity init is provided
    assert world.ambient_humidity.vapor_pressure == vapor_pressure
    assert world.ambient_humidity.update_rule_ratio == update_rule_ratio
    assert hasattr(world, 'ambient_co2')
    assert world.ambient_co2.co2level == 800 # NOTE: to change if co2 init is provided
    assert world.ambient_co2.outside_co2 == co2_out
    assert world.ambient_co2.room_insulation == insulation
    assert world.ambient_co2.update_rule_ratio == update_rule_ratio
    assert hasattr(world, 'ambient_world')


# CONFIG_PATH = "./docs/config/config_test_update_world.json"
# def test_correct_world_update():
#     room1 = system.configure_system_from_file(CONFIG_PATH, test_mode=True)[0]


#     # TODO: Must test with a config file
#     assert True

