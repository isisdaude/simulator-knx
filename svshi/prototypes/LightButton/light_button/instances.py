###
### DO NOT TOUCH THIS FILE!!!
###

from models.switch import Switch
from models.binary import BinarySensor

from models.state import AppState
from models.SvshiApi import SvshiApi

LED = Switch('led')
BUTTON = BinarySensor('button')

svshi_api = SvshiApi()
app_state = AppState()