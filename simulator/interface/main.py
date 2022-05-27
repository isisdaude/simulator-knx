import sys
from typing import List
sys.path.append(".")
sys.path.append("..")
import asyncio
import socket
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *
import xknx.telegram.telegram as real_t
from xknx.knxip import TunnellingRequest

import system.telegrams as sim_t

class Interface:

	def __init__(self):
		self.__sending_lock = asyncio.Lock()
		self.__sending_queue: asyncio.Queue[sim_t.Telegram] = asyncio.Queue()
		from telegram_parser import TelegramParser
		group_address_to_payload = {} #TODO: create correct bindings! for the moment, only BinaryPayload

		self.telegram_parser = TelegramParser(group_address_to_payload)

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		hostname = socket.gethostname()   
		self.IPAddr = socket.gethostbyname(hostname)  

		server_address = (self.IPAddr, 3671)
		self.sock.bind(server_address)

	def __create_ack_data(self, frame: KNXIPFrame):
		'''Creates ACK message to be sent as a response to a received telegram'''
		frame.init(KNXIPServiceType.TUNNELLING_ACK)
		frame.header.set_length(frame.body)
		return bytes(frame.to_knx())

	def __create_connection(self, xknx: XKNX):
		'''Creates a connection between a client and ourselves, with sequence number 0 and individual address 0.0.0'''
		while True:
			data, addr = self.sock.recvfrom(1024)
			
			if data:
				print("Address of the sender:", addr)
				# Initializing the KNX/IP Frame to be sent
				frame = KNXIPFrame(xknx)
				frame.from_knx(data)
				frame.init(KNXIPServiceType.CONNECT_RESPONSE)
				frame.header.set_length(frame.body)

				# Sending the response
				data_to_send = bytes(frame.to_knx())
				self.sock.sendto(data_to_send, addr)
				break
		return (frame, addr)

	

	async def main(self):#, room):
		"""Initializes the communication between any external KNX interface and us"""
		

		print("Waiting on port:", 3671, "at address", self.IPAddr)
		connection_config = ConnectionConfig(
					route_back=True,  # To enable connection through the docker
					connection_type=ConnectionType.TUNNELING,
					gateway_ip=self.IPAddr,
					gateway_port=3671,
				)
		self.xknx = XKNX(connection_config=connection_config)

		(frame, addr) = self.__create_connection(self.xknx)

		
		while True:
			# data, addr = self.sock.recvfrom(1024)
			
			# frame.from_knx(data)

			if isinstance(frame.body, TunnellingRequest):
				telegram: real_t.Telegram = frame.body.cemi.telegram

				sim_telegram: sim_t.Telegram = self.telegram_parser.from_knx_telegram(telegram)
				print(sim_telegram)

				#room.knxbus.transmit_telegram(sim_telegram)
				
				self.sock.sendto(self.__create_ack_data(frame), addr)
				print("ACK sent")

			# TODO: as a task?
			await self.__process_telegram_queue(addr)
					

	async def add_to_sending_queue(self, teleg: List[sim_t.Telegram]):
		async with self.__sending_lock:
			for t in teleg:
				await self.__sending_queue.put(self.telegram_parser.from_simulator_telegram(t))

	async def __process_telegram_queue(self, addr):
		"""Endless loop for processing telegrams."""
		# TODO: On another thread?
		while True:
			with self.__sending_lock:
				# Breaking up queue if None is pushed to the queue
				if self.__sending_queue:
						teleg = await self.__sending_queue.get()
						if teleg is None:
							return
						sender = KNXIPFrame(self.xknx)
						cemif = CEMIFrame(self.xknx).init_from_telegram(self.xknx, teleg)
						req = TunnellingRequest(self.xknx, cemi= cemif)
						sender = sender.init_from_body(req)
						print("Sending to SVSHI!")
						self.sock.sendto(bytes(sender.to_knx()), addr)
				
				
				
	def run(self):#, room):
		asyncio.run(self.main())

i = Interface()
from system.tools import GroupAddress, IndividualAddress
ga = GroupAddress('2-levels', 0,0)
ia = IndividualAddress(0,0,1)
test_sim = sim_t.Telegram(0, ia, ga, sim_t.BinaryPayload(True))
asyncio.run(i.add_to_sending_queue([test_sim]))
i.run()

