import logging

LOGGING_LEVEL = logging.INFO
logging.basicConfig(level=LOGGING_LEVEL, format='%(asctime)s | [%(levelname)s] %(message)s') #%(name)s : username (e.g. root)

room_key = 'key_of_the_room'
logging.error(f" '{room_key}' not defined in config file, or wrong number of rooms")

assert -3 >= 0

print("assertion done")
