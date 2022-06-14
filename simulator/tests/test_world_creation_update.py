""" test World creation, updates and state changes"""
import pytest
import logging
from datetime import timedelta, datetime

import system
import tools
import world
import devices as dev


def test_correct_world_creation():
    speed_factor = 360
    system_dt = 1
    update_rule_ratio = 0.1
    insulation = "good"
    temp_out, hum_out, co2_out = 20.0, 35, 400
    temp_in, hum_in, co2_in = 20.0, 35, 800
    datetime = "2022/06/13/11/00"
    weather = "clear"
    p_sat = 2339.32074966  # NOTE: or temp = 20.0 and hum = 35
    vapor_pressure = 818.76226238  # NOTE: for temp = 20.0 and hum = 35
    utilization_factor = 0.52
    light_loss_factor = 0.8
    world_object = world.World(
        speed_factor,
        system_dt,
        datetime,
        weather,
        insulation,
        temp_out,
        hum_out,
        co2_out,
        temp_in,
        hum_in,
        co2_in,
    )
    assert hasattr(world_object, "time")
    assert world_object.time.speed_factor == speed_factor
    assert hasattr(world_object, "_World__room_insulation")
    assert world_object._World__room_insulation == insulation
    assert (
        world_object._World__temp_out,
        world_object._World__hum_out,
        world_object._World__co2_out,
    ) == (temp_out, hum_out, co2_out)
    assert hasattr(world_object.time, "update_rule_ratio")
    assert world_object.time.update_rule_ratio == update_rule_ratio
    assert hasattr(world_object, "ambient_temperature")
    assert (
        world_object.ambient_temperature._AmbientTemperature__update_rule_ratio
        == update_rule_ratio
    )
    assert (
        world_object.ambient_temperature._AmbientTemperature__temperature_in == temp_in
    )
    assert world_object.ambient_temperature.temperature_out == temp_out
    assert (
        world_object.ambient_temperature._AmbientTemperature__room_insulation
        == insulation
    )
    assert hasattr(world_object, "ambient_light")
    assert (
        world_object.ambient_light._AmbientLight__utilization_factor
        == utilization_factor
    )
    assert (
        world_object.ambient_light._AmbientLight__light_loss_factor == light_loss_factor
    )
    assert hasattr(world_object, "ambient_humidity")
    assert world_object.ambient_humidity._AmbientHumidity__temperature_out == temp_out
    assert world_object.ambient_humidity.humidity_out == hum_out
    assert world_object.ambient_humidity._AmbientHumidity__room_insulation == insulation
    assert (
        world_object.ambient_humidity._AmbientHumidity__saturation_vapour_pressure_in
        == p_sat
    )
    assert (
        world_object.ambient_humidity._AmbientHumidity__saturation_vapour_pressure_out
        == p_sat
    )
    assert world_object.ambient_humidity._AmbientHumidity__humidity_in == hum_in
    assert (
        world_object.ambient_humidity._AmbientHumidity__vapor_pressure_in
        == vapor_pressure
    )
    assert (
        world_object.ambient_humidity._AmbientHumidity__vapor_pressure_out
        == vapor_pressure
    )
    assert (
        world_object.ambient_humidity._AmbientHumidity__update_rule_ratio
        == update_rule_ratio
    )
    assert hasattr(world_object, "ambient_co2")
    assert world_object.ambient_co2._AmbientCO2__co2_in == co2_in
    assert world_object.ambient_co2.co2_out == co2_out
    assert world_object.ambient_co2._AmbientCO2__room_insulation == insulation
    assert world_object.ambient_co2._AmbientCO2__update_rule_ratio == update_rule_ratio

    weathers = ["clear", "overcast", "dark"]
    datetimes = [
        "2022/06/13/11/00",
        "2022/06/13/19/30",
        "2022/06/13/23/00",
        "2022/06/13/03/30",
    ]
    for dt in datetimes:
        for wth in weathers:
            world_object_weather = world.World(
                speed_factor,
                system_dt,
                dt,
                wth,
                insulation,
                temp_out,
                hum_out,
                co2_out,
                temp_in,
                hum_in,
                co2_in,
            )


