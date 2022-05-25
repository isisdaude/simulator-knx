import asyncio
import socket
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
import numpy as np
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *

async def main(): # TODO: Put room as argument
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	hostname = socket.gethostname()   
	IPAddr = socket.gethostbyname(hostname)  

	server_address = (IPAddr, 3671)
	sock.bind(server_address)

	print("Waiting on port:", 3671, "at address", IPAddr)
	connection_config = ConnectionConfig(
				route_back=True,  # To enable connection through the docker
				connection_type=ConnectionType.TUNNELING,
				gateway_ip=IPAddr,
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
		
		frame.from_knx(data)
		print(frame)
		# room.knxbus.transmot_telegram, should aprse it to a simulated telegram
		frame.init(KNXIPServiceType.TUNNELLING_ACK)
		frame.header.set_length(frame.body)

		data_to_send = bytes(frame.to_knx())
		sock.sendto(data_to_send, addr)
		
if __name__ == '__main__':
	asyncio.run(main())