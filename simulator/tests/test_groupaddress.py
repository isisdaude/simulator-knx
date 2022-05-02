import pytest
from _pytest.logging import LogCaptureFixture

import system

gas = {
    '3-levels' : {
        'gas' : ['0/0/0', '1/1/1', '23/6/217', '31/7/255'],
        'gas_split' : [(0,0,0), (1,1,1), (23,6,217), (31,7,255)],
        'gas_wrong' : ['-1/-3/-19', '-32/5/5', '35/9/280', '31/7/500'],
        'gas_false' : ['a/a/a', '1/2/3/4', '1/2/*', '+/-/#', ' ']},
    '2-levels' : {
        'gas' : ['0/0', '1/1', '23/1256', '31/2047'],
        'gas_split' : [(0,0), (1,1), (23,1256), (31,2047)],
        'gas_wrong' : ['-1/-19', '-32/5', '35/2410', '31/2500'],
        'gas_false' : ['a/a', '1/2/3/4', '1/*', '+/#', ' ']},
    'free' : {
        'gas' : ['0', '1', '217', '65535'],
        'gas_split' : [0, 1, 217, 65535],
        'gas_wrong' : ['-1', '-32', '65537', '72333'],
        'gas_false' : ['-0', 'a', '1/2/3/4', '*', '+/#', ' ']}}

encoding_styles = ['free', '2-levels', '3-levels']
encoding_styles_gas = ['60000', '5/5', '2/2/2']
encoding_styles_gas_split = [6000, (5,5), (2,2,2)],
encoding_style_wrong = ['0-levels', '1-levels', '2-level', '2levels', '3level', '4-levels']


def test_correct_group_address():
    for encoding_style in encoding_styles:
        gc = 0
        group_addresses = gas[encoding_style]['gas']
        group_addresses_split = gas[encoding_style]['gas_split']
        for group_address in group_addresses:
            ga = system.group_address_format_check(encoding_style, group_address)
            assert ga is not None
            if encoding_style == '3-levels':
                assert ga.main == group_addresses_split[gc][0]
                assert ga.middle == group_addresses_split[gc][1]
                assert ga.sub == group_addresses_split[gc][2]
            if encoding_style == '2-levels':
                assert ga.main == group_addresses_split[gc][0]
                assert ga.sub == group_addresses_split[gc][1]
            if encoding_style == 'free':
                assert ga.main == group_addresses_split[gc]
            gc += 1

def test_wrong_group_address(caplog: LogCaptureFixture):
    for encoding_style in encoding_styles:
        group_addresses = gas[encoding_style]['gas_wrong']
        # Out-of-bounds address
        for group_address in group_addresses:
            caplog.clear
            ga = system.group_address_format_check(encoding_style, group_address)
            assert ga is None
            # assert ("group address is out of bounds" in caplog.text or "has wrong value type," in caplog.text)


def test_false_group_address(caplog: LogCaptureFixture):
    for encoding_style in encoding_styles:
        group_addresses = gas[encoding_style]['gas_false']
        # Totally false group addresses
        for group_address in group_addresses:
            caplog.clear
            ga = system.group_address_format_check(encoding_style, group_address)
            assert ga is None
            # assert ("style is not respected," in caplog.text or "group address has wrong value type," in caplog.text)

def test_correct_style_name(): #,encoding_styles_gas_split
    for s in range(len(encoding_styles)):
        encoding_style, group_address = encoding_styles[s], encoding_styles_gas[s]
        ga =system.group_address_format_check(encoding_style, group_address)
        assert ga is not None
        # if s == 2:
        #     assert ga.main == encoding_styles_gas_split[s][0]
        #     assert ga.middle == encoding_styles_gas_split[s][1]
        #     assert ga.sub == encoding_styles_gas_split[s][2]
        # if s == 1:
        #     assert ga.main == encoding_styles_gas_split[s][0]
        #     assert ga.sub == encoding_styles_gas_split[s][1]
        # if s == 0:
        #     assert ga.main == encoding_styles_gas_split[s][0]

def test_wrong_style_name(caplog: LogCaptureFixture):
    for encoding_style in encoding_style_wrong:
        caplog.clear
        ga =system.group_address_format_check(encoding_style, '1/1/1')
        assert ga is None
        # for record in caplog.records:
        #     assert record.levelname != "CRITICAL"
        assert "unknown, please use 'free'(0-65535), '2-levels'(0/0 -> 31/2047) or '3-levels'(0/0/0-31/7/255)" in caplog.text



