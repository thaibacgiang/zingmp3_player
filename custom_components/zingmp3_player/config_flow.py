"""Config flow for Zing MP3 Player integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.entity import Entity

from .const import (
    CONF_DROPDOWNS,
    CONF_EXTRA_SENSOR,
    CONF_SPEAKERS,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("name", default=DEFAULT_NAME): str,
        vol.Optional(CONF_SPEAKERS, default=[]): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain="media_player",
                multiple=True,
            ),
        ),
        vol.Optional(CONF_EXTRA_SENSOR, default=False): bool,
        vol.Optional(CONF_DROPDOWNS, default=[]): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=["speakers", "playmode", "repeatmode"],
                multiple=True,
                mode=selector.SelectMode.DROPDOWN,
            ),
        ),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zing MP3 Player."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate name
            if not user_input["name"]:
                errors["name"] = "invalid_name"
            else:
                # Check if already configured
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input["name"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle confirmation step (if needed)."""
        return self.async_abort(reason="single_instance_allowed")
