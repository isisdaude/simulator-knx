from itertools import tee
from telegram_parser import *
import xknx.telegram.telegram as knx_t
import system.telegrams as sim_t


class CommunicationInterface:
    '''Class that represents the interface allowing the simulator to transmit its telegrams to other interfaces'''

    def __init__(self, knx_address: str,
                 knx_port: int, group_address_to_payload: Dict[str, sim_t.Payload]):
        self.to_forward_to_network: List[sim_t.Telegram] = []
        self.to_forward_to_simulator: List[sim_t.Telegram] = []

        self.knx_address = knx_address
        self.knx_port = knx_port

        self.group_address_to_payload = group_address_to_payload
    
    def add_telegram_to_send(self, telegram: sim_t.Telegram):
        '''Adds a telegram to send to the network'''
        self.to_forward_to_network.append(telegram)

        self.communication.add_to_send(self.to_forward_to_network)

        self.communication.send_all()
        

    async def initialize_communication(self):
        '''Initializes all necessary processes for the external communication'''
        from xknx.xknx import XKNX
        from xknx.io.connection import ConnectionConfig, ConnectionType

        print("Initializing listeners...", flush=True)

        connection_config = ConnectionConfig(
            connection_type=ConnectionType.TUNNELING,
            gateway_ip=self.knx_address,
            gateway_port=self.knx_port,
        )

        xknx_for_listening = XKNX(
            daemon_mode=True, connection_config=connection_config)

        # self.communication = __ExternalCommunication(xknx_for_listening, self.group_address_to_payload)
        
        # print("Connecting to KNX and listening to telegrams...", flush=True)
        # self.communication.listen()

        # print("Disconnecting from KNX... ", end="", flush=True)
        # self.communication.stop()
        # print("done!", flush=True)

        await xknx_for_listening.start()

        await xknx_for_listening.stop()

    # def start_communication(self):
    #     '''Starts the communication process'''
    #     self.__initialize_communication()

class __ExternalCommunication:

    def __init__(self, xknx_for_listening: XKNX, group_address_to_payload: Dict[str, sim_t.Payload]):
        self.sending_buffer = []
        self.receiving_buffer = []
        self.exec_lock = asyncio.Lock()

        self.__xknx_for_listening = xknx_for_listening
        self.__xknx_for_listening.telegram_queue.register_telegram_received_cb(
            self.__telegram_received_cb
        )
        self.telegram_parser = TelegramParser(group_address_to_payload)

    async def listen(self):
        """
        Connects to KNX and listens infinitely for telegrams.
        """
        await self.__xknx_for_listening.start()

    async def stop(self):
        """
        Stops listening for telegrams and disconnects.
        """
        await self.__xknx_for_listening.stop()

    async def add_to_send(self, list_to_send: List[sim_t.Telegram]):
        '''Adds elements to the buffer of telegrams to send and parses them to knx telegrams'''
        async with self.exec_lock:
            for telegram in list_to_send:
                self.telegram_parser.from_simulator_telegram(telegram)
                self.sending_buffer.append(telegram)

    async def send_all(self):
        '''Sends all telegrams in the sending buffer'''
        async with self.exec_lock:
            sent = []
            for idx, telegram in enumerate(self.sending_buffer):
                await self.__xknx_for_listening.telegrams.put(telegram)
                sent.append(idx)
            # We remove all telegrams that were sent
            self.sending_buffer = [element for i, element in enumerate(
                self.sending_buffer) if i not in sent]

    async def __telegram_received_cb(self, telegram: knx_t.Telegram):
        """
        Updates the received buffer with simulated telegram once a knx telegram is received.
        """
        print('Received a telegram!')
        async with self.exec_lock:
            simulated_t = self.telegram_parser.from_knx_telegram(telegram)
            if simulated_t:
                await self.receiving_buffer.append(simulated_t)
