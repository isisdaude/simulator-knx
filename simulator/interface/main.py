from communication_interface import *

class Main:
    '''Test class for our KNX telegram exchange framework'''

    from system.telegrams import ButtonPayload, HeaterPayload
    group_address_to_payload_example = {
        '0/0/0': ButtonPayload,
        '0/0': HeaterPayload,
    }
    com = CommunicationInterface('224.0.23.12', 3671, group_address_to_payload_example)

    asyncio.run(com.initialize_communication())