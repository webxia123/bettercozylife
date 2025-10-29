"""Platform for sensor integration using shared coordinator."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONF_NAME,
    CONF_IP_ADDRESS,
    UnitOfPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
)
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, DEVICE_TYPE_SWITCH, CONF_DEVICE_TYPE
from .coordinator import CozyLifeCoordinator
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BetterCozyLife sensors via coordinator."""
    config = config_entry.data

    if config[CONF_DEVICE_TYPE] != DEVICE_TYPE_SWITCH:
        return

    coordinator: CozyLifeCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        BetterCozyLifePowerSensor(coordinator, config),
        BetterCozyLifeCurrentSensor(coordinator, config),
        BetterCozyLifeVoltageSensor(coordinator, config),
    ]
    async_add_entities(entities)


class BaseBetterCozyLifeSensor(CoordinatorEntity[CozyLifeCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: CozyLifeCoordinator, config: dict, name_suffix: str):
        super().__init__(coordinator)
        self._ip = config[CONF_IP_ADDRESS]
        base_name = config.get(CONF_NAME, f"BetterCozyLife {self._ip}")
        self._attr_name = f"{base_name} {name_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._ip)},
            name=base_name,
            manufacturer="CozyLife",
            model="Smart Switch",
            sw_version="1.0",
        )

    @property
    def available(self) -> bool:
        if hasattr(self.coordinator, "coordinator_available"):
            return self.coordinator.coordinator_available
        return super().available


class BetterCozyLifePowerSensor(BaseBetterCozyLifeSensor):
    def __init__(self, coordinator: CozyLifeCoordinator, config: dict):
        super().__init__(coordinator, config, "Power")
        self._attr_unique_id = f"bettercozylife_power_{self._ip}"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("power")


class BetterCozyLifeCurrentSensor(BaseBetterCozyLifeSensor):
    def __init__(self, coordinator: CozyLifeCoordinator, config: dict):
        super().__init__(coordinator, config, "Current")
        self._attr_unique_id = f"bettercozylife_current_{self._ip}"
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("current")


class BetterCozyLifeVoltageSensor(BaseBetterCozyLifeSensor):
    def __init__(self, coordinator: CozyLifeCoordinator, config: dict):
        super().__init__(coordinator, config, "Voltage")
        self._attr_unique_id = f"bettercozylife_voltage_{self._ip}"
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.VOLT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("voltage")
