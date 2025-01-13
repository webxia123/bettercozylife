"""Platform for switch integration."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_NAME,
    CONF_IP_ADDRESS,
    UnitOfPower,
    ATTR_VOLTAGE,
    STATE_UNAVAILABLE,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from .const import DOMAIN, DEVICE_TYPE_SWITCH, CONF_DEVICE_TYPE
from .cozylife_device import CozyLifeDevice
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BetterCozyLife Switch."""
    config = config_entry.data
    
    if config[CONF_DEVICE_TYPE] == DEVICE_TYPE_SWITCH:
        # Create both switch and power sensor entities
        switch = BetterCozyLifeSwitch(config, config_entry.entry_id)
        power_sensor = BetterCozyLifePowerSensor(config, config_entry.entry_id, switch._device)
        async_add_entities([switch, power_sensor])

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

class BetterCozyLifePowerSensor(SensorEntity):
    """Representation of a BetterCozyLife Power Sensor."""

    def __init__(self, config, entry_id, device):
        """Initialize the power sensor."""
        self._device = device
        self._ip = config[CONF_IP_ADDRESS]
        self._entry_id = entry_id
        self._name = f"{config.get(CONF_NAME, 'BetterCozyLife')} Power"
        self._attr_has_entity_name = True
        self._state = None
        self._available = True
        
        # Set up sensor attributes
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"bettercozylife_power_{self._ip}"

    @property
    def device_info(self):
        """Return device information about this sensor."""
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
        """Return the display name of this sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def available(self):
        """Return True if entity is available."""
        return self._available

    def update(self):
        """Fetch new state data for the sensor."""
        state = self._device.query_state()
        if state is not None:
            # Get power value from attribute 28
            power = state.get('28', 0)
            self._state = float(power)
            self._available = True
        else:
            self._state = None
            self._available = False