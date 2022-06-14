""" 
Module defining constant variables for the GUI Window and widgets
"""

## GUI dimensions definitions
WIN_WIDTH = 1500  # [x axis]
WIN_LENGTH = 1000  # [y axis]
ROOM_WIDTH = 1000  # [x axis] ## NOTE, ROOM_WIDTH and ROOM_LENGTH used to define size ratio for windows, if value changed here, it needs to be changed in system.system_tools also
ROOM_LENGTH = 800  # [y axis] ## NOTE (problem of circular import and problems with pytest and github CI if import in system_tools
WIN_BORDER = (
    20  # [x & y axis] Window border reference, sometimes only half or third is used
)
ROOM_BORDER = 40  # [x & y axis] Room walls
BOX_BORDER = WIN_BORDER / 3  # [x & y axis] Border width of GUI boxes

## Positions definitions
# Main boxes/labels positions
TIMEWEATHER_POS = (WIN_BORDER / 2, WIN_BORDER / 2 + ROOM_LENGTH + 2 * ROOM_BORDER)
SIMTIME_POS = (
    WIN_WIDTH - ROOM_WIDTH - WIN_BORDER - 2 * ROOM_BORDER,
    95 * (WIN_LENGTH // 100),
)
COMMANDLABEL_POS = (WIN_WIDTH - WIN_BORDER, 96 * (WIN_LENGTH // 100))
TEXTBOX_POS = (80 * (WIN_WIDTH // 100), 91 * (WIN_LENGTH // 100))
SENSOR_LABELS_INIT = 85  # Initial ratio for sensors labels positions
BRIGHTNESS_LABEL_POS = (WIN_BORDER, SENSOR_LABELS_INIT * (WIN_LENGTH // 100))
TEMPERATURE_LABEL_POS = (WIN_BORDER, (SENSOR_LABELS_INIT - 6) * (WIN_LENGTH // 100))
AIRSENSOR_LABEL_POS = (WIN_BORDER, (SENSOR_LABELS_INIT - 12) * (WIN_LENGTH // 100))
DEVICELIST_POS = (WIN_BORDER, 35 * (WIN_LENGTH // 100))
# GUI Buttons positions
INITIAL_POSITION_BUTTON = 51  # Initial ratio for buttons img positions
RATIO_OFFSET_BUTTONS = 6  # "ratio" offsets for buttons img positions
BUTTON_PAUSE_POS = (
    INITIAL_POSITION_BUTTON * (WIN_WIDTH // 100),
    93 * (WIN_LENGTH // 100),
)
BUTTON_STOP_POS = (
    (RATIO_OFFSET_BUTTONS + INITIAL_POSITION_BUTTON) * (WIN_WIDTH // 100),
    93 * (WIN_LENGTH // 100),
)
BUTTON_RELOAD_POS = (
    (2 * RATIO_OFFSET_BUTTONS + INITIAL_POSITION_BUTTON) * (WIN_WIDTH // 100),
    93 * (WIN_LENGTH // 100),
)
BUTTON_SAVE_POS = (
    (3 * RATIO_OFFSET_BUTTONS + INITIAL_POSITION_BUTTON) * (WIN_WIDTH // 100),
    93 * (WIN_LENGTH // 100),
)
BUTTON_DEFAULT_POS = (
    (4 * RATIO_OFFSET_BUTTONS + INITIAL_POSITION_BUTTON) * (WIN_WIDTH // 100),
    93 * (WIN_LENGTH // 100),
)


## Offset definitions and Box dimensions
# Global offsets
OFFSET_TITLE = 20  # [y axis] between Sensor Titles (Brightness, Temperature,...) and Sensors Labels(bright1, thermo1,...)
OFFSET_LABEL_DEVICE = 10  # [y axis] between Device PNG and label
OFFSET_LABEL_BUTTON = 15  # [y axis] between Button PNG and label
BOX_WIDTH = (
    WIN_WIDTH - 2 * WIN_BORDER - 2 * ROOM_BORDER - ROOM_WIDTH
)  # [x axis] width of information gui boxes
# SimTime / DateTime offsets
OFFSET_SIMTIME_BOX = 20  # [x axis] between simtime box position and "SimTime:" label
OFFSET_SIMTIME_DATE = 30  # [y axis] between simtime and datetime labels
OFFSET_SIMTIME_VALUE = 90  # [x axis] between "SimTime:" label and its value "00:00:00"
OFFSET_DATETIME_VALUE = 55  # [x axis] between "Date:" label and its value
SIMTIME_BOX_WIDTH = 320  # [x axis]
SIMTIME_BOX_LENGTH = 75  # [y axis]
# Out State offsets
OFFSET_OUTSTATE_LABEL = 6  # [x & y axis] between box border and out_state label
OFFSET_OUTSTATE_VALUE = 85  # [x axis] between "Out state:" and its values
OFFSET_SUN_MOON_Y = (
    35  # [y axis] between weather box position and moon/sun img position
)
OFFSET_SUN_MOON_X = (
    150  # [x axis] between weather box position and moon/sun img position
)
OFFSET_SUNRISE_SUNSET_Y = (
    25  # [y axis] between weather box position and sunrise/sunset img position
)
OFFSET_SUNRISE_X = 50  # [x axis] between weather box position and sunrise img position
OFFSET_SUNSET_X = 250  # [x axis] between weather box position and sunset img position
OFFSET_CLOUD_WIDTH_RATIO = 0.5  # [x axis] ratio to compute offset of overcast cloud img with width of sun/sunset/sunrise/moon sprite
OFFSET_CLOUD_DARK_WIDTH_RATIO = 0  # [x axis] ratio to compute offset of dark cloud img with width of sun/sunset/sunrise/moon sprite
OFFSET_CLOUD_LENGTH_RATIO = 0.5  # [y axis] ratio to compute offset of overcast cloud img with length of sun/sunset/sunrise/moon sprite
OFFSET_CLOUD_DARK_LENGTH_RATIO = 0.3  # [y axis] ratio to compute offset of dark cloud img with length of sun/sunset/sunrise/moon sprite
TIMEWEATHER_BOX_WIDTH = BOX_WIDTH  # [x axis]
TIMEWEATHER_BOX_LENGTH = WIN_LENGTH - WIN_BORDER / 2 - TIMEWEATHER_POS[1]  # [y axis]
# Sensors offsets
OFFSET_SENSOR_TITLE = 15  # [y axis] between sensor label and value
OFFSET_SENSOR_LEVELS = 100  # [x axis] between sensor elements
OFFSET_AIRQUALITY_LEVELS = (
    15  # [y axis] Vertical space between sensor values of the same air quality sensor
)
OFFSET_SENSOR_LEVELS_BOX_Y_BOTTOM = (
    WIN_LENGTH - 345
)  # [y axis] between top GUI window and position of sesnors box (origin is box bottom)
SENSOR_LEVELS_BOX_LENGTH = 230  # [y axis]
SENSOR_LEVELS_BOX_WIDTH = BOX_WIDTH  # [x axis]
# Availables devices offsets
OFFSET_AVAILABLE_DEVICES = (
    20  # [x axis] base offset between two consecutive available devices img
)
OFFSET_AVAILABLEDEVICES_LINE1 = (
    WIN_LENGTH - 420
)  # [y axis] between top GUI window and position of first line of available devices
OFFSET_AVAILABLEDEVICES_LINE2 = (
    OFFSET_AVAILABLEDEVICES_LINE1 - 80
)  # [y axis] between top GUI window and position of second line of available devices
OFFSET_AVAILABLEDEVICES_LINE3 = (
    OFFSET_AVAILABLEDEVICES_LINE2 - 80
)  # [y axis] between top GUI window and position of third line of available devices
AVAILABLE_DEVICES_BOX_WIDTH = BOX_WIDTH  # [x axis]
AVAILABLE_DEVICES_BOX_LENGTH = (
    3 * (OFFSET_AVAILABLEDEVICES_LINE1 - OFFSET_AVAILABLEDEVICES_LINE2)
    + OFFSET_AVAILABLE_DEVICES
)  # [y axis]
# Devices List offsets
OFFSET_DEVICESLIST_TITLE = (
    30  # [y axis] between "Devices in the Room:" title and the first device label
)
OFFSET_LIST_DEVICE = 33  # [y axis] between elements in room devices list
OFFSET_INDIVIDUAL_ADDR_LABEL = (
    12  # [x axis] between device label and its individual address label
)
DEVICE_LIST_BOX_WIDTH = BOX_WIDTH  # [x axis]
OFFSET_DEVICELIST_BOX_TOP = (
    35  # [y axis] between box top and "Devices in the Room:" title
)
OFFSET_DEVICELIST_BOX_BOTTOM = 30  # [y axis] between box bottom and last displayed list element when scroll is at the end of the list
# Special offsets
OFFSET_DIMMER_RATIO = (
    5  # [x axis] between end of dimer img and position of dimmer state (%)
)
OFFSET_MAX_DIMMER_RATIO = 150  # [y axis] max distance between dimmer img center and mouse when setting dimmer ratio


## Color definitions
# Color palette definitions
BLUEGREY50_RGBA = (237, 242, 247, 255)
BLUEGREY100_RGBA = (209, 222, 232, 255)
BLUEGREY200_RGBA = (175, 198, 214, 150)
BLUEGREY300_RGBA = (143, 171, 191, 150)
# BLUEGREY400_RGBA    = (112, 144, 166, 150)
# BLUEGREY500_RGBA    = (79, 115, 140, 150)
# BLUEGREY600_RGBA    = (54, 91, 116, 150)
BLUEGREY800_RGBA = (25, 53, 72, 255)
BLUEGRAY900_RGBA = (1, 38, 58, 255)
BLUETURQUOISE_RGBA = (100, 150, 165, 255)
BLUETURQUOISEDARK_RGBA = (90, 125, 145, 255)
BLACK_RGBA = (20, 20, 20, 255)
GRAYX11_RGBA = (190, 190, 190, 150)
# Dimmer ratio colors
COLOR_LOW = (149, 0, 12, 255)
COLOR_MEDIUM_LOW = (163, 52, 12, 255)
COLOR_MEDIUM_HIGH = (172, 144, 25, 255)
COLOR_HIGH = (0, 79, 17, 255)
# Humidity soil label colors
COLOR_RED = (149, 0, 12, 255)
COLOR_YELLOW = (172, 144, 25, 255)
COLOR_GREEN = (0, 79, 17, 255)
COLOR_BLUE = (3, 97, 190, 255)

# Global colors
COLOR_FONT_BUTTON = BLUEGREY50_RGBA
COLOR_FONT_ROOMDEVICE = BLACK_RGBA
# Room colors
COLOR_ROOM = GRAYX11_RGBA[:-1]  # [:-1] => shapes need only RGB, not alpha
COLOR_ROOM_BORDER = BLACK_RGBA[:-1]
# Simtime and Datetime box colors
COLOR_BOX_SIMTIME = BLUETURQUOISE_RGBA[:-1]
COLOR_BOX_SIMTIME_BORDER = BLUEGREY200_RGBA[:-1]
COLOR_FONT_SIMTIME_LABEL = BLUEGRAY900_RGBA
COLOR_FONT_SIMTIME_VALUE = BLUEGREY50_RGBA
# Weather  box colors
COLOR_BOX_WEATHER = BLUETURQUOISE_RGBA[:-1]
COLOR_BOX_WEATHER_BORDER = BLUEGREY200_RGBA[:-1]
COLOR_FONT_OUTSTATE_LABEL = BLUEGRAY900_RGBA
COLOR_FONT_OUTSTATE_VALUE = BLUEGREY50_RGBA
# Sensors box colors
COLOR_BOX_SENSORS = BLUETURQUOISE_RGBA[:-1]
COLOR_BOX_SENSORS_BORDER = BLUEGREY200_RGBA[:-1]
COLOR_FONT_SENSORS_TITLE = BLUEGRAY900_RGBA
COLOR_FONT_SENSORS_DEVICE = BLUEGREY800_RGBA
COLOR_FONT_SENSORS_VALUE = BLUEGREY50_RGBA
# Availables devices box colors
COLOR_BOX_AVAILABLEDEVICES = BLUETURQUOISEDARK_RGBA[:-1]
COLOR_BOX_AVAILABLEDEVICES_BORDER = BLUEGREY300_RGBA[:-1]
COLOR_FONT_AVAILABLEDEVICE = BLUEGRAY900_RGBA
# Room devices list colors
COLOR_BOX_DEVICESLIST = BLUETURQUOISEDARK_RGBA[:-1]
COLOR_BOX_DEVICESLIST_BORDER = BLUEGREY300_RGBA[:-1]
COLOR_FONT_DEVICESLIST_TITLE = BLUEGRAY900_RGBA
COLOR_FONT_DEVICESLIST_DEVICE = BLUEGREY50_RGBA
COLOR_FONT_DEVICESLIST_DEVICE_IA = BLUEGREY100_RGBA

## Font definitions
FONT_BUTTON = "Proxima Nova"
FONT_DEVICE = "Lato"
FONT_SYSTEM_TITLE = "Open Sans"
FONT_SYSTEM_INFO = "Lato"
FONT_USER_INPUT = "Roboto"
FONT_DIMMER_RATIO = "Roc"
FONT_HUMIDITYSOIL_DROP = "Roc"
FONT_INTERACTIVE = "Roc"
# Font size definitions
FONT_SIZE_DATETIME_TITLE = 15
FONT_SIZE_SIMTIME = 17
FONT_SIZE_DATE = 15
FONT_SIZE_INTERACTIVE = 30  # dimmer and humidity soil drop
FONT_SIZE_DEVICESLIST = 14
FONT_SIZE_SENSOR_LABEL = 13
FONT_SIZE_SENSOR_LEVEL = 11
FONT_SIZE_INDIVIDUAL_ADDR = 10
FONT_SIZE_OUT_STATE = 14
FONT_SIZE_SOILMOISTURE = 10

## Opacity definitions
OPACITY_DEFAULT = 255
OPACITY_MIN = 55
OPACITY_CLICKED = 150
OPACITY_ROOM = 222
OPACITY_ROOM_LABEL = 60

## PNG paths
# Main imgaes
ROOM_BACKGROUND_PATH = "png_simulator/bedroom.png"
BUTTON_RELOAD_PATH = "png_simulator/reload.png"
BUTTON_PAUSE_PATH = "png_simulator/pause.png"
BUTTON_PLAY_PATH = "png_simulator/play.png"
BUTTON_STOP_PATH = "png_simulator/stop.png"
BUTTON_SAVE_PATH = "png_simulator/save.png"
BUTTON_DEFAULT_PATH = "png_simulator/default_config.png"
# Device images
INDICATOR_SWITCH_ON = "png_simulator/switch_indicator_ON.png"
INDICATOR_SWITCH_OFF = "png_simulator/switch_indicator_OFF.png"
DEVICE_LED_ON_PATH = "png_simulator/lightbulb_ON.png"
DEVICE_LED_OFF_PATH = "png_simulator/lightbulb_OFF.png"
DEVICE_BUTTON_ON_PATH = "png_simulator/button_ON.png"
DEVICE_BUTTON_OFF_PATH = "png_simulator/button_OFF.png"
DEVICE_DIMMER_PATH = "png_simulator/dimmer.png"
DEVICE_DIMMER_ON_PATH = "png_simulator/dimmer_ON.png"
DEVICE_DIMMER_OFF_PATH = "png_simulator/dimmer_OFF.png"
DEVICE_BRIGHT_SENSOR_PATH = "png_simulator/brightness_sensor.png"
DEVICE_THERMO_NEUTRAL_PATH = "png_simulator/thermo_stable.png"
DEVICE_THERMO_COLD_PATH = "png_simulator/thermo_cold.png"
DEVICE_THERMO_HOT_PATH = "png_simulator/thermo_hot.png"
DEVICE_HEATER_OFF_PATH = "png_simulator/heater_OFF.png"
DEVICE_HEATER_ON_PATH = "png_simulator/heater_ON.png"
DEVICE_AC_ON_PATH = "png_simulator/AC_ON.png"
DEVICE_AC_OFF_PATH = "png_simulator/AC_OFF.png"
DEVICE_PRESENCE_ON_PATH = "png_simulator/presence_ON.png"
DEVICE_PRESENCE_OFF_PATH = "png_simulator/presence_OFF.png"
DEVICE_AIRSENSOR_PATH = "png_simulator/airsensor.png"
DEVICE_SWITCH_ON_PATH = "png_simulator/switch_indicator_ON.png"
DEVICE_SWITCH_OFF_PATH = "png_simulator/switch_indicator_OFF.png"
DEVICE_HUMIDITYSOIL_PATH = "png_simulator/humiditysoil.png"
DEVICE_HUMIDITYAIR_PATH = "png_simulator/humidityair.png"
DEVICE_CO2_PATH = "png_simulator/co2.png"
# Weather images
SUNRISE_PATH = "png_simulator/sunrise.png"
SUN_PATH = "png_simulator/sun.png"
SUNSET_PATH = "png_simulator/sunset.png"
MOON_PATH = "png_simulator/moon.png"
CLOUD_OVERCAST_PATH = "png_simulator/cloud_overcast.png"
CLOUD_DARK_PATH = "png_simulator/cloud_dark.png"
# Special images
DROP_RED_PATH = "png_simulator/drop_red.png"
DROP_YELLOW_PATH = "png_simulator/drop_yellow.png"
DROP_GREEN_PATH = "png_simulator/drop_green.png"
DROP_BLUE_PATH = "png_simulator/drop_blue.png"
PERSON_CHILD_PATH = "png_simulator/person_child.png"
PERSON_SITTING_PATH = "png_simulator/person_sitting.png"
VACUUM_PATH = "png_simulator/vacuum.png"
WINDOW_VERTICAL_PATH = "png_simulator/window_vertical.png"
WINDOW_HORIZONTAL_PATH = "png_simulator/window_horizontal.png"
