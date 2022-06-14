""" Test communication through IP interface"""

import os
import socket

import asyncio
import threading
import signal
import sys
import pytest

sys.path.append("..")
sys.path.append(".")

from time import sleep
from xknx.core.value_reader import ValueReader
from xknx.dpt.dpt import DPTArray, DPTBase, DPTBinary
from xknx.telegram.apci import GroupValueWrite
from xknx.telegram.telegram import Telegram
from xknx.telegram.address import GroupAddress
from xknx.xknx import XKNX
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.xknx import XKNX
import xknx.telegram.telegram as real_t
from xknx import XKNX
from xknx.knxip import *
from xknx.io.connection import ConnectionConfig, ConnectionType
from xknx.io.transport import *
from xknx.io.knxip_interface import *
from xknx.io.request_response import *
from xknx.knxip import TunnellingRequest
import socket


class SVSHI_TEST:
    def __init__(self) -> None:
        self.communication_engaged = False

    def start(self, interface):
        print("Starting communication")
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        connection_config = ConnectionConfig(
            route_back=True,  # To enable connection through the docker
            connection_type=ConnectionType.TUNNELING,
            gateway_ip=IPAddr,
            gateway_port=3671,
        )
        xknx_read = XKNX(connection_config=connection_config)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.bind((IPAddr, 5151))
        dest = (IPAddr, 3671)
        # Initializing the KNX/IP Frame to be sent
        frame = KNXIPFrame(xknx_read)
        frame.init(KNXIPServiceType.CONNECT_REQUEST)
        frame.header.set_length(frame.body)

        # threading.Thread(target=)

        b = None
        while b is None:
            sock.sendto(bytes(frame.to_knx()), dest)
            try:
                b = sock.recvfrom(1024)
            except TimeoutError:
                continue

        print("Connected")

        frame = KNXIPFrame(xknx_read)
        frame.init(KNXIPServiceType.DISCONNECT_REQUEST)
        frame.header.set_length(frame.body)
        sock.sendto(bytes(frame.to_knx()), dest)

        sock.recvfrom(1024)
        print("Disconnected")

        xknx = XKNX(connection_config=connection_config, daemon_mode=True)

        frame = KNXIPFrame(xknx)
        frame.init(KNXIPServiceType.CONNECT_REQUEST)
        frame.header.set_length(frame.body)
        sock.sendto(bytes(frame.to_knx()), dest)

        sock.recvfrom(1024)
        print("Connected")

        from system import telegrams as sim_t
        import system.system_tools as addr

        ga1 = addr.GroupAddress("3-levels", 0, 0, 0)
        ia1 = addr.IndividualAddress(1, 1, 1)

        simulator_t = sim_t.Telegram(ia1, ga1, sim_t.BinaryPayload(True))
        interface.add_to_sending_queue([simulator_t])

        sock.recvfrom(1024)

        sock.sendto(interface._Interface__create_ack_data(frame), dest)

        knx_t = Telegram(
            destination_address=GroupAddress("1/1/1"),
            payload=GroupValueWrite(DPTBinary(1)),
        )

        sender = KNXIPFrame(xknx)
        cemif = CEMIFrame(xknx).init_from_telegram(xknx, knx_t)
        req = TunnellingRequest(xknx, cemi=cemif)

        # Wait to receive the ACK
        sender = sender.init_from_body(req)
        sock.sendto(bytes(sender.to_knx()), dest)

        sock.sendto(b"\x11", dest)

        self.communication_engaged = True


def test_communication():
    from svshi_interface.main import Interface
    import system

    svshi = SVSHI_TEST()
    speed_factor = 180
    group_address_style = "3-levels"
    room = system.Room(
        "bedroom1",
        20,
        20,
        3,
        speed_factor,
        group_address_style,
        insulation="good",
        test_mode=True,
    )

    interface = Interface(room, False, testing=True)

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    connection_config = ConnectionConfig(
        route_back=True,  # To enable connection through the docker
        connection_type=ConnectionType.TUNNELING,
        gateway_ip=IPAddr,
        gateway_port=3671,
    )
    xknx = XKNX(connection_config=connection_config)

    start_comm = threading.Thread(target=interface.main, args=())
    start_comm.start()

    svshi.start(interface)

    start_comm.join()
    assert svshi.communication_engaged
