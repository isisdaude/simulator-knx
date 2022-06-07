###
### DO NOT TOUCH THIS FILE!!!
###

from models.switch import Switch
from models.binary import BinarySensor
from models.temperature import TemperatureSensor

from models.state import AppState
from models.SvshiApi import SvshiApi

LED = Switch('led')
BUTTON = BinarySensor('button')
THERMOMETER = TemperatureSensor('thermometer')

svshi_api = SvshiApi()
app_state = AppState()