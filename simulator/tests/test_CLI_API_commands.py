""" Test CLI and API commands"""
import sys

import pytest
from _pytest.logging import LogCaptureFixture
from time import sleep

import system
import tools
import devices as dev


button1 = dev.Button("button1", system.IndividualAddress(0, 0, 20))
dimmer1 = dev.Dimmer("dimmer1", system.IndividualAddress(0, 0, 22))
led1 = dev.LED("led1", system.IndividualAddress(0, 0, 1))  # Area 0, Line 0, Device 0
heater1 = dev.Heater(
    "heater1", system.IndividualAddress(0, 0, 11), 400
)  # 400W max power
switch1 = dev.Switch("switch1", system.IndividualAddress(0, 0, 44))
brightness1 = dev.Brightness("brightness1", system.IndividualAddress(0, 0, 5))
humiditysoil1 = dev.HumiditySoil("humiditysoil1", system.IndividualAddress(0, 0, 34))
airsensor1 = dev.AirSensor("airsensor1", system.IndividualAddress(0, 0, 55))
presencesensor1 = dev.PresenceSensor(
    "presencesensor1", system.IndividualAddress(0, 0, 66)
)

config_path = "config/config_test_config.json"
room_conf, system_dt = tools.configure_system_from_file(
    config_path, system_dt=1, test_mode=True
)

ir_button1 = system.InRoomDevice(button1, room_conf, 0.5, 3.1, 1.0)
ir_dimmer1 = system.InRoomDevice(dimmer1, room_conf, 0.525, 7.6375, 1.0)
ir_led1 = system.InRoomDevice(led1, room_conf, 5.7125, 7.5875, 1.0)
ir_heater1 = system.InRoomDevice(heater1, room_conf, 1.5625, 3.0375, 1.0)
ir_switch1 = system.InRoomDevice(switch1, room_conf, 4.1625, 1.5375, 1.0)
ir_brightness1 = system.InRoomDevice(brightness1, room_conf, 11.6625, 5.8, 1.0)
ir_humiditysoil1 = system.InRoomDevice(humiditysoil1, room_conf, 7.25, 1.1875, 1.0)
ir_airsensor1 = system.InRoomDevice(airsensor1, room_conf, 0.5375, 5.5, 1.0)
ir_presencesensor1 = system.InRoomDevice(presencesensor1, room_conf, 5.8375, 4.1, 1.0)

window1 = system.Window("window1", room_conf, "north", 4, [2, 1.5], test_mode=True)
ir_window1 = system.InRoomDevice(window1, room_conf, 4, 10, 1.5)

# Initial state
room_conf.update_world(
    interval=system_dt, gui_mode=False
)  # first_update flag is True after system initialization, no update is done simlpy set sensors values

system_button1 = room_conf.devices[room_conf.devices.index(ir_button1)].device
system_dimmer1 = room_conf.devices[room_conf.devices.index(ir_dimmer1)].device
system_heater1 = room_conf.devices[room_conf.devices.index(ir_heater1)].device
system_led1 = room_conf.devices[room_conf.devices.index(ir_led1)].device

system_brightness1 = room_conf.devices[room_conf.devices.index(ir_brightness1)].device
system_humiditysoil1 = room_conf.devices[
    room_conf.devices.index(ir_humiditysoil1)
].device
system_airsensor1 = room_conf.devices[room_conf.devices.index(ir_airsensor1)].device
system_presencesensor1 = room_conf.devices[
    room_conf.devices.index(ir_presencesensor1)
].device


