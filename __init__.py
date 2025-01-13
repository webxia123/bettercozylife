"""The CozyLife Direct Control integration."""
import voluptuous as vol
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from .const import *

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_DEVICE_IP): cv.string,
    vol.Required(CONF_DEVICE_TYPE): cv.string,
    vol.Optional(CONF_NAME): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list, [DEVICE_SCHEMA])
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Set up the CozyLife Direct Control component."""
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