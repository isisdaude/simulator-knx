"""
Main class that implements the interface with sending and receving operations
"""

import queue
import sys
import socket
import select
import threading

from typing import List, Tuple
from _thread import *

import xknx.telegram.telegram as real_t
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *
from xknx.knxip import TunnellingRequest


sys.path.append(".")
sys.path.append("..")


class Interface:
    def __init__(self, room, telegram_logging: bool, testing=False) -> None:
        """Initalizes the interface used for communication with SVSHI"""
        from svshi_interface.telegram_parser import TelegramParser
        import system.telegrams as sim_t

        self.__telegram_logging = telegram_logging
        self.__last_tel_logged = None
        self.__sending_queue: queue.Queue[sim_t.Telegram] = queue.Queue()

        # Any data sent to ssock shows up on rsock
        self.__rsock, self.__ssock = socket.socketpair()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.__telegram_parser = TelegramParser()

        hostname = socket.gethostname()
        self.__IPAddr = socket.gethostbyname(hostname)

        server_address = (self.__IPAddr, 3671)
        self.__sock.bind(server_address)
        self.room = room  # to get telegram file path because fails when reloading (cannot stop thread)

        if not testing:
            self.main()

    # INITIALIZATION OF THE CONNECTION #
    def __create_connection(self, xknx: XKNX) -> Tuple[KNXIPFrame, Any]:
        """Creates a connection between a client and ourselves, with sequence number 0 and individual address 0.0.0"""

        data, addr = self.__sock.recvfrom(1024)

        print("Address of SVSHI:", addr)

        # Initializing the KNX/IP Frame to be sent
        frame = KNXIPFrame(xknx)
        frame.from_knx(data)
        frame.init(KNXIPServiceType.CONNECT_RESPONSE)
        frame.header.set_length(frame.body)

        # Sending the response
        data_to_send = bytes(frame.to_knx())
        self.__sock.sendto(data_to_send, addr)

        while True:
            data, addr = self.__sock.recvfrom(1024)

            frame = KNXIPFrame(xknx)
            frame.from_knx(data)
            if isinstance(frame.body, TunnellingRequest):
                self.__sock.sendto(self.__create_ack_data(frame), addr)

            elif isinstance(frame.body, DisconnectRequest):
                frame = KNXIPFrame(xknx)
                frame.from_knx(data)
                frame.init(KNXIPServiceType.DISCONNECT_RESPONSE)
                frame.header.set_length(frame.body)

                data_to_send = bytes(frame.to_knx())
                self.__sock.sendto(data_to_send, addr)
                break

        data, addr = self.__sock.recvfrom(1024)

        # Initializing the KNX/IP Frame to be sent
        frame = KNXIPFrame(xknx)
        frame.from_knx(data)
        frame.init(KNXIPServiceType.CONNECT_RESPONSE)
        frame.header.set_length(frame.body)

        # Sending the response
        data_to_send = bytes(frame.to_knx())
        self.__sock.sendto(data_to_send, addr)

        return (frame, addr)

    def __create_ack_data(self, frame: KNXIPFrame) -> bytes:
        """Creates ACK message to be sent as a response to a received telegram"""
        frame.init(KNXIPServiceType.TUNNELLING_ACK)
        frame.header.set_length(frame.body)
        return bytes(frame.to_knx())

    # RECEIVING TELEGRAMS
    def __receiving_telegrams(
        self, frame: KNXIPFrame, data: bytes, addr: Any, knxbus=None
    ) -> None:
        """Receives telegrams and forwards them to the system"""

        frame.from_knx(data)

        if isinstance(frame.body, TunnellingRequest):
            telegram: real_t.Telegram = frame.body.cemi.telegram
            import system.telegrams as sim_t

            sim_telegram: sim_t.Telegram = self.__telegram_parser.from_knx_telegram(
                telegram
            )
            print("Received a telegram :\n", sim_telegram)
            if self.__telegram_logging:
                with open(self.room.telegram_logging_file_path, "a+") as log_file:
                    if (
                        self.__last_tel_logged is None
                        or self.__last_tel_logged == "sent"
                    ):
                        log_file.write("\n++++++++++ Telegram received ++++++++++")
                        self.__last_tel_logged = "recv"
                    log_file.write(f"\nSVSHI -> Simulator: {telegram}")

            if sim_telegram is not None:
                knxbus.transmit_telegram(sim_telegram)
                self.__sock.sendto(self.__create_ack_data(frame), addr)

        elif isinstance(frame.body, ConnectionStateRequest):
            frame.init(KNXIPServiceType.CONNECTIONSTATE_RESPONSE)
            frame.body.communication_channel_id = 0
            frame.header.set_length(frame.body)
            self.__sock.sendto(bytes(frame.to_knx()), addr)

        elif isinstance(frame.body, TunnellingAck):
            pass

    # SENDING TELEGRAMS

    def add_to_sending_queue(self, teleg) -> None:
        """Adds to the queue of telegrams to be sent to the external interface"""
        for t in teleg:
            t_xknx = self.__telegram_parser.from_simulator_telegram(t)
            self.__sending_queue.put(t_xknx)
        self.__ssock.send(b"\x00")

    def __process_telegram_queue(self, addr: Any) -> None:
        """Processes telegrams to be sent to the external interface"""
        # Breaking up queue if None is pushed to the queue
        if self.__sending_queue:
            teleg = self.__sending_queue.get()
            if teleg is None:
                return
            sender = KNXIPFrame(self.__xknx)
            cemif = CEMIFrame(self.__xknx).init_from_telegram(self.__xknx, teleg)
            req = TunnellingRequest(self.__xknx, cemi=cemif)

            # Wait to receive the ACK
            sender = sender.init_from_body(req)
            self.__sock.sendto(bytes(sender.to_knx()), addr)
            if self.__telegram_logging:
                with open(self.room.telegram_logging_file_path, "a+") as log_file:
                    if (
                        self.__last_tel_logged is None
                        or self.__last_tel_logged == "recv"
                    ):
                        log_file.write("\n---------- Telegram sent ----------")
                        self.__last_tel_logged = "sent"
                    log_file.write(f"\nSimulator -> SVSHI: {teleg}")

    # MAIN
    def main(self) -> None:
        """Initializes the communication between any external KNX interface and us"""

        print("Waiting on port:", 3671, "at address", self.__IPAddr)
        connection_config = ConnectionConfig(
            route_back=True,  # To enable connection through the docker
            connection_type=ConnectionType.TUNNELING,
            gateway_ip=self.__IPAddr,
            gateway_port=3671,
        )
        self.__xknx = XKNX(connection_config=connection_config)

        (frame, addr) = self.__create_connection(self.__xknx)

        def threaded():
            while True:
                data = None
                # When either main_socket has data or rsock has data, select.select will return
                rlist, _, _ = select.select([self.__sock, self.__rsock], [], [])
                for ready_socket in rlist:
                    if ready_socket is self.__sock:
                        data = self.__sock.recv(1024)
                        # Ready socket is sock, we receive telegrams from SVSHI
                        if data == b"\x11":
                            break
                        self.__receiving_telegrams(frame, data, addr, self.room.knxbus)
                    else:
                        # Ready_socket is rsock, we need to send to SVSHI
                        signal = self.__rsock.recv(1)  # Dump the ready mark

                        # Send the data.
                        self.__process_telegram_queue(addr)

                if data == b"\x11":
                    break

        main_functions = threading.Thread(target=threaded, args=())
        main_functions.start()
