import asyncio
import time
from xknx.core.value_reader import ValueReader
from xknx.dpt.dpt import DPTArray, DPTBase, DPTBinary
from xknx.telegram.apci import GroupValueWrite
from xknx.telegram.telegram import Telegram
from xknx.telegram.address import GroupAddress
from xknx.xknx import XKNX
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.xknx import XKNX
from xknx.telegram.telegram import Telegram
import asyncio
import time

async def telegram_received_cb(telegram: Telegram):
        """
        Updates the state once a telegram is received.
        """
        print(telegram)

async def main():
    connection_config = ConnectionConfig(
            route_back=True,  # To enable connection through the docker
            connection_type=ConnectionType.TUNNELING,
            gateway_ip="192.168.1.10",
            gateway_port=3671,
        )
    xknx = XKNX( connection_config=connection_config)
    xknx.telegram_queue.register_telegram_received_cb(telegram_received_cb)

    telegram = Telegram(
                destination_address=GroupAddress("1/1/56"),
                payload=GroupValueWrite(DPTBinary(1)),
            )
    
    await xknx.telegrams.put(telegram)
    await xknx.start()
    print("Connected!")
    print("sending telegram")
    # async with xknx as xknx:
    #         # Read from KNX the current value
    #         value_reader = ValueReader(
    #             xknx,
    #             GroupAddress("0/0/5"),
    #             timeout_in_seconds=5,
    #         )
    #         telegram = await value_reader.read()
    #         print(telegram)
asyncio.run(main())