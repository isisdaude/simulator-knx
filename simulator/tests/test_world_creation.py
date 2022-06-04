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
    utilization_factor = 0.52
    light_loss_factor = 0.8
    world = sim.World(width, length, height, speed_factor, system_dt, insulation, temp_out, hum_out, co2_out)
    assert hasattr(world, 'time')
    assert world.time.speed_factor == speed_factor
    assert hasattr(world, 'room_insulation')
    assert world.__room_insulation == insulation ### TODO prvate attr name
    assert (world.temp_out, world.hum_out, world.co2_out) == (temp_out, hum_out, co2_out)
    assert hasattr(world.time, 'update_rule_ratio')
    assert world.time.update_rule_ratio == update_rule_ratio
    assert hasattr(world, 'ambient_temperature')
    assert world.ambient_temperature.update_rule_ratio == update_rule_ratio ### TODO prvate attr name
    assert world.ambient_temperature.temperature_in == world.ambient_temperature.outside_temperature == temp_out # NOTE: to change if temp init ≠ temp_out in room
    assert world.ambient_temperature.__room_insulation == insulation ### TODO prvate attr name
    assert world.ambient_temperature.__room_volume == room_volume ### TODO prvate attr name
    assert hasattr(world, 'ambient_light')
    assert world.ambient_light.__.utilization_factor == utilization_factor
    assert world.ambient_light.__light_loss_factor == light_loss_factor
    assert hasattr(world, 'ambient_humidity')
    assert world.ambient_humidity.temp == temp_out # NOTE: to change if temp init ≠ temp_out in room
    assert world.ambient_humidity.humidity_out == hum_out
    assert world.ambient_humidity.__room_insulation == insulation ### TODO prvate attr name
    assert world.ambient_humidity.__saturation_vapour_pressure == p_sat
    assert world.ambient_humidity.humidity == 35 # NOTE: to change if humidity init is provided
    assert world.ambient_humidity.__vapor_pressure == vapor_pressure
    assert world.ambient_humidity.update_rule_ratio == update_rule_ratio ### TODO prvate attr name
    assert hasattr(world, 'ambient_co2')
    assert world.ambient_co2.__co2_in == 800 # NOTE: to change if co2 init is provided
    assert world.ambient_co2.outside_co2 == co2_out
    assert world.ambient_co2.__room_insulation == insulation ### TODO prvate attr name
    assert world.ambient_co2.update_rule_ratio == update_rule_ratio ### TODO prvate attr name
    assert hasattr(world, 'ambient_world')


# CONFIG_PATH = "./docs/config/config_test_update_world.json"
# def test_correct_world_update():
#     room1 = system.configure_system_from_file(CONFIG_PATH, test_mode=True)[0]


#     # TODO: Must test with a config file
#     assert True

