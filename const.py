"""Constants for the CozyLife Direct Control integration."""
DOMAIN = "cozylife_direct"

CONF_DEVICES = "devices"
CONF_DEVICE_IP = "ip"
CONF_DEVICE_TYPE = "type"

DEVICE_TYPE_SWITCH = "switch"
DEVICE_TYPE_LIGHT = "light"

# Device specific constants
SWITCH_TYPE_CODE = '00'
LIGHT_TYPE_CODE = '01'

CMD_INFO = 0
CMD_QUERY = 2
CMD_SET = 3