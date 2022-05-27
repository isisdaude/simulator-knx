import asyncio
import socket
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
import numpy as np
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *
import xknx.telegram.telegram as real_t
from .telegram_parser import TelegramParser
import system.telegrams as sim_t

def create_ack_data(frame: KNXIPFrame):
	'''Creates ACK message to be sent as a response to a received telegram'''
	frame.init(KNXIPServiceType.TUNNELLING_ACK)
	frame.header.set_length(frame.body)
	return bytes(frame.to_knx())

def create_connection(sock: socket.socket, xknx: XKNX):
	'''Creates a connection between a client and ourselves, with sequence number 0 and individual address 0.0.0'''
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
	return frame

	

async def main(room):

	group_address_to_payload = {} #TODO: create correct bindings!

	telegram_parser = TelegramParser(group_address_to_payload)


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

	frame = create_connection(sock, xknx)

	# while True:
	# 	data, addr = sock.recvfrom(1024)
		
	# 	if data:
	# 		print("Address of the sender:", addr)
	# 		# Initializing the KNX/IP Frame to be sent
	# 		frame = KNXIPFrame(xknx)
	# 		frame.from_knx(data)
	# 		frame.init(KNXIPServiceType.CONNECT_RESPONSE)
	# 		frame.header.set_length(frame.body)

	# 		# Sending the response
	# 		data_to_send = bytes(frame.to_knx())
	# 		sock.sendto(data_to_send, addr)
	# 		break
	
	while True:
		data, addr = sock.recvfrom(1024)
		
		frame.from_knx(data)

		telegram: real_t.Telegram = frame.body.cemi.telegram # The telegram to be sent to simulator after parsed!

		sim_telegram: sim_t.Telegram = telegram_parser.from_knx_telegram(telegram)
		
		room.knxbus.transmit_telegram(sim_telegram)
		
		# frame.init(KNXIPServiceType.TUNNELLING_ACK)
		# frame.header.set_length(frame.body)

		# data_to_send = bytes(frame.to_knx())
		sock.sendto(create_ack_data(frame), addr)
		
if __name__ == '__main__':
	asyncio.run(main())