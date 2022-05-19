

WIN_WIDTH = 1500
WIN_LENGTH = 1000
WIN_BORDER = 20  # Space between the window border and the Room wodget borders
ROOM_BORDER = 40 # margin to place devices at room boundaries
ROOM_WIDTH = 1000
ROOM_LENGTH = 800

OFFSET_ROOM_LABEL = 40
OFFSET_TITLE = 20 # [y axis] Between Titles and Information (e.g. devices list, brightness/temperature values)
OFFSET_SIMTIME_TITLE = 35
OFFSET_DEVICESLIST_TITLE = 30
# OFFSET_LIST_ELEMENT = 20 # [y axis] Between element in list (e.g. devices list in the room)
OFFSET_LIST_DEVICE = 33 # [y axis] Between element in list (e.g. devices list in the room)
OFFSET_LABEL_DEVICE = 10 # [y axis] Between Device PNG and label
OFFSET_LABEL_BUTTON = 15 # [y axis] Between Button PNG and label
OFFSET_INDIVIDUAL_ADDR_LABEL = 12
OFFSET_SENSOR_TITLE = 15 # [y axis] Between sensor label and level
OFFSET_SENSOR_LEVELS = 100 # [x axis] Horizontal distance between sensor elements

OFFSET_DIMMER_RATIO = 5
OFFSET_MAX_DIMMER_RATIO = 150
OFFSET_AVAILABLE_DEVICES = 20
OFFSET_AVAILABLEDEVICES_LINE1 = WIN_LENGTH - 330
OFFSET_AVAILABLEDEVICES_LINE2 = OFFSET_AVAILABLEDEVICES_LINE1 - 80

# Box offsets
OFFSET_SIMTIME_BOX = 20
SIMTIME_BOX_WIDTH = 275
SIMTIME_BOX_LENGTH = 80
AVAILABLE_DEVICES_BOX_WIDTH = WIN_WIDTH - 2*WIN_BORDER - 2*ROOM_BORDER - ROOM_WIDTH 
AVAILABLE_DEVICES_BOX_LENGTH = 2 * (OFFSET_AVAILABLEDEVICES_LINE1 - OFFSET_AVAILABLEDEVICES_LINE2 + OFFSET_AVAILABLE_DEVICES)
DEVICE_LIST_BOX_WIDTH = AVAILABLE_DEVICES_BOX_WIDTH
OFFSET_SENSOR_LEVELS_BOX_Y = WIN_LENGTH - 220 
SENSOR_LEVELS_BOX_WIDTH = DEVICE_LIST_BOX_WIDTH
# DEVICE_LIST_BOX_LENGTH = 
OFFSET_DEVICELIST_BOX_TOP = 35
OFFSET_DEVICELIST_BOX_BOTTOM = 30

INITIAL_POSITION_BUTTON = 50
OFFSET_BUTTONS = 6


MAX_SIZE_DEVICE_LIST = 14


BLUENAVY_RGB = (1, 1, 122)
BLUEAIRFORCE_RGB = (75, 119, 190)
BLUEMARINER_RGB = (44, 130, 217)
BLUEMOODY_RGB = (132, 141, 223)
BLUESUMMERSKY_RGB = (30, 140, 211)
BLUEMINSK_RGB = (50, 50, 120)
BLUEJORDY_RGB = (137, 212, 244)
BLUEIRIS_RGB = (0, 176, 221)

# color for dimmer ratio
COLOR_LOW = (149, 0, 12, 255)
COLOR_MEDIUM_LOW = (163, 52, 12, 255)
COLOR_MEDIUM_HIGH = (172, 144, 25, 255)
COLOR_HIGH = (0, 79, 17, 255)

FONT_BUTTON = 'Proxima Nova'
FONT_DEVICE = 'Lato'
FONT_SYSTEM_TITLE = 'Open Sans'
FONT_SYSTEM_INFO = 'Lato'
FONT_USER_INPUT = 'Roboto'
FONT_DIMMER_RATIO = 'Roc'

FONT_SIZE_DEVICESLIST = 14
FONT_SIZE_SENSOR_LABEL = 13
FONT_SIZE_SENSOR_LEVEL = 11
FONT_SIZE_INDIVIDUAL_ADDR = 10


OPACITY_DEFAULT = 255
OPACITY_MIN = 55
OPACITY_CLICKED = 150
OPACITY_ROOM = 222
OPACITY_ROOM_LABEL = 60

ROOM_BACKGROUND_PATH = 'png_simulator/room.png'
BUTTON_RELOAD_PATH = 'png_simulator/reload.png'
BUTTON_PAUSE_PATH = 'png_simulator/pause.png'
BUTTON_PLAY_PATH = 'png_simulator/play.png'
BUTTON_STOP_PATH = 'png_simulator/stop.png'
BUTTON_SAVE_PATH = 'png_simulator/save.png'
BUTTON_DEFAULT_PATH = 'png_simulator/default_config.png'
INDICATOR_SWITCH_ON = 'png_simulator/switch_indicator_ON.png'
INDICATOR_SWITCH_OFF = 'png_simulator/switch_indicator_OFF.png'
DEVICE_LED_ON_PATH = 'png_simulator/lightbulb_ON.png'
DEVICE_LED_OFF_PATH = 'png_simulator/lightbulb_OFF.png'
DEVICE_BUTTON_ON_PATH = 'png_simulator/button_ON.png'
DEVICE_BUTTON_OFF_PATH = 'png_simulator/button_OFF.png'
DEVICE_DIMMER_PATH = 'png_simulator/dimmer.png'
DEVICE_DIMMER_ON_PATH = 'png_simulator/dimmer_ON.png'
DEVICE_DIMMER_OFF_PATH = 'png_simulator/dimmer_OFF.png'
DEVICE_BRIGHT_SENSOR_PATH = 'png_simulator/brightness_sensor.png'
DEVICE_THERMO_PATH = 'png_simulator/thermo_stable.png'
DEVICE_THERMO_COLD_PATH = 'png_simulator/thermo_cold.png'
DEVICE_THERMO_HOT_PATH = 'png_simulator/thermo_hot.png'
DEVICE_HEATER_OFF_PATH = 'png_simulator/heater_OFF.png'
DEVICE_HEATER_ON_PATH = 'png_simulator/heater_ON.png'
DEVICE_AC_ON_PATH = 'png_simulator/AC_ON.png'
DEVICE_AC_OFF_PATH = 'png_simulator/AC_OFF.png'
DEVICE_PRESENCE_ON_PATH = 'png_simulator/presence_ON.png'
DEVICE_PRESENCE_OFF_PATH = 'png_simulator/presence_OFF.png'
DEVICE_AIRSENSOR_PATH = 'png_simulator/airsensor.png'
DEVICE_SWITCH_ON_PATH = 'png_simulator/switch_indicator_ON.png'
DEVICE_SWITCH_OFF_PATH = 'png_simulator/switch_indicator_OFF.png'

GREEN_PATH = 'png_simulator/green.png'