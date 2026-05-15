"""Config flow for the pyhap_override_quiet integration.

The integration takes no user-supplied configuration - its only job is to
monkey-patch pyhap at import time. The flow exists solely so HA records a
config entry, which is what causes HA to import this integration's module on
every startup without requiring an entry in configuration.yaml.
"""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN


class PyhapOverrideQuietConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-instance, zero-input config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user from Settings - Devices & Services.

        Shows a description on first call (user_input=None) and creates the entry
        once the user clicks Submit.
        """
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is None:
            return self.async_show_form(step_id="user")

        return self.async_create_entry(
            title="pyhap override_properties quiet patch", data={}
        )

    async def async_step_import(
        self, import_data: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Migrate a legacy configuration.yaml entry to a config entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="pyhap override_properties quiet patch", data={}
        )
