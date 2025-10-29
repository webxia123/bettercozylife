"""Platform for switch integration using a shared coordinator."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS
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
    """Set up the BetterCozyLife Switch via coordinator."""
    config = config_entry.data

    if config[CONF_DEVICE_TYPE] != DEVICE_TYPE_SWITCH:
        return

    coordinator: CozyLifeCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([BetterCozyLifeSwitch(coordinator, config)])


class BetterCozyLifeSwitch(CoordinatorEntity[CozyLifeCoordinator], SwitchEntity):
    """Representation of a BetterCozyLife Switch using coordinator."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: CozyLifeCoordinator, config: dict):
        super().__init__(coordinator)
        self._name = config.get(CONF_NAME, f"BetterCozyLife Switch {config[CONF_IP_ADDRESS]}")
        self._ip = config[CONF_IP_ADDRESS]

    @property
    def unique_id(self):
        return f"bettercozylife_switch_{self._ip}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._ip)},
            name=self._name,
            manufacturer="CozyLife",
            model="Smart Switch",
            sw_version="2.1",
        )

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        data = self.coordinator.data or {}
        return bool(data.get("switch", False))

    @property
    def available(self):
        # Use coordinator's threshold-aware availability
        if hasattr(self.coordinator, "coordinator_available"):
            return self.coordinator.coordinator_available
        return super().available

    async def async_turn_on(self, **kwargs):
        try:
            ok = await self.hass.async_add_executor_job(self.coordinator.device.send_command, True)
            if ok:
                _LOGGER.info("Successfully turned on switch: %s", self._name)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.warning("Failed to turn on switch: %s", self._name)
        except Exception as e:
            _LOGGER.error("Error turning on switch %s: %s", self._name, e)

    async def async_turn_off(self, **kwargs):
        try:
            ok = await self.hass.async_add_executor_job(self.coordinator.device.send_command, False)
            if ok:
                _LOGGER.info("Successfully turned off switch: %s", self._name)
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.warning("Failed to turn off switch: %s", self._name)
        except Exception as e:
            _LOGGER.error("Error turning off switch %s: %s", self._name, e)
