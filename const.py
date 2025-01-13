"""Constants for the BetterCozyLife integration."""
from homeassistant.const import (
    CONF_NAME,
    CONF_IP_ADDRESS,
    CONF_TYPE,
)

DOMAIN = "bettercozylife"

CONF_DEVICES = "devices"
CONF_DEVICE_IP = CONF_IP_ADDRESS
CONF_DEVICE_TYPE = CONF_TYPE

DEVICE_TYPE_SWITCH = "switch"
DEVICE_TYPE_LIGHT = "light"

# Device specific constants
SWITCH_TYPE_CODE = '00'
LIGHT_TYPE_CODE = '01'

CMD_INFO = 0
CMD_QUERY = 2
CMD_SET = 3