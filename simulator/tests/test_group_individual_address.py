"""Test group and individual address creation"""
import pytest
from _pytest.logging import LogCaptureFixture

import system, tools


gas = {
    "3-levels": {
        "gas": ["0/0/0", "1/1/1", "23/6/217", "31/7/255"],
        "gas_split": [(0, 0, 0), (1, 1, 1), (23, 6, 217), (31, 7, 255)],
        "gas_wrong": ["-1/-3/-19", "-32/5/5", "35/9/280", "31/7/500"],
        "gas_false": ["a/a/a", "1/2/3/4", "1/2/*", "+/-/#", " "],
    },
    "2-levels": {
        "gas": ["0/0", "1/1", "23/1256", "31/2047"],
        "gas_split": [(0, 0), (1, 1), (23, 1256), (31, 2047)],
        "gas_wrong": ["-1/-19", "-32/5", "35/2410", "31/2500"],
        "gas_false": ["a/a", "1/2/3/4", "1/*", "+/#", " "],
    },
    "free": {
        "gas": ["0", "1", "217", "65535"],
        "gas_split": [0, 1, 217, 65535],
        "gas_wrong": ["-1", "-32", "65537", "72333"],
        "gas_false": ["-0", "a", "1/2/3/4", "*", "+/#", " "],
    },
}

encoding_styles = ["free", "2-levels", "3-levels"]
encoding_styles_gas_split = ([6000, (5, 5), (2, 2, 2)],)
encoding_style_wrong = [
    "0-levels",
    "1-levels",
    "2-level",
    "2levels",
    "3level",
    "4-levels",
]


# Test style name of group addresses
def test_correct_style_name():
    for s in range(len(encoding_styles)):
        encoding_style = encoding_styles[s]
        ga_style = tools.check_group_address(encoding_style, style_check=True)
        assert ga_style == encoding_style


def test_wrong_style_name():
    for encoding_style in encoding_style_wrong:
        ga = tools.check_group_address(encoding_style, "1/1/1")
        assert ga is None


# Test group addresses
def test_correct_group_address():
    for encoding_style in encoding_styles:
        gc = 0
        group_addresses = gas[encoding_style]["gas"]
        group_addresses_split = gas[encoding_style]["gas_split"]
        for group_address in group_addresses:
            ga = tools.check_group_address(encoding_style, group_address)
            assert ga is not None
            if encoding_style == "3-levels":
                assert ga.main == group_addresses_split[gc][0]
                assert ga.middle == group_addresses_split[gc][1]
                assert ga.sub == group_addresses_split[gc][2]
            if encoding_style == "2-levels":
                assert ga.main == group_addresses_split[gc][0]
                assert ga.sub == group_addresses_split[gc][1]
            if encoding_style == "free":
                assert ga.main == group_addresses_split[gc]
            gc += 1


def test_wrong_group_address():
    for encoding_style in encoding_styles:
        group_addresses = gas[encoding_style]["gas_wrong"]
        # Out-of-bounds address
        for group_address in group_addresses:
            ga = tools.check_group_address(encoding_style, group_address)
            assert ga is None


def test_false_group_address():
    for encoding_style in encoding_styles:
        group_addresses = gas[encoding_style]["gas_false"]
        # Totally false group addresses
        for group_address in group_addresses:
            ga = tools.check_group_address(encoding_style, group_address)
            assert ga is None


# Test individual addresses
correct_indiv_addr = [(0, 0, 0), (2, 10, 250), (15, 15, 255)]
false_indiv_addr = [(-1, 0, 12), (2.4, 10, 10), (0, 20, 200), ("a", "l0", 20)]


def test_correct_individual_address():
    for ia_tuple in correct_indiv_addr:
        area, line, device = ia_tuple[0], ia_tuple[1], ia_tuple[2]
        ia = system.IndividualAddress(area, line, device)
        assert ia.area is not None and ia.area == area
        assert ia.line is not None and ia.line == line
        assert ia.device is not None and ia.device == device


def test_incorrect_individual_address():
    for ia_tuple in false_indiv_addr:
        area, line, device = ia_tuple[0], ia_tuple[1], ia_tuple[2]
        ia = system.IndividualAddress(area, line, device)
        assert ia.area is None and ia.line is None and ia.device is None
