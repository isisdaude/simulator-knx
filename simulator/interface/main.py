import asyncio

# from xknx import XKNX
# from xknx.dpt import DPTBinary
# from xknx_tweaked.tunnel import UDPTunnel
# from xknx.telegram import GroupAddress, IndividualAddress, Telegram
# from xknx.telegram.apci import GroupValueWrite
# Changed request response to wait for any received packet
# async def main():
#     """Connect to a tunnel, send 2 telegrams and disconnect."""
#     xknx = XKNX()

#     # an individual address will most likely be assigned by the tunnelling server
#     xknx.own_address = IndividualAddress("15.15.249")

#     tunnel = UDPTunnel(
#         xknx,
#         gateway_ip="127.0.0.1",
#         gateway_port=3671,
#         local_ip="127.0.0.1",
#         local_port=3671,
#         route_back=False,
#     )

#     await tunnel.connect()

#     await tunnel.send_telegram(
#         Telegram(
#             destination_address=GroupAddress("1/0/15"),
#             payload=GroupValueWrite(DPTBinary(1)),
#         )
#     )
#     await asyncio.sleep(2)
#     await tunnel.send_telegram(
#         Telegram(
#             destination_address=GroupAddress("1/0/15"),
#             payload=GroupValueWrite(DPTBinary(0)),
#         )
#     )
#     await asyncio.sleep(2)

#     await tunnel.disconnect()


# asyncio.run(main())
import socket
import sys
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
import numpy as np
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *

async def main(room):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	server_address = ('128.179.196.182', 3671)
	sock.bind(server_address)

	print("waiting on port:", 3671)
	connection_config = ConnectionConfig(
				route_back=True,  # To enable connection through the docker
				connection_type=ConnectionType.TUNNELING,
				gateway_ip="128.179.196.182",
				gateway_port=3671,
			)
	xknx = XKNX(connection_config=connection_config)

	while True:
		data, addr = sock.recvfrom(1024)
		
		if data:
			print("Address of the sender:", addr)
			# Initializing the KNX/IP Frame to be sent
			frame = KNXIPFrame(xknx)
			frame.from_knx(data)
			frame.init(KNXIPServiceType.CONNECT_RESPONSE)
			frame.header.set_length(frame.body)

			# Sending the response
			data_to_send = bytes(frame.to_knx())
			sock.sendto(data_to_send, addr)
			break
	
	while True:
		data, addr = sock.recvfrom(1024)
		# room.knxbus.transmot_telegram
		print(data)
		
if __name__ == '__main__':
	asyncio.run(main())