def test_world_configfile_creation_and_update():
    config_path = "config/config_test_config.json"
    speed_factor = 180
    system_dt = 1
    update_rule_ratio = system_dt * speed_factor / 3600
    temp_out = 20.0
    temp_in = 25.0
    hum_out = 35.0
    hum_in = 50.0
    p_sat_out = 2339.32074966  # NOTE: or temp = 20.0 and hum = 35
    vapor_pressure_out = 818.76226238  # NOTE: for temp = 20.0 and hum = 35
    p_sat_in = 3169.95003067  # NOTE: or temp = 25.0 and hum = 50
    vapor_pressure_in = 1584.97501534  # NOTE: for temp = 25.0 and hum = 50
    co2_out = 300.0
    co2_in = 800.0
    dt = "2022/06/13/11/00".split("/")
    date_time = datetime(
        year=int(dt[0]),
        month=int(dt[1]),
        day=int(dt[2]),
        hour=int(dt[3]),
        minute=int(dt[4]),
    )
    time_of_day = "sun"
    weather = "clear"
    lux_out = 10752
    brightness = 3877.0
    insulation = "average"
    humiditysoil = 10.0
    presence = False

    button1 = dev.Button("button1", system.IndividualAddress(0, 0, 20))
    dimmer1 = dev.Dimmer("dimmer1", system.IndividualAddress(0, 0, 22))
    led1 = dev.LED(
        "led1", system.IndividualAddress(0, 0, 1)
    )  # Area 0, Line 0, Device 0
    heater1 = dev.Heater(
        "heater1", system.IndividualAddress(0, 0, 11), 400
    )  # 400W max power
    switch1 = dev.Switch("switch1", system.IndividualAddress(0, 0, 44))
    brightness1 = dev.Brightness("brightness1", system.IndividualAddress(0, 0, 5))
    humiditysoil1 = dev.HumiditySoil(
        "humiditysoil1", system.IndividualAddress(0, 0, 34)
    )
    airsensor1 = dev.AirSensor("airsensor1", system.IndividualAddress(0, 0, 55))
    presencesensor1 = dev.PresenceSensor(
        "presencesensor1", system.IndividualAddress(0, 0, 66)
    )

    room_conf, system_dt = tools.configure_system_from_file(
        config_path, system_dt=system_dt, test_mode=True
    )

    ir_button1 = system.InRoomDevice(button1, room_conf, 0.5, 3.1, 1.0)
    ir_dimmer1 = system.InRoomDevice(dimmer1, room_conf, 0.525, 7.6375, 1.0)
    ir_led1 = system.InRoomDevice(led1, room_conf, 5.7125, 7.5875, 1.0)
    ir_heater1 = system.InRoomDevice(heater1, room_conf, 1.5625, 3.0375, 1.0)
    ir_switch1 = system.InRoomDevice(switch1, room_conf, 4.1625, 1.5375, 1.0)
    ir_brightness1 = system.InRoomDevice(brightness1, room_conf, 11.6625, 5.8, 1.0)
    ir_humiditysoil1 = system.InRoomDevice(humiditysoil1, room_conf, 7.25, 1.1875, 1.0)
    ir_airsensor1 = system.InRoomDevice(airsensor1, room_conf, 0.5375, 5.5, 1.0)
    ir_presencesensor1 = system.InRoomDevice(
        presencesensor1, room_conf, 5.8375, 4.1, 1.0
    )

    window1 = system.Window("window1", room_conf, "north", 4, [2, 1.5], test_mode=True)
    ir_window1 = system.InRoomDevice(window1, room_conf, 4, 10, 1.5)

    # Initial state
    room_conf.update_world(
        interval=system_dt, gui_mode=False
    )  # first_update flag is True after system initialization, no update is done simlpy set sensors values
    world_conf = room_conf.world
    assert hasattr(room_conf, "world")
    assert hasattr(world_conf, "time")
    assert world_conf.time.simulation_time() == 0
    assert world_conf.time.simulation_time(str_mode=True) == "0:00:00"
    assert world_conf.time.update_rule_ratio == update_rule_ratio
    assert world_conf.time._Time__system_dt == system_dt
    assert world_conf.time._Time__datetime_init == date_time
    assert hasattr(world_conf, "ambient_light")
    assert world_conf.ambient_light._AmbientLight__weather == weather
    assert world_conf.ambient_light._AmbientLight__lux_out == lux_out
    assert world_conf.ambient_light._AmbientLight__time_of_day == time_of_day
    assert ir_led1 in world_conf.ambient_light._AmbientLight__light_sources
    assert ir_window1 in world_conf.ambient_light._AmbientLight__windows
    assert ir_brightness1 in world_conf.ambient_light._AmbientLight__light_sensors
    assert hasattr(world_conf, "ambient_temperature")
    assert world_conf.ambient_temperature._AmbientTemperature__temperature_in == temp_in
    assert world_conf.ambient_temperature.temperature_out == temp_out
    assert (
        world_conf.ambient_temperature._AmbientTemperature__room_insulation
        == insulation
    )
    assert (
        world_conf.ambient_temperature._AmbientTemperature__update_rule_ratio
        == update_rule_ratio
    )
    assert (
        ir_heater1 in world_conf.ambient_temperature._AmbientTemperature__temp_sources
    )
    assert (
        ir_airsensor1
        in world_conf.ambient_temperature._AmbientTemperature__temp_sensors
    )
    assert hasattr(world_conf, "ambient_humidity")
    assert world_conf.ambient_humidity._AmbientHumidity__humidity_in == hum_in
    assert world_conf.ambient_humidity.humidity_out == hum_out
    assert world_conf.ambient_humidity._AmbientHumidity__temperature_in == temp_in
    assert world_conf.ambient_humidity._AmbientHumidity__temperature_out == temp_out
    assert world_conf.ambient_humidity._AmbientHumidity__room_insulation == insulation
    assert (
        world_conf.ambient_humidity._AmbientHumidity__update_rule_ratio
        == update_rule_ratio
    )
    assert (
        world_conf.ambient_humidity._AmbientHumidity__saturation_vapour_pressure_out
        == p_sat_out
    )
    assert (
        world_conf.ambient_humidity._AmbientHumidity__saturation_vapour_pressure_in
        == p_sat_in
    )
    assert (
        world_conf.ambient_humidity._AmbientHumidity__vapor_pressure_out
        == vapor_pressure_out
    )
    assert (
        world_conf.ambient_humidity._AmbientHumidity__vapor_pressure_in
        == vapor_pressure_in
    )
    assert (
        ir_airsensor1 in world_conf.ambient_humidity._AmbientHumidity__humidity_sensors
    )
    assert hasattr(world_conf, "ambient_co2")
    assert world_conf.ambient_co2._AmbientCO2__co2_in == co2_in
    assert world_conf.ambient_co2.co2_out == co2_out
    assert world_conf.ambient_co2._AmbientCO2__room_insulation == insulation
    assert world_conf.ambient_co2._AmbientCO2__update_rule_ratio == update_rule_ratio
    assert ir_airsensor1 in world_conf.ambient_co2._AmbientCO2__co2_sensors
    assert hasattr(world_conf, "soil_moisture")
    assert (
        world_conf.soil_moisture._SoilMoisture__update_rule_ratio == update_rule_ratio
    )
    assert (
        ir_humiditysoil1 in world_conf.soil_moisture._SoilMoisture__humiditysoil_sensors
    )
    assert hasattr(world_conf, "presence")
    assert world_conf.presence.presence == False
    assert ir_presencesensor1 in world_conf.presence._Presence__presence_sensors

    system_brightness1 = world_conf.ambient_light._AmbientLight__light_sensors[
        world_conf.ambient_light._AmbientLight__light_sensors.index(ir_brightness1)
    ].device
    assert round(system_brightness1.brightness, 1) == brightness
    system_airsensor1 = world_conf.ambient_co2._AmbientCO2__co2_sensors[
        world_conf.ambient_co2._AmbientCO2__co2_sensors.index(ir_airsensor1)
    ].device
    assert round(system_airsensor1.temperature, 1) == temp_in
    assert round(system_airsensor1.humidity, 2) == hum_in
    assert int(system_airsensor1.co2) == co2_in
    system_humiditysoil1 = world_conf.soil_moisture._SoilMoisture__humiditysoil_sensors[
        world_conf.soil_moisture._SoilMoisture__humiditysoil_sensors.index(
            ir_humiditysoil1
        )
    ].device
    assert system_humiditysoil1.humiditysoil == humiditysoil
    system_presence1 = world_conf.presence._Presence__presence_sensors[
        world_conf.presence._Presence__presence_sensors.index(ir_presencesensor1)
    ].device
    assert system_presence1.state == presence
    # Update World state
    room_conf.update_world(
        interval=system_dt, gui_mode=False
    )  # second update change the value from one system_dt
    new_temp_in = 24.0
    new_hum_in = 52.51
    new_co2_in = 793
    new_p_sat_in = 2985.81505025  # NOTE: or temp = 24.0 and hum = 52.51
    new_vapor_pressure_in = 1567.7352283984  # NOTE: for temp = 24.0 and hum = 52.51
    new_simtime = "0:03:00"
    # Time
    updated_datetime = date_time + timedelta(seconds=system_dt * speed_factor)
    assert world_conf.time.date_time == updated_datetime
    assert world_conf.time.simulation_time(str_mode=True) == new_simtime
    # Brightness
    assert round(system_brightness1.brightness, 1) == brightness
    # Temperature
    assert (
        world_conf.ambient_temperature._AmbientTemperature__temperature_in
        == new_temp_in
    )
    assert round(system_airsensor1.temperature, 1) == new_temp_in
    # Humidity
    assert (
        round(world_conf.ambient_humidity._AmbientHumidity__humidity_in, 2)
        == new_hum_in
    )
    assert (
        world_conf.ambient_humidity._AmbientHumidity__saturation_vapour_pressure_in
        == new_p_sat_in
    )
    assert (
        world_conf.ambient_humidity._AmbientHumidity__vapor_pressure_in
        == new_vapor_pressure_in
    )
    assert round(system_airsensor1.humidity, 2) == new_hum_in
    # CO2
    assert int(world_conf.ambient_co2._AmbientCO2__co2_in) == new_co2_in
    assert system_airsensor1.co2 == new_co2_in
    # Presence and humidity did not change
    assert system_presence1.state == presence
    assert system_humiditysoil1.humiditysoil == humiditysoil
