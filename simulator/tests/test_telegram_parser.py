""" Test parsing of telegrams"""

import sys

sys.path.append("..")
import system.telegrams as sim_t
import system.system_tools as sim_addr
from system.telegrams import FloatPayload, BinaryPayload
from svshi_interface.telegram_parser import *
import pytest


def test_telegram_from_simulated_1():
    group_address_to_payload_1 = {"0/0/0": BinaryPayload, "0/0": FloatPayload}
    parser = TelegramParser(group_address_to_payload_1)

    # For group address 1
    ga1 = sim_addr.GroupAddress("3-levels", 0, 0, 0)
    ia1 = sim_addr.IndividualAddress(1, 1, 1)

    simulator_t = sim_t.Telegram(ia1, ga1, BinaryPayload(True))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    # For group address 2
    ga1 = sim_addr.GroupAddress("2-levels", 0, 0)
    ia1 = sim_addr.IndividualAddress(1, 1, 2)

    simulator_t = sim_t.Telegram(ia1, ga1, FloatPayload(22.2))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    simulator_t = sim_t.Telegram(ia1, ga1, FloatPayload(None))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert knx_t is None


group_address_to_payload_2 = {"0/0/0": FloatPayload, "0": FloatPayload}


def test_telegram_from_simulated_2():
    parser = TelegramParser(group_address_to_payload_2)

    # For group address 1
    ga1 = sim_addr.GroupAddress("3-levels", 0, 1, 1)
    ia1 = sim_addr.IndividualAddress(0, 1, 2)

    simulator_t = sim_t.Telegram(ia1, ga1, BinaryPayload(False))
    knx_t = parser.from_simulator_telegram(simulator_t)
    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    # For group address 2
    ga1 = sim_addr.GroupAddress("3-levels", 0, 0, 0)
    ia1 = sim_addr.IndividualAddress(1, 1, 2)

    simulator_t = sim_t.Telegram(ia1, ga1, FloatPayload(12.0))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))

    # For group address 3
    ga1 = sim_addr.GroupAddress("free", 0)
    ia1 = sim_addr.IndividualAddress(1, 3, 2)

    simulator_t = sim_t.Telegram(ia1, ga1, FloatPayload(18.2))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))


group_address_to_payload_3 = {"30/6/100": FloatPayload, "29/35": FloatPayload}


def test_telegram_from_simulated_3():
    parser = TelegramParser(group_address_to_payload_3)

    # For group address 1
    ga1 = sim_addr.GroupAddress("3-levels", 30, 6, 100)
    ia1 = sim_addr.IndividualAddress(0, 1, 2)

    simulator_t = sim_t.Telegram(ia1, ga1, FloatPayload(1.0))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))
    # For group address 2
    ga1 = sim_addr.GroupAddress("2-levels", 29, 0, 35)
    ia1 = sim_addr.IndividualAddress(1, 1, 2)

    simulator_t = sim_t.Telegram(ia1, ga1, FloatPayload(90.0))

    knx_t = parser.from_simulator_telegram(simulator_t)

    assert str(simulator_t) == str(parser.from_knx_telegram(knx_t))
