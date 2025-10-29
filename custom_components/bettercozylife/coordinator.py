"""Update coordinator for BetterCozyLife devices."""
from __future__ import annotations

from datetime import timedelta
import asyncio
import async_timeout
import logging
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_IP_ADDRESS,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .cozylife_device import CozyLifeDevice
from .const import CONF_FAILURE_THRESHOLD, DEFAULT_FAILURE_THRESHOLD

_LOGGER = logging.getLogger(__name__)


class CozyLifeCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Coordinator to manage CozyLife device state and availability."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.ip = entry.data[CONF_IP_ADDRESS]
        self.device = CozyLifeDevice(self.ip)
        self.consecutive_failures = 0
        # Read from options, fallback to default
        self.failure_threshold = entry.options.get(CONF_FAILURE_THRESHOLD, DEFAULT_FAILURE_THRESHOLD)

        super().__init__(
            hass,
            _LOGGER,
            name=f"BetterCozyLife {self.ip}",
            update_interval=timedelta(seconds=10),  # Align to 10s
        )

    @property
    def coordinator_available(self) -> bool:
        """Availability with failure threshold considered."""
        return self.consecutive_failures < self.failure_threshold

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from device."""
        try:
            async with async_timeout.timeout(5):
                state = await self.hass.async_add_executor_job(self.device.query_state)
        except (asyncio.TimeoutError, Exception) as err:
            _LOGGER.debug("Coordinator update error for %s: %s", self.ip, err)
            self.consecutive_failures += 1
            raise UpdateFailed(f"Update failed: {err}") from err

        if state is None:
            # During backoff, keep last known data and do not count as a failure
            if hasattr(self.device, "is_backing_off") and self.device.is_backing_off():
                _LOGGER.debug("Coordinator skipping update for %s due to connection backoff", self.ip)
                # Keep failure count unchanged during backoff
                if self.data is not None:
                    return self.data
                # If no previous data, treat as failure
                self.consecutive_failures += 1
                raise UpdateFailed("No data and no previous state during backoff")

            # Not backing off: count as a failure
            self.consecutive_failures += 1
            raise UpdateFailed("No data returned from device")

        # Successful update
        self.consecutive_failures = 0

        try:
            result = {
                "switch": state.get("1", 0) > 0,
                "current": float(state.get("27", 0)) / 1000.0,
                "power": float(state.get("28", 0)),
                "voltage": float(state.get("29", 0)),
                "raw": state,
            }
        except Exception as parse_err:
            _LOGGER.debug("Parsing state failed for %s: %s", self.ip, parse_err)
            # Treat this as a failure to be safe
            self.consecutive_failures += 1
            raise UpdateFailed(f"Parse failed: {parse_err}") from parse_err

        return result
