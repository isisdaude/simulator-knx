# KNX Smart Home simulator

A simulator of a KNX smart home according to the user's configurations.

when modifying classes:
-> modify the `__init__.py` files

When adding new devices types ("light",...):
-> modify the list in devices.abstractions

Config file json:
-> keys are names (area0, line0, led1, switch1,...)


launch pytest command
pytest -q --log-cli-level error simulator/tests/