""" Test Speed Factor"""
import pytest

import tools

# Test the speed factor given by user
speed_factor_correct = ["1", " 1 ", "50", "180", "300.67", "004"]
speed_factor_correct_verif = [1.0, 1.0, 50.0, 180.0, 300.67, 4.0]
speed_factor_wrong = ["0.99", "0", "-45", "-792.56"]
speed_factor_false = ["a4", "-056", "0x4", "0b1001"]


def test_correct_speed_factor():
    for s in range(len(speed_factor_correct)):
        assert (
            tools.check_simulation_speed_factor(speed_factor_correct[s])
            == speed_factor_correct_verif[s]
        )


def test_incorrect_speed_factor():
    for wrong_factor in speed_factor_wrong:
        assert tools.check_simulation_speed_factor(wrong_factor) is None
    for false_factor in speed_factor_false:
        assert tools.check_simulation_speed_factor(false_factor) is None
