"""Platform for switch integration."""
import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_NAME
import logging
from .cozylife_device import CozyLifeDevice
from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the CozyLife Switch platform."""
    if discovery_info is None:
        return
    
    devices = []
    for device_config in discovery_info:
        if device_config[CONF_DEVICE_TYPE] == DEVICE_TYPE_SWITCH:
            devices.append(CozyLifeSwitch(device_config))
    
    async_add_entities(devices)

class CozyLifeSwitch(SwitchEntity):
    """Representation of a CozyLife Switch."""

    def __init__(self, config):
        """Initialize the switch."""
        self._device = CozyLifeDevice(config[CONF_DEVICE_IP])
        self._name = config.get(CONF_NAME, f"CozyLife Switch {config[CONF_DEVICE_IP]}")
        self._is_on = False
        self._available = True

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._is_on

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        if self._device.send_command(True):
            self._is_on = True

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        if self._device.send_command(False):
            self._is_on = False

    def update(self):
        """Fetch new state data for this switch."""
        state = self._device.query_state()
        if state is not None:
            self._is_on = state.get('1', 0) > 0
            self._available = True
        else:
            self._available = False