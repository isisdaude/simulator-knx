"""
TODO
"""

import os
import queue
import sys
import socket
import select
import threading

from datetime import datetime
from typing import List
from _thread import *

import xknx.telegram.telegram as real_t
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *
from xknx.knxip import TunnellingRequest

import system.telegrams as sim_t

sys.path.append(".")
sys.path.append("..")

# TODO: when to resend unacked?

class Interface:

    def __init__(self, room, telegram_logging: bool):
        from svshi_interface.telegram_parser import TelegramParser
        self.__telegram_logging = telegram_logging
        self.__last_tel_logged = None
        # if self.__telegram_logging:
        #     logging_path = "./logs/" + datetime.now().strftime("%d-%m-%Y_%H%M%S")
        #     os.mkdir(logging_path)
        #     self.__logging_file_path = logging_path + "/telegram_logs.txt" # path to txt file for telegram logs
        self.sequence_number = 0
        self.__not_acked_telegrams = {}
        self.__sending_queue: queue.Queue[sim_t.Telegram] = queue.Queue()

        # Any data sent to ssock shows up on rsock
        self.rsock, self.ssock = socket.socketpair()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        group_address_to_payload = {} # TODO: create correct bindings! for the moment, only BinaryPayload

        self.telegram_parser = TelegramParser(group_address_to_payload)

        hostname = socket.gethostname()
        self.IPAddr = socket.gethostbyname(hostname)

        server_address = (self.IPAddr, 3671)
        self.sock.bind(server_address)
        self.room = room # to get telegram file path because fails when relaoding (cannot stop thread)
        self.main()
    
    # def new_system_config(self):
    #     print(f"new system config interface")
    #     if self.__telegram_logging:
    #         print(f"telegram logging is true")
    #         logging_path = "./logs/" + datetime.now().strftime("%d-%m-%Y_%H%M%S")
    #         os.mkdir(logging_path)
    #         self.__logging_file_path = logging_path + "/telegram_logs.txt" # path to txt file for telegram logs
    #     # self.main(self.knxbus)
        

    # INITIALIZATION OF THE CONNECTION #
    def __create_connection(self, xknx: XKNX):
        """Creates a connection between a client and ourselves, with sequence number 0 and individual address 0.0.0"""
        
        #while True:
        data, addr = self.sock.recvfrom(1024)

        print("Address of SVSHI program:", addr)
        # Initializing the KNX/IP Frame to be sent
        frame = KNXIPFrame(xknx)
        frame.from_knx(data)
        frame.init(KNXIPServiceType.CONNECT_RESPONSE)
        frame.header.set_length(frame.body)

        # Sending the response
        data_to_send = bytes(frame.to_knx())
        self.sock.sendto(data_to_send, addr)

        while True:
            data, addr = self.sock.recvfrom(1024)

            frame = KNXIPFrame(xknx)
            frame.from_knx(data)
            if isinstance(frame.body, TunnellingRequest):
                self.sock.sendto(self.__create_ack_data(frame), addr)
            
            elif isinstance(frame.body, DisconnectRequest):
                frame = KNXIPFrame(xknx)
                frame.from_knx(data)
                frame.init(KNXIPServiceType.DISCONNECT_RESPONSE)
                frame.header.set_length(frame.body)

                data_to_send = bytes(frame.to_knx())
                self.sock.sendto(data_to_send, addr)
                break
        
        data, addr = self.sock.recvfrom(1024)

        # Initializing the KNX/IP Frame to be sent
        frame = KNXIPFrame(xknx)
        frame.from_knx(data)
        frame.init(KNXIPServiceType.CONNECT_RESPONSE)
        frame.header.set_length(frame.body)

        # Sending the response
        data_to_send = bytes(frame.to_knx())
        self.sock.sendto(data_to_send, addr)

        return (frame, addr)

    def __create_ack_data(self, frame: KNXIPFrame):
        """Creates ACK message to be sent as a response to a received telegram"""
        frame.init(KNXIPServiceType.TUNNELLING_ACK)
        frame.header.set_length(frame.body)
        return bytes(frame.to_knx())

    # RECEIVING TELEGRAMS
    def __receiving_telegrams(self, frame: KNXIPFrame, data, addr, knxbus):
        """Receives telegrams and forwards them to the system"""

        frame.from_knx(data)
        
        if isinstance(frame.body, TunnellingRequest):
            telegram: real_t.Telegram = frame.body.cemi.telegram

            sim_telegram: sim_t.Telegram = self.telegram_parser.from_knx_telegram(
                telegram
            )
            print("Received a telegram :\n", sim_telegram)
            if self.__telegram_logging:
                with open(self.room.telegram_logging_file_path, "a+") as log_file:
                    if self.__last_tel_logged is None or self.__last_tel_logged == 'sent':
                        log_file.write("\n++++++++++ Telegram received ++++++++++")
                        self.__last_tel_logged = 'recv'
                    log_file.write(f"\nSVSHI -> Simulator: {telegram}")
            ## TODO log telegrams
            if sim_telegram is not None:
                knxbus.transmit_telegram(sim_telegram)
                self.sock.sendto(self.__create_ack_data(frame), addr)
                # keyboard = Controller()
                # print("======== press enter keyboard controller ===========")
                # keyboard.press(Key.enter)
                # keyboard.release(Key.enter)

        elif isinstance(frame.body, ConnectionStateRequest):
            frame.init(KNXIPServiceType.CONNECTIONSTATE_RESPONSE)
            frame.body.communication_channel_id = 0
            frame.header.set_length(frame.body)
            self.sock.sendto(bytes(frame.to_knx()), addr)

        elif isinstance(frame.body, TunnellingAck):
            self.__not_acked_telegrams.pop(frame.body.sequence_counter, None)

    # SENDING TELEGRAMS
    def add_to_sending_queue(self, teleg: List[sim_t.Telegram]):
        """Adds to the queue of telegrams to be sent to the external interface"""
        for t in teleg:
            t_xknx = self.telegram_parser.from_simulator_telegram(t)
            self.__sending_queue.put(t_xknx)
        self.ssock.send(b"\x00")

    def __process_telegram_queue(self, addr):
        """Processes telegrams to be sent to the external interface"""
        # Breaking up queue if None is pushed to the queue
        if self.__sending_queue:
            teleg = self.__sending_queue.get()
            if teleg is None:
                return
            sender = KNXIPFrame(self.xknx)
            cemif = CEMIFrame(self.xknx).init_from_telegram(self.xknx, teleg)
            req = TunnellingRequest(self.xknx, cemi=cemif)
            # req.sequence_counter = self.sequence_number
            # self.sequence_number += 1

            # Wait to receive the ACK
            sender = sender.init_from_body(req)
            self.sock.sendto(bytes(sender.to_knx()), addr)
            if self.__telegram_logging:
                with open(self.room.telegram_logging_file_path, "a+") as log_file:
                    if self.__last_tel_logged is None or self.__last_tel_logged == 'recv':
                        log_file.write("\n---------- Telegram sent ----------")
                        self.__last_tel_logged = 'sent'
                    log_file.write(f"\nSimulator -> SVSHI: {teleg}")
            # data, addr = self.sock.recvfrom(1024)

            # sender.from_knx(data)
            # if isinstance(sender.body, TunnellingAck):
            #     self.__not_acked_telegrams.pop(sender.body.sequence_counter, None)
            
            self.__not_acked_telegrams[req.sequence_counter] = bytes(sender.to_knx()) # TODO: when do we resend?

    # MAIN
    def main(self):
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

        def threaded():
            while True:
                # When either main_socket has data or rsock has data, select.select will return
                rlist, _, _ = select.select([self.sock, self.rsock], [], [])
                for ready_socket in rlist:
                    if ready_socket is self.sock:
                        data = self.sock.recv(1024)
                        # Do stuff with data, fill this up with your code
                        self.__receiving_telegrams(frame, data, addr, self.room.knxbus)
                    else:
                        # print("on est dans le coing")
                        # Ready_socket is rsock
                        self.rsock.recv(1)  # Dump the ready mark
                        # Send the data.
                        self.__process_telegram_queue(addr)

        main_functions = threading.Thread(target=threaded, args=())
        main_functions.start()


# def test():
#     i = Interface(1)
#     from system.system_tools import GroupAddress, IndividualAddress

#     ga = GroupAddress("2-levels", 0, 0)
#     ia = IndividualAddress(0, 0, 1)
#     test_sim = sim_t.Telegram(0, ia, ga, sim_t.BinaryPayload(True))
#     time.sleep(5)
#     for _ in range(3):
#         i.add_to_sending_queue([test_sim])
        
# test()