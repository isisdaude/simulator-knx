import os
import socket

import asyncio
import threading
import signal
import sys
import pytest

sys.path.append('..')
sys.path.append('.')

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

    def start(self):

        # def threaded():
            def main():
                
                print("Starting communication")
                hostname = socket.gethostname()
                IPAddr = socket.gethostbyname(hostname)  
                connection_config = ConnectionConfig(
                        route_back=True,  # To enable connection through the docker
                        connection_type=ConnectionType.TUNNELING,
                        gateway_ip=IPAddr,
                        gateway_port=3671,
                    )
                xknx_read = XKNX( connection_config=connection_config)

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5)
                sock.bind((IPAddr, 5151))
                dest = (IPAddr, 3671)
                # Initializing the KNX/IP Frame to be sent
                frame = KNXIPFrame(xknx_read)
                frame.init(KNXIPServiceType.CONNECT_REQUEST)
                frame.header.set_length(frame.body)

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
                
                
                xknx = XKNX( connection_config = connection_config, daemon_mode=True)
                
                frame = KNXIPFrame(xknx)
                frame.init(KNXIPServiceType.CONNECT_REQUEST)
                frame.header.set_length(frame.body)
                sock.sendto(bytes(frame.to_knx()), dest)

                sock.recvfrom(1024)
                print("Connected")

                self.communication_engaged = True

            main()

def test_communication():
    svshi = SVSHI_TEST()

    speed_factor = 180
    group_address_style = '3-levels'
    # room1_config = {"name":"bedroom1", "dimensions":[20,20,3]}
    # Test correct room configuration (constructor call)
    import system
    def room_create():
        
        room = system.Room("bedroom1", 20, 20, 3, speed_factor, group_address_style, insulation='good', test_mode=True, svshi_mode=True)
        # from system.telegrams import Telegram as sim_t
        # from system.system_tools import IndividualAddress, GroupAddress
        # from system.telegrams import BinaryPayload

        # ga1 = GroupAddress('3-levels', 0, 0, 0)
        # ia1 = IndividualAddress(1, 1, 1) 

        # simulator_t = sim_t(0, ia1, ga1, BinaryPayload(True))
        # sleep(3)
        # room.interface_device.update_state(simulator_t)
    
    # def service_shutdown(signum, frame):
    #     print('Caught signal %d' % signum)
    #     raise Exception
        
    start_func = threading.Thread(target=room_create, args=())
    start_func.start()
    svshi.start()
    assert svshi.communication_engaged
    os._exit(0)
        
        