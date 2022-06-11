#pylint: disable=[W0223, C0301, C0114, C0115, C0116]
import pytest
import logging

import system
import world


def test_correct_world_creation():
    width, length, height = 12.5, 10, 3
    room_volume = 12.5*10*3
    speed_factor = 360
    system_dt = 1
    update_rule_ratio = 0.1
    insulation = 'good'
    temp_out, hum_out, co2_out = 20.0, 55, 400
    temp_in, hum_in, co2_in = 25.0, 45, 800
    datetime = "today"
    weather="clear"
    p_sat_out = 2339.32074966 # NOTE: to change if temp init ≠ 20.0
    vapor_pressure = 818.76226238 # NOTE: to change if temp init ≠ 20.0 and hum inti ≠ 35
    utilization_factor = 0.52
    light_loss_factor = 0.8
    world_object = world.World(width, length, height, speed_factor, system_dt, insulation, temp_out, hum_out, co2_out, temp_in, hum_in, co2_in, datetime, weather)
    assert hasattr(world_object, 'time')
    assert world_object.time.speed_factor == speed_factor
    assert hasattr(world_object, '_World__room_insulation')
    assert world_object._World__room_insulation == insulation ### TODO prvate attr name
    assert (world_object._World__temp_out, world_object._World__hum_out, world_object._World__co2_out) == (temp_out, hum_out, co2_out)
    assert hasattr(world_object.time, 'update_rule_ratio')
    assert world_object.time.update_rule_ratio == update_rule_ratio
    assert hasattr(world_object, 'ambient_temperature')
    assert world_object.ambient_temperature._AmbientTemperature__update_rule_ratio == update_rule_ratio ### TODO prvate attr name
    assert world_object.ambient_temperature._AmbientTemperature__temperature_in == temp_in
    assert world_object.ambient_temperature.temperature_out == temp_out # NOTE: to change if temp init ≠ temp_out in room
    assert world_object.ambient_temperature._AmbientTemperature__room_insulation == insulation ### TODO prvate attr name
    # assert world_object.ambient_temperature.__room_volume == room_volume ### TODO prvate attr name
    assert hasattr(world_object, 'ambient_light')
    assert world_object.ambient_light._AmbientLight__utilization_factor == utilization_factor
    assert world_object.ambient_light._AmbientLight__light_loss_factor == light_loss_factor
    assert hasattr(world_object, 'ambient_humidity')
    assert world_object.ambient_humidity._AmbientHumidity__temperature_out == temp_out # NOTE: to change if temp init ≠ temp_out in room
    assert world_object.ambient_humidity.humidity_out == hum_out
    assert world_object.ambient_humidity._AmbientHumidity__room_insulation == insulation ### TODO prvate attr name
    # assert world_object.ambient_humidity._AmbientHumidity__saturation_vapour_pressure_in == p_sat
    # assert world_object.ambient_humidity.saturation_vapour_pressure_out == p_sat_out
    assert world_object.ambient_humidity._AmbientHumidity__humidity_in == hum_in # NOTE: to change if humidity init is provided
    # assert world_object.ambient_humidity._AmbientHumidity__vapor_pressure == vapor_pressure
    assert world_object.ambient_humidity._AmbientHumidity__update_rule_ratio == update_rule_ratio ### TODO prvate attr name
    assert hasattr(world_object, 'ambient_co2')
    assert world_object.ambient_co2._AmbientCO2__co2_in == co2_in # NOTE: to change if co2 init is provided
    assert world_object.ambient_co2.co2_out == co2_out
    assert world_object.ambient_co2._AmbientCO2__room_insulation == insulation ### TODO prvate attr name
    assert world_object.ambient_co2._AmbientCO2__update_rule_ratio == update_rule_ratio ### TODO prvate attr name
    # assert hasattr(world_object, 'ambient_world')


# CONFIG_PATH = "./config/config_test_update_world.json"
# def test_correct_world_update():
#     room1 = system.configure_system_from_file(CONFIG_PATH, test_mode=True)[0]


#     # TODO: Must test with a config file
#     assert True

