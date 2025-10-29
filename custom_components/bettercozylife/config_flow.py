"""Config flow for BetterCozyLife integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS
import homeassistant.helpers.config_validation as cv
from typing import Any
import socket
import logging
from .const import DOMAIN, CONF_DEVICE_TYPE, DEVICE_TYPE_SWITCH, CONF_FAILURE_THRESHOLD, DEFAULT_FAILURE_THRESHOLD
from .cozylife_device import CozyLifeDevice

_LOGGER = logging.getLogger(__name__)

class BetterCozyLifeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BetterCozyLife."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test connection to device
                device = CozyLifeDevice(user_input[CONF_IP_ADDRESS])
                if await self.hass.async_add_executor_job(device.test_connection):
                    # Create unique ID from IP address
                    await self.async_set_unique_id(user_input[CONF_IP_ADDRESS])
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=user_input[CONF_NAME],
                        data=user_input
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.error(f"Error connecting to device: {e}")
                errors["base"] = "cannot_connect"

        # Show configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Required(CONF_DEVICE_TYPE, default=DEVICE_TYPE_SWITCH): vol.In([
                    DEVICE_TYPE_SWITCH
                
                ]),
                vol.Optional(CONF_NAME): str,
            }),
            errors=errors,
        )

    async def async_step_import(self, import_config):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_config)


class BetterCozyLifeOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options to display and modify IP address/name."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            new_ip = user_input.get(CONF_IP_ADDRESS, self.config_entry.data.get(CONF_IP_ADDRESS))
            new_name = user_input.get(CONF_NAME, self.config_entry.title)
            failure_threshold = user_input.get(CONF_FAILURE_THRESHOLD, self.config_entry.options.get(CONF_FAILURE_THRESHOLD, DEFAULT_FAILURE_THRESHOLD))

            # Validate connectivity to new IP
            try:
                device = CozyLifeDevice(new_ip)
                ok = await self.hass.async_add_executor_job(device.test_connection)
                if not ok:
                    errors["base"] = "cannot_connect"
                else:
                    # Update entry data/options
                    new_data = dict(self.config_entry.data)
                    new_data[CONF_IP_ADDRESS] = new_ip
                    if new_name:
                        new_data[CONF_NAME] = new_name
                    else:
                        new_data.pop(CONF_NAME, None)
                    new_options = dict(self.config_entry.options)
                    new_options[CONF_FAILURE_THRESHOLD] = int(failure_threshold)

                    await self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        title=new_name if new_name else self.config_entry.title,
                        data=new_data,
                        options=new_options,
                    )

                    # Reload entry to apply changes (restart coordinator)
                    await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                    return self.async_create_entry(title="", data={})
            except Exception as e:
                _LOGGER.error("Error validating new IP %s: %s", new_ip, e)
                errors["base"] = "cannot_connect"

        # Show form with current values
        current = self.config_entry.data
        current_options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_IP_ADDRESS, default=current.get(CONF_IP_ADDRESS)): str,
                    vol.Optional(CONF_NAME, default=self.config_entry.title): str,
                    vol.Required(
                        CONF_FAILURE_THRESHOLD,
                        default=current_options.get(CONF_FAILURE_THRESHOLD, DEFAULT_FAILURE_THRESHOLD),
                    ): cv.positive_int,
                }
            ),
            errors=errors,
        )


async def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    return BetterCozyLifeOptionsFlowHandler(config_entry)
