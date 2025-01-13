"""Platform for switch integration."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, DEVICE_TYPE_SWITCH, CONF_DEVICE_TYPE
from .cozylife_device import CozyLifeDevice

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BetterCozyLife Switch."""
    config = config_entry.data
    
    if config[CONF_DEVICE_TYPE] == DEVICE_TYPE_SWITCH:
        async_add_entities([BetterCozyLifeSwitch(config, config_entry.entry_id)])

class BetterCozyLifeSwitch(SwitchEntity):
    """Representation of a BetterCozyLife Switch."""

    def __init__(self, config, entry_id):
        """Initialize the switch."""
        self._device = CozyLifeDevice(config[CONF_IP_ADDRESS])
        self._name = config.get(CONF_NAME, f"BetterCozyLife Switch {config[CONF_IP_ADDRESS]}")
        self._ip = config[CONF_IP_ADDRESS]
        self._entry_id = entry_id
        self._attr_has_entity_name = True
        self._is_on = False
        self._available = True

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"bettercozylife_switch_{self._ip}"

    @property
    def device_info(self):
        """Return device information about this switch."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._ip)},
            name=self._name,
            manufacturer="CozyLife",
            model="Smart Switch",
            sw_version="1.0",
            via_device=(DOMAIN, self._entry_id),
        )

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