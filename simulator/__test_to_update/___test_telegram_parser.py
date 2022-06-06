import sys
sys.path.append('..')
import system.telegrams as sim_t
import system.system_tools as sim_addr
from system.telegrams import HeaterPayload, TempControllerPayload
from svshi_interface.telegram_parser import *
import pytest


group_address_to_payload_1 = {
    # '0/0/0': SwitchPayload,
    '0/0': HeaterPayload,
}

def test_telegram_from_simulated_1():
    parser = TelegramParser(group_address_to_payload_1)

    # For group address 1
    # ga1 = sim_addr.GroupAddress('3-levels', 0, 0, 0)
    # ia1 = sim_addr.IndividualAddress(1, 1, 1) 

    # simulator_t = sim_t.Telegram(0, ia1, ga1, SwitchPayload(True))

    # knx_t = parser.from_simulator_telegram(simulator_t)
    
    # assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    # For group address 2
    ga1 = sim_addr.GroupAddress('2-levels', 0, 0)
    ia1 = sim_addr.IndividualAddress(1, 1, 2)

    simulator_t = sim_t.Telegram(0, ia1, ga1, HeaterPayload(22))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))


group_address_to_payload_2 = {
    # '0/1/1': SwitchPayload,
    '0/0/0': HeaterPayload,
    '0': TempControllerPayload
}


def test_telegram_from_simulated_2():
    parser = TelegramParser(group_address_to_payload_2)

    # For group address 1
    # ga1 = sim_addr.GroupAddress('3-levels', 0, 1, 1)
    # ia1 = sim_addr.IndividualAddress(0, 1, 2)

    # simulator_t = sim_t.Telegram(0, ia1, ga1, SwitchPayload(False))
    # knx_t = parser.from_simulator_telegram(simulator_t)
    # assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    # For group address 2
    ga1 = sim_addr.GroupAddress('3-levels', 0, 0, 0)
    ia1 = sim_addr.IndividualAddress(1, 1, 2)

    simulator_t = sim_t.Telegram(0, ia1, ga1, HeaterPayload(123456789))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    # For group address 3
    ga1 = sim_addr.GroupAddress('free', 0)
    ia1 = sim_addr.IndividualAddress(1, 53, 2)

    simulator_t = sim_t.Telegram(0, ia1, ga1, TempControllerPayload(1234567))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))


group_address_to_payload_3 = {
    '30/6/100': TempControllerPayload,
    '29/35': HeaterPayload
}

def test_telegram_from_simulated_3():
    parser = TelegramParser(group_address_to_payload_3)

    # For group address 1
    ga1 = sim_addr.GroupAddress('3-levels', 30, 6, 100)
    ia1 = sim_addr.IndividualAddress(0, 1, 2)

    simulator_t = sim_t.Telegram(0, ia1, ga1, TempControllerPayload(1))
    
    knx_t = parser.from_simulator_telegram(simulator_t)
    
    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))
    # For group address 2
    ga1 = sim_addr.GroupAddress('2-levels', 29, 0,35)
    ia1 = sim_addr.IndividualAddress(1, 1, 2)

    simulator_t = sim_t.Telegram(0, ia1, ga1, HeaterPayload(90))

    knx_t = parser.from_simulator_telegram(simulator_t)
    
    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))