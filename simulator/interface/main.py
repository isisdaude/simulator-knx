import sys
import time
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
import select
import socket
import queue

import system.telegrams as sim_t

class Interface:
	# __sending_lock = asyncio.Lock()

	def __init__(self):
		self.__sending_queue: queue.Queue[sim_t.Telegram] = queue.Queue()

			# Any data sent to ssock shows up on rsock
		self.rsock, self.ssock = socket.socketpair()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		from telegram_parser import TelegramParser
		group_address_to_payload = {} #TODO: create correct bindings! for the moment, only BinaryPayload

		self.telegram_parser = TelegramParser(group_address_to_payload)

		
		# self.sock.setblocking(False)
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

	

	async def main(self, room):
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


		# test_sim = sim_t.Telegram(0, ia, ga, sim_t.BinaryPayload(True))
		# await self.add_to_sending_queue([test_sim])

		print("before loop")
		while True:
			# When either main_socket has data or rsock has data, select.select will return
			rlist, _, _ = select.select([self.sock, self.rsock], [], [])
			print("something arrived")
			for ready_socket in rlist:
				if ready_socket is self.sock:
					data = self.sock.recv(1024)
					# Do stuff with data, fill this up with your code
					await self.__receiving_telegrams(frame, data, addr)
				else:
					# Ready_socket is rsock
					self.rsock.recv(1)  # Dump the ready mark
					# Send the data.
					await self.__process_telegram_queue(addr)

	
	async def __receiving_telegrams(self, frame, data, addr):
		print("Received")
		frame.from_knx(data)

		if isinstance(frame.body, TunnellingRequest):
			telegram: real_t.Telegram = frame.body.cemi.telegram

			sim_telegram: sim_t.Telegram = self.telegram_parser.from_knx_telegram(telegram)
			print(sim_telegram)

			#room.knxbus.transmit_telegram(sim_telegram)
			
			self.sock.sendto(self.__create_ack_data(frame), addr)
			print("ACK sent")

	async def add_to_sending_queue(self, teleg: List[sim_t.Telegram]):
		for t in teleg:
			t_xknx = self.telegram_parser.from_simulator_telegram(t)
			self.__sending_queue.put(t_xknx)
		self.ssock.send(b"\x00")

	async def __process_telegram_queue(self, addr):
		"""Endless loop for processing telegrams."""
		print("Sending")
				# Breaking up queue if None is pushed to the queue
		if self.__sending_queue:
				teleg = self.__sending_queue.get()
				print("Telegram:", teleg)
				if teleg is None:
					return
				sender = KNXIPFrame(self.xknx)
				cemif = CEMIFrame(self.xknx).init_from_telegram(self.xknx, teleg)
				req = TunnellingRequest(self.xknx, cemi= cemif)
				sender = sender.init_from_body(req)
				print("Sending to SVSHI!")
				self.sock.sendto(bytes(sender.to_knx()), addr)
				# TODO: add ACK receiving that SVSHI sends? --> if not received, should not resend (2x) --> list of acked to be removed
					
	async def run(self, room):
		await self.main(room)


async def test():
	i = Interface()
	from system.tools import GroupAddress, IndividualAddress
	ga = GroupAddress('2-levels', 0,0)
	ia = IndividualAddress(0,0,1)
	test_sim = sim_t.Telegram(0, ia, ga, sim_t.BinaryPayload(True))
	t = asyncio.create_task(i.run(1))
	for j in range(3):
		await i.add_to_sending_queue([test_sim])
		print("bonjour")

asyncio.run(test())

# i = Interface()
# from system.tools import GroupAddress, IndividualAddress
# ga = GroupAddress('2-levels', 0,0)
# ia = IndividualAddress(0,0,1)
# test_sim = sim_t.Telegram(0, ia, ga, sim_t.BinaryPayload(True))
# # asyncio.run(i.add_to_sending_queue([test_sim]))
# asyncio.run(i.run(1))
