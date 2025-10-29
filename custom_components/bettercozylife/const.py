"""Constants for the BetterCozyLife integration."""
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS, CONF_TYPE, CONF_TIMEOUT

DOMAIN = "bettercozylife"

CONF_DEVICES = "devices"
CONF_DEVICE_IP = CONF_IP_ADDRESS
CONF_DEVICE_TYPE = CONF_TYPE

DEVICE_TYPE_SWITCH = "switch"

# Device specific constants
SWITCH_TYPE_CODE = '00'

CMD_INFO = 0
CMD_QUERY = 2
CMD_SET = 3

# Options
CONF_FAILURE_THRESHOLD = "failure_threshold"
DEFAULT_FAILURE_THRESHOLD = 5
CONF_RETRY_WINDOW = "retry_window"
DEFAULT_TIMEOUT = 3
DEFAULT_RETRY_WINDOW = 10
