"""Platform for sensor integration."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_NAME,
    CONF_IP_ADDRESS,
    UnitOfPower,
)
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, DEVICE_TYPE_SWITCH, CONF_DEVICE_TYPE
from .cozylife_device import CozyLifeDevice
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BetterCozyLife sensors."""
    config = config_entry.data
    
    if config[CONF_DEVICE_TYPE] == DEVICE_TYPE_SWITCH:
        device = CozyLifeDevice(config[CONF_IP_ADDRESS])
        async_add_entities([BetterCozyLifePowerSensor(config, config_entry.entry_id, device)])

class BetterCozyLifePowerSensor(SensorEntity):
    """Representation of a BetterCozyLife Power Sensor."""
    
    _attr_has_entity_name = True

    def __init__(self, config, entry_id, device):
        """Initialize the power sensor."""
        self._device = device
        self._ip = config[CONF_IP_ADDRESS]
        self._entry_id = entry_id
        base_name = config.get(CONF_NAME, f"BetterCozyLife {self._ip}")
        self._attr_name = f"{base_name} Power"
        self._state = None
        self._available = True
        
        # Set up sensor attributes
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        # Set unique ID
        self._attr_unique_id = f"bettercozylife_power_{self._ip}"
        
        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ip)},
            name=base_name,
            manufacturer="CozyLife",
            model="Smart Switch",
            sw_version="1.0",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        state = self._device.query_state()
        if state is not None:
            # Get power value from attribute 28 which we identified as power
            power = state.get('28', 0)
            self._state = float(power)
            self._available = True
        else:
            self._state = None
            self._available = False