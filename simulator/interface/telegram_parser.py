
import dataclasses
import asyncio
import datetime
from asyncio.tasks import Task
from io import TextIOWrapper
import os
import sys

sys.path.append('.')
sys.path.append('..')
from typing import Any, Callable, Dict, Final, List, Optional, Tuple, Union, cast
from itertools import groupby
from collections import defaultdict
from enum import Enum
from xknx.core.value_reader import ValueReader
from xknx.dpt.dpt import DPTArray, DPTBase, DPTBinary
from xknx.telegram.apci import GroupValueWrite
from xknx.telegram.telegram import Telegram
from xknx.telegram.address import GroupAddress, IndividualAddress, GroupAddressType
from xknx.xknx import XKNX
import system.telegrams as sim_t


#TODO: we do not handle floats for the moment, but useful when describing temperature!!!

class TelegramParser:
    '''Class that implements a parser for telegrams, from simulated telegrams to real telegrams and the other way around'''

    def __init__(self, group_address_to_payload):
        # TODO: If new devices, must add payload import and update dict here
        self.group_address_to_payload: Dict[str,
                                            sim_t.Payload] = group_address_to_payload
        self.payload_to_dpt: Dict[sim_t.Payload, Union[DPTBinary, DPTArray]] = {
            # sim_t.ButtonPayload: DPTBinary,
            sim_t.HeaterPayload: DPTArray,
            sim_t.BinaryPayload: DPTBinary,
            sim_t.ButtonPayload: DPTBinary
        }

        # Represent true and false values in knx communication
        self.__TRUE: Final = 1
        self.__FALSE: Final = 0
        
        self.__FREE: Final = GroupAddressType.FREE
        self.__SHORT: Final = GroupAddressType.SHORT
        self.__LONG: Final = GroupAddressType.LONG

        self.__sim_encoding_to_xknx = {
            'free': self.__FREE,
            '2-levels': self.__SHORT,
            '3-levels': self.__LONG
        }


    def from_knx_telegram(self, telegram: Telegram):
        '''Creates a simulator telegram from a knx telegram'''
        from system.tools import GroupAddress, IndividualAddress
        payload = telegram.payload
        
        ga_split = str(telegram.destination_address).split('/')

        if telegram.destination_address.address_format == self.__sim_encoding_to_xknx.get('free'):
            address = GroupAddress('free', ga_split[0])
        elif telegram.destination_address.address_format == self.__sim_encoding_to_xknx.get('2-levels'):
            address = GroupAddress('2-levels', ga_split[0], 0, ga_split[1])
        else:
            address = GroupAddress('3-levels', ga_split[0], ga_split[1], ga_split[2])

        source = IndividualAddress(telegram.source_address.area, telegram.source_address.line, telegram.source_address.main)
        output = None


        if isinstance(payload, GroupValueWrite):
            # For the moment, similarly to SVSHI, we only support GroupValueWrtie as there is no reading involved
            v = payload.value
            if v:
                dpt = self.payload_to_dpt.get(self.group_address_to_payload.get(str(address),None),None)
                
                if dpt == None:
                    return None
                
                # TODO: what control field?
                if dpt == DPTBinary:
                    payload = self.group_address_to_payload.get(str(address))(switched=True if v.value == self.__TRUE else False)
                    output = sim_t.Telegram(0, source, address,payload)
                    
                else:
                    
                    conv_v = v.value[0]
                    payload = self.group_address_to_payload.get(str(address))(conv_v)
                    output = sim_t.Telegram(0, source, address,payload)
        return output
    
    def from_simulator_telegram(self, telegram: sim_t.Telegram):
        '''Creates a knx telegram from a simulator telegram'''
        address = str(telegram.destination)
        payload = telegram.payload

        encoding = telegram.destination.encoding_style

        dpt = None
        value = None

        if isinstance(payload, sim_t.BinaryPayload):
            dpt = self.payload_to_dpt.get(sim_t.BinaryPayload)
            value = payload.binary_state
        
        elif isinstance(payload, sim_t.ButtonPayload):
            dpt = self.payload_to_dpt.get(sim_t.ButtonPayload)
            value = payload.state

        # elif isinstance(payload, sim_t.HeaterPayload):
        #     dpt = self.payload_to_dpt.get(sim_t.HeaterPayload)
        #     value = payload.max_power


        if dpt != None and value != None:
            content = None

            if dpt == DPTBinary:
                binary_value = self.__TRUE if value else self.__FALSE
                write_content = DPTBinary(value=binary_value)
            else:
                write_content = DPTArray(value)
     
            ga = GroupAddress(address)
            ga.address_format = self.__sim_encoding_to_xknx.get(encoding)
 
            telegram = Telegram(source_address=IndividualAddress(telegram.source.__repr__()),
                destination_address=ga,
                payload=GroupValueWrite(write_content)
            )

            return telegram
        else:    
            return None

def main():
    from system.telegrams import ButtonPayload, HeaterPayload
    from system.tools import GroupAddress, IndividualAddress

    group_address_to_payload_example = {
        '0/0/0': ButtonPayload,
        '0/0': HeaterPayload,
    }

    parser = TelegramParser(group_address_to_payload_example)
    ga = GroupAddress('2-levels', 0,0)
    ia = IndividualAddress(0,0,1)
    test_sim = sim_t.Telegram(0, ia, ga, sim_t.HeaterPayload(19))
    print(test_sim)
    knx_t = parser.from_simulator_telegram(test_sim)

    back = parser.from_knx_telegram(knx_t)
    print(str(back) == str(test_sim))

# if __name__=="__main__":
#     main()


