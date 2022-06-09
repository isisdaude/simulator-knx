"""
TODO
"""

import socket

import asyncio
from xknx.core.value_reader import ValueReader
from xknx.dpt.dpt import DPTArray, DPTBase, DPTBinary
from xknx.telegram.apci import GroupValueWrite
from xknx.telegram.telegram import Telegram
from xknx.telegram.address import GroupAddress
from xknx.xknx import XKNX
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.xknx import XKNX
from xknx.telegram.telegram import Telegram


async def telegram_received_cb(telegram: Telegram):
        """
        Updates the state once a telegram is received.
        """
        print(telegram)

async def main():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)  
    connection_config = ConnectionConfig(
            route_back=True,  # To enable connection through the docker
            connection_type=ConnectionType.TUNNELING,
            gateway_ip=IPAddr,
            gateway_port=3671,
        )
    xknx = XKNX( connection_config=connection_config, daemon_mode=True)
    xknx.telegram_queue.register_telegram_received_cb(telegram_received_cb)

    telegram = Telegram(
                destination_address=GroupAddress("1/1/1"),
                payload=GroupValueWrite(DPTBinary(1)),
            )
    
    await xknx.telegrams.put(telegram)
    await xknx.start()
    print("Connected!")
    print("sending telegram")
    
asyncio.run(main())