def test_cli_commands(capfd):

    # 'set' functional module
    assert system_button1.state == False
    assert system_dimmer1.state == False
    assert system_button1._Button__str_state == "OFF"
    assert system_dimmer1._Dimmer__str_state == "OFF"
    ret = tools.user_command_parser("set button1 ON", room_conf)
    assert ret == 1
    assert system_button1.state == True
    assert system_button1._Button__str_state == "ON"
    assert system_heater1.state == True  # button1 on same group address than heater1
    ret = tools.user_command_parser("set dimmer1 ON 60", room_conf)
    assert ret == 1
    assert system_dimmer1.state == True
    assert system_dimmer1._Dimmer__str_state == "ON"
    assert system_dimmer1.state_ratio == 60
    assert system_led1.state == True  # dimmer1 on same group address than led1
    assert system_led1.state_ratio == 60
    assert system_led1.effective_lumen() == 800 * 0.6
    # actuators' state check
    ret = tools.user_command_parser(
        "set button1", room_conf
    )  # if no state entioned, switch state
    assert ret == 1
    assert system_button1.state == False
    assert system_button1._Button__str_state == "OFF"
    assert system_heater1.state == False
    ret = tools.user_command_parser("set dimmer1 OFF", room_conf)
    assert ret == 1
    assert system_dimmer1.state == False
    assert system_dimmer1._Dimmer__str_state == "OFF"
    assert system_led1.state == False

    ret = tools.user_command_parser(
        "set brightness1 OFF", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "set button22 ON", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "set brightness1", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "set button22", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "set dummy_device OFF", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "set dimmer1 ON 150", room_conf
    )  # test if state_ratio device case handled
    assert ret == 0

    # 'getvalue' sensor
    capfd.readouterr()  # empty buffer
    ret = tools.user_command_parser("getvalue brightness1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    # print(f"captured.out : {captured.out}\n")
    device_got = captured.out.split(":>")[-1].strip()
    assert device_got == "brightness1"
    ret = tools.user_command_parser("getvalue humiditysoil1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    device_got = captured.out.split(":>")[-1].strip()
    assert device_got == "humiditysoil1"
    ret = tools.user_command_parser("getvalue airsensor1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    device_got = captured.out.split(":>")[-1].strip()
    assert device_got == "airsensor1"
    ret = tools.user_command_parser("getvalue presencesensor1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    device_got = captured.out.split(":>")[-1].strip()
    assert device_got == "presencesensor1"

    ret = tools.user_command_parser(
        "getvalue button1", room_conf
    )  # test with worn device type
    assert ret == 0

    # 'getinfo'
    capfd.readouterr()  # empty buffer
    ret = tools.user_command_parser("getinfo", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    print(f"captured.out : {captured.out}\n")
    assert "> World information:" in captured.out
    assert "> Room information:" in captured.out
    assert "> Bus information:" in captured.out

    # 'getinfo world'
    capfd.readouterr()  # empty buffer
    ret = tools.user_command_parser("getinfo world", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world"
    ret = tools.user_command_parser("getinfo world time", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world time"
    ret = tools.user_command_parser("getinfo world temperature", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world temperature"
    ret = tools.user_command_parser("getinfo world humidity", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world humidity"
    ret = tools.user_command_parser("getinfo world co2", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world co2"
    ret = tools.user_command_parser("getinfo world brightness", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world brightness"
    ret = tools.user_command_parser("getinfo world weather", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world weather"
    ret = tools.user_command_parser("getinfo world out", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world out"
    ret = tools.user_command_parser("getinfo world all", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "world all"
    ret = tools.user_command_parser(
        "getinfo world dummy_option", room_conf
    )  # test if wrong option case handled
    assert ret == 0

    # 'getinfo room'
    capfd.readouterr()  # empty buffer
    ret = tools.user_command_parser("getinfo room", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "room"
    ret = tools.user_command_parser(
        "getinfo room dummy_option", room_conf
    )  # test if wrong option case handled
    assert ret == 0
    # 'getinfo bus'
    capfd.readouterr()  # empty buffer
    ret = tools.user_command_parser("getinfo bus", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "bus"
    ret = tools.user_command_parser(
        "getinfo bus dummy_option", room_conf
    )  # test if wrong option case handled
    assert ret == 0

    # 'getinfo dev'
    capfd.readouterr()  # empty buffer
    ret = tools.user_command_parser("getinfo dev button1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev button1"
    ret = tools.user_command_parser("getinfo dev dimmer1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev dimmer1"
    ret = tools.user_command_parser("getinfo dev led1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev led1"
    ret = tools.user_command_parser("getinfo dev heater1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev heater1"
    ret = tools.user_command_parser("getinfo dev switch1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev switch1"
    ret = tools.user_command_parser("getinfo dev brightness1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev brightness1"
    ret = tools.user_command_parser("getinfo dev humiditysoil1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev humiditysoil1"
    ret = tools.user_command_parser(
        "getinfo airsensor1", room_conf
    )  # works without specifying 'dev'
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "airsensor1"
    ret = tools.user_command_parser("getinfo dev presencesensor1", room_conf)
    assert ret == 1
    captured = capfd.readouterr()
    syst_component = captured.out.split(":>")[-1].strip()
    assert syst_component == "dev presencesensor1"

    ret = tools.user_command_parser(
        "getinfo dev dummy_device", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "getinfo dev", room_conf
    )  # test if wrong device case handled
    assert ret == 0
    ret = tools.user_command_parser(
        "value of brightness1", room_conf
    )  # test if wrong command case handled
    assert ret == 0

    # 'help' and 'quit' commands
    ret = tools.user_command_parser("h", room_conf)
    assert ret == 1
    ret = tools.user_command_parser("q", room_conf)  #
    assert ret == None


@pytest.mark.asyncio
async def test_api_commands(capfd):
    parser_object = tools.ScriptParser()
    # 'wait'
    ret, _ = await parser_object.script_command_parser(room_conf, "wait 0.1 h")
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(room_conf, "wait 6 m")
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(room_conf, "wait 180 s")
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "wait 2 x"
    )  # Test with wrong option
    assert ret == None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "wait 2 3 m"
    )  # Test with wrong number of option
    assert ret == None

    ## 'set [device]'
    # 'set button'
    ret, _ = await parser_object.script_command_parser(room_conf, "set button1 ON")
    assert ret == 1
    assert system_button1.state == True
    assert system_button1._Button__str_state == "ON"
    assert system_heater1.state == True  # button1 on same group address than heater1
    ret, _ = await parser_object.script_command_parser(room_conf, "set button1 OFF")
    assert ret == 1
    assert system_button1.state == False
    assert system_button1._Button__str_state == "OFF"
    assert system_heater1.state == False  # button1 on same group address than heater1
    # 'set dimmer'
    ret, _ = await parser_object.script_command_parser(room_conf, "set dimmer1 ON 60")
    assert ret == 1
    assert system_dimmer1.state == True
    assert system_dimmer1._Dimmer__str_state == "ON"
    assert system_led1.state == True  # dimmer1 on same group address than led1
    assert system_led1.state_ratio == 60
    ret, _ = await parser_object.script_command_parser(room_conf, "set dimmer1 OFF")
    assert ret == 1
    assert system_dimmer1.state == False
    assert system_dimmer1._Dimmer__str_state == "OFF"
    assert system_led1.state == False  # dimmer1 on same group address than led1
    # 'set presencesensor'
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set presencesensor1 True"
    )
    assert ret == 1
    assert system_presencesensor1.state == True
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set presencesensor1 False"
    )
    assert ret == 1
    assert system_presencesensor1.state == False
    # 'set humiditysoil'
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set humiditysoil1 97"
    )
    assert ret == 1
    assert system_humiditysoil1.humiditysoil == 97

    # test with wrong arguments
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set brightness1 ON"
    )  # test if wrong device case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set dummy_device ON"
    )  # test if wrong device case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set humiditysoil1 2f"
    )  # test if wrong option case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set presencesensor1 24"
    )  # test if wrong option case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set presencesensor22 True"
    )  # test if unknown device case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set button1"
    )  # test if options missing case handled
    assert ret is None

    # 'set temperature'
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set temperature 32 in"
    )
    assert ret == 1
    assert room_conf.world.ambient_temperature._AmbientTemperature__temperature_in == 32
    assert system_airsensor1.temperature == 32
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set temperature 30 out"
    )
    assert ret == 1
    assert room_conf.world.ambient_temperature.temperature_out == 30
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set temperature 24d out"
    )  # test if wrong value case handled
    assert ret is None
    # 'set humidity'
    ret, _ = await parser_object.script_command_parser(room_conf, "set humidity 20 in")
    assert ret == 1
    assert room_conf.world.ambient_humidity._AmbientHumidity__humidity_in == 20
    assert system_airsensor1.humidity == 20
    ret, _ = await parser_object.script_command_parser(room_conf, "set humidity 53 out")
    assert ret == 1
    assert room_conf.world.ambient_humidity.humidity_out == 53
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set humidity 24d out"
    )  # test if wrong value case handled
    assert ret is None
    # 'set co2'
    ret, _ = await parser_object.script_command_parser(room_conf, "set co2 550 in")
    assert ret == 1
    assert room_conf.world.ambient_co2._AmbientCO2__co2_in == 550
    assert system_airsensor1.humidity == 20
    ret, _ = await parser_object.script_command_parser(room_conf, "set co2 660 out")
    assert ret == 1
    assert room_conf.world.ambient_co2.co2_out == 660
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set co2 24d out"
    )  # test if wrong value case handled
    assert ret is None
    # 'set presence'
    ret, _ = await parser_object.script_command_parser(room_conf, "set presence True")
    assert ret == 1
    assert room_conf.world.presence.presence == True
    assert system_presencesensor1.state == True
    ret, _ = await parser_object.script_command_parser(room_conf, "set presence False")
    assert ret == 1
    assert room_conf.world.presence.presence == False
    assert system_presencesensor1.state == False

    ret, _ = await parser_object.script_command_parser(
        room_conf, "set presence dummy_state"
    )  # test if wrong value case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set presence True in"
    )  # test if wrong value case handled
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set Temperature 21 in memory"
    )  # test if wrong number of options case handled
    assert ret is None

    # 'set weather'
    ret, _ = await parser_object.script_command_parser(room_conf, "set weather dark")
    assert ret == 1
    assert room_conf.world.ambient_light._AmbientLight__weather == "dark"
    assert round(system_brightness1.brightness, 1) == 38.6
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set weather overcast"
    )
    assert ret == 1
    assert room_conf.world.ambient_light._AmbientLight__weather == "overcast"
    assert round(system_brightness1.brightness, 1) == 387.6
    ret, _ = await parser_object.script_command_parser(room_conf, "set weather clear")
    assert ret == 1
    assert room_conf.world.ambient_light._AmbientLight__weather == "clear"
    assert round(system_brightness1.brightness, 1) == 3877.0
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set weather dummy_weather"
    )
    assert ret is None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "set weather clear in"
    )
    assert ret is None

    ## 'store'
    # 'store world'
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world simtime sim_time1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world temperature temp1"
    )  # 32°
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world humidity hum1"
    )  # 20%
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world co2 co21"
    )  # 550 ppm
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world brightness bright1"
    )  # 3877.0 lux
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world weather weather1"
    )  # 'clear'
    assert ret == 1
    # 'store [device]'
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store button1 state button1_state1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store dimmer1 state dimmer1_state1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store dimmer1 state_ratio dimmer1_stateratio1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store led1 state led1_state1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store led1 max_lumen led1_maxlumen1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store led1 effective_lumen led1_efflumen1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store led1 state_ratio led1_stateratio1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store led1 beam_angle led1_beamangle1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store heater1 state heater1_state1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store heater1 max_power heater1_maxpower1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store heater1 effective_power heater1_effpower1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store heater1 state_ratio heater1_stateratio1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store switch1 state switch1_state1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store brightness1 brightness brightness1_bright1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store humiditysoil1 humiditysoil humiditysoil1_moisture1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store airsensor1 temperature airsensor1_temp1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store airsensor1 humidity airsensor1_temp1"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store airsensor1 co2 airsensor1_co21"
    )
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store presencesensor1 state presensor1_state1"
    )
    assert ret == 1

    ret, _ = await parser_object.script_command_parser(
        room_conf, "store presencesensor1 state presensor1_state1 in memory"
    )  # Test with wrong number of options
    assert ret == None
    ret, _ = await parser_object.script_command_parser(
        room_conf, "store world state world_1"
    )  # Test with wrong world ambient
    assert ret == None

    ## 'assert'
    await parser_object.script_command_parser(
        room_conf, "set temperature 20 in"
    )  # < previous 32
    await parser_object.script_command_parser(
        room_conf, "set humidity 70 in"
    )  # > previous 20
    await parser_object.script_command_parser(
        room_conf, "set co2 550 in"
    )  # = previous 550
    await parser_object.script_command_parser(
        room_conf, "set weather dark"
    )  # != previous 'clear'
    await parser_object.script_command_parser(
        room_conf, "set presencesensor1 True"
    )  # != previous 'False'
    await parser_object.script_command_parser(
        room_conf, "# wait 1"
    )  # '#' comment is not considered
    await parser_object.script_command_parser(
        room_conf, "store world temperature temp2"
    )  # 20°
    await parser_object.script_command_parser(
        room_conf, "store world humidity hum2"
    )  # 70%
    await parser_object.script_command_parser(
        room_conf, "store world co2 co22"
    )  # 550 ppm
    await parser_object.script_command_parser(
        room_conf, "store world brightness bright2"
    )  # 38.6 lux
    await parser_object.script_command_parser(
        room_conf, "store world weather weather2"
    )  # 'dark'
    await parser_object.script_command_parser(
        room_conf, "store presencesensor1 state presensor1_state2"
    )

    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert temp2 <= temp1"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True1" in key:
            assert "temp2 <= temp1" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert hum2 >= hum1"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True2" in key:
            assert "hum2 >= hum1" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert co22 == co21"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True3" in key:
            assert "co22 == co21" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert weather2 != weather1"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True4" in key:
            assert "weather2 != weather1" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert bright2 <= bright1"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True5" in key:
            assert "bright2 <= bright1" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert presensor1_state2 != presensor1_state1"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True6" in key:
            assert "presensor1_state2 != presensor1_state1" in assertions[key]

    await parser_object.script_command_parser(
        room_conf, "store presencesensor1 state presensor1_state3"
    )
    await parser_object.script_command_parser(
        room_conf, "store world brightness bright3"
    )  # 38.6 lux
    await parser_object.script_command_parser(
        room_conf, "store world weather weather3"
    )  # 'dark'
    await parser_object.script_command_parser(room_conf, "wait 2")
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert weather3 == weather2"
    )
    assert ret == 1
    for key in assertions.keys():  # key with simtime
        if "Assertion True7" in key:
            assert "weather3 == weather2" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert weather3 == dark"
    )
    assert ret == 1
    for key in assertions.keys():  # key with simtime
        if "Assertion True8" in key:
            assert "weather3 == new_var" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert bright3 == bright2"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True9" in key:
            assert "bright3 == bright2" in assertions[key]
    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert presensor1_state3 == True"
    )
    assert ret == 1
    assert len(assertions) > 0
    for key in assertions.keys():  # key with simtime
        if "Assertion True10" in key:
            assert "presensor1_state2 != new_var" in assertions[key]

    ret, assertions = await parser_object.script_command_parser(
        room_conf, "assert weather3 != weather2"
    )  # Test with false assertion
    assert ret == None
    for key in assertions.keys():  # key with simtime
        if "Assertion True11" in key:
            assert "weather3 != weather2" in assertions[key]
    ret, _ = await parser_object.script_command_parser(
        room_conf, "assert bright3 == or <= bright2"
    )  # Test with wrong number of options
    assert ret == None

    # 'show' and 'end' commands
    ret, _ = await parser_object.script_command_parser(room_conf, "show bright2")
    assert ret == 1
    ret, _ = await parser_object.script_command_parser(
        room_conf, "show bright1 in terminal"
    )  # Test with too many options
    assert ret == None
    ret, _ = await parser_object.script_command_parser(room_conf, "end")
    assert ret == 0
