

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
OFFSET_AIRQUALITY_LEVELS = 15 # [y axis] Vertical space between sensor values of the same air quality sensor
OFFSET_AIRQUALITY_LABELS = 90 # [x axis] Horizontal offset between airquality sensor labels

OFFSET_DIMMER_RATIO = 5
OFFSET_MAX_DIMMER_RATIO = 150
OFFSET_AVAILABLE_DEVICES = 20
OFFSET_AVAILABLEDEVICES_LINE1 = WIN_LENGTH - 420 ###NOTE top window offset
OFFSET_AVAILABLEDEVICES_LINE2 = OFFSET_AVAILABLEDEVICES_LINE1 - 80
OFFSET_AVAILABLEDEVICES_LINE3 = OFFSET_AVAILABLEDEVICES_LINE2 - 80

# Box offsets
OFFSET_SIMTIME_BOX = 25
SIMTIME_BOX_WIDTH = 275
SIMTIME_BOX_LENGTH = 80
AVAILABLE_DEVICES_BOX_WIDTH = WIN_WIDTH - 2*WIN_BORDER - 2*ROOM_BORDER - ROOM_WIDTH 
AVAILABLE_DEVICES_BOX_LENGTH = 3*(OFFSET_AVAILABLEDEVICES_LINE1 - OFFSET_AVAILABLEDEVICES_LINE2) + OFFSET_AVAILABLE_DEVICES
DEVICE_LIST_BOX_WIDTH = AVAILABLE_DEVICES_BOX_WIDTH
OFFSET_SENSOR_LEVELS_BOX_Y_BOTTOM = WIN_LENGTH - 345 ###NOTE top window offset
SENSOR_LEVELS_BOX_LENGTH = 230
SENSOR_LEVELS_BOX_WIDTH = DEVICE_LIST_BOX_WIDTH
# DEVICE_LIST_BOX_LENGTH = 
OFFSET_DEVICELIST_BOX_TOP = 35
OFFSET_DEVICELIST_BOX_BOTTOM = 30

INITIAL_POSITION_BUTTON = 50
OFFSET_BUTTONS = 6


COMMANDLABEL_POS = (WIN_WIDTH-WIN_BORDER, 96*(WIN_LENGTH//100))
SIMLABEL_POS = (WIN_WIDTH-ROOM_WIDTH-WIN_BORDER-ROOM_BORDER, 95*(WIN_LENGTH//100))  #2*(self.__width//100)
TEXTBOX_POS = (80*(WIN_WIDTH//100), 91*(WIN_LENGTH//100))
DEVICELIST_POS = (WIN_BORDER, 35*(WIN_LENGTH//100))  #2*(self.__width//100)
SENSOR_LABELS_INIT = 85
BRIGHTNESS_LABEL_POS = (WIN_BORDER, SENSOR_LABELS_INIT*(WIN_LENGTH//100)) #2*(self.__width//100)
TEMPERATURE_LABEL_POS = (WIN_BORDER, (SENSOR_LABELS_INIT-6)*(WIN_LENGTH//100))  #2*(self.__width//100)
AIRSENSOR_LABEL_POS = (WIN_BORDER, (SENSOR_LABELS_INIT-12)*(WIN_LENGTH//100))
# Define the position of the buttons to interact with the user
BUTTON_PAUSE_POS = (INITIAL_POSITION_BUTTON*(WIN_WIDTH//100), 93*(WIN_LENGTH//100)) # 
BUTTON_STOP_POS = ((OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(WIN_WIDTH//100), 93*(WIN_LENGTH//100))
BUTTON_RELOAD_POS = ((2*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(WIN_WIDTH//100), 93*(WIN_LENGTH//100))
BUTTON_SAVE_POS = ((3*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(WIN_WIDTH//100), 93*(WIN_LENGTH//100))
BUTTON_DEFAULT_POS = ((4*OFFSET_BUTTONS+INITIAL_POSITION_BUTTON)*(WIN_WIDTH//100), 93*(WIN_LENGTH//100))



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
# color for humidity soil label
COLOR_RED = (149, 0, 12, 255)
COLOR_YELLOW = (172, 144, 25, 255)
COLOR_GREEN = (0, 79, 17, 255)
COLOR_BLUE =(3, 97, 190, 255)

FONT_BUTTON = 'Proxima Nova'
FONT_DEVICE = 'Lato'
FONT_SYSTEM_TITLE = 'Open Sans'
FONT_SYSTEM_INFO = 'Lato'
FONT_USER_INPUT = 'Roboto'
FONT_DIMMER_RATIO = 'Roc'
FONT_HUMIDITYSOIL_DROP = 'Roc'
FONT_INTERACTIVE = 'Roc'

FONT_SIZE_INTERACTIVE = 30 # dimmer and drop humidity soil
FONT_SIZE_DEVICESLIST = 14
FONT_SIZE_SENSOR_LABEL = 13
FONT_SIZE_SENSOR_LEVEL = 11
FONT_SIZE_INDIVIDUAL_ADDR = 10


OPACITY_DEFAULT = 255
OPACITY_MIN = 55
OPACITY_CLICKED = 150
OPACITY_ROOM = 222
OPACITY_ROOM_LABEL = 60

ROOM_BACKGROUND_PATH = 'png_simulator/bedroom.png'
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
DEVICE_HUMIDITYSOIL_PATH = 'png_simulator/humiditysoil.png'
DEVICE_HUMIDITYAIR_PATH = 'png_simulator/humidityair.png'
DEVICE_CO2_PATH = 'png_simulator/co2.png'
DROP_RED_PATH = 'png_simulator/drop_red.png'
DROP_YELLOW_PATH = 'png_simulator/drop_yellow.png'
DROP_GREEN_PATH = 'png_simulator/drop_green.png'
DROP_BLUE_PATH = 'png_simulator/drop_blue.png'
PERSON_CHILD_PATH = 'png_simulator/person_child.png'
PERSON_SITTING_PATH = 'png_simulator/person_sitting.png'

GREEN_PATH = 'png_simulator/green.png'