from system import telegrams as sim_t
import xknx
from xknx.telegram.telegram import Telegram
from xknx.telegram.apci import GroupValueWrite


class TelegramParser:
    '''Class that implements a parser for telegrams, from simulated telegrams to real telegrams and the other way around'''

    def __init__(self):
        # TODO: should contain a list of devices (or only type) and the associated grooup address to be able to make the right payload when parsing
        
        pass

    def from_knx_telegram(self, telegram: Telegram):
        '''Creates a simulator telegram from a knx telegram'''
        payload = telegram.payload
        address = str(telegram.destination_address)

        if isinstance(payload, GroupValueWrite):
            # For the moment, similarly to SVSHI, we only support GroupValueWrtie as there is no reading involved
            v = payload.value

            if v:
                # What if it's a value that can only be interpreted by a device? dropped at arrival?
                pass