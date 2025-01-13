"""The BetterCozyLife integration."""
import voluptuous as vol
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS
import homeassistant.helpers.config_validation as cv
from .const import *

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_TYPE): cv.string,
    vol.Optional(CONF_NAME): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Set up the BetterCozyLife component."""
    if DOMAIN not in config:
        return True

    devices = config[DOMAIN][CONF_DEVICES]
    
    # Setup platforms
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform(
            'switch', DOMAIN, devices, config
        )
    )

    return True