"""Monkey-patch pyhap.characteristic.Characteristic.override_properties.

Upstream pyhap calls valid_value_or_raise inside override_properties' recovery
path, which logs at ERROR before raising. The exception is caught and recovery
is the intended behavior, but the ERROR line still surfaces in HA's log every
time a HomeKit accessory restricts valid_values such that the format default
falls outside (e.g. alarm panels without ARM_HOME, where SecuritySystem*State
defaults to StayArmed=0 but valid_values excludes 0).

Replace override_properties with an equivalent that performs the membership
check directly. See ikalchev/HAP-python#473 for the upstream issue and
pszypowicz/HAP-python#1 for the proposed fix.

The integration registers a config flow so it can be added via the UI without
any configuration.yaml entry. An existing yaml entry is migrated to a config
entry automatically on the next HA start.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from pyhap.characteristic import (
    PROP_VALID_VALUES,
    Characteristic,
    _validate_properties,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


def _override_properties_quiet(
    self: Characteristic,
    properties: dict | None = None,
    valid_values: dict | None = None,
) -> None:
    if not properties and not valid_values:
        raise ValueError("No properties or valid_values specified to override.")

    self._clear_cache()

    if properties:
        _validate_properties(properties)
        self._properties.update(properties)

    if valid_values:
        self._properties[PROP_VALID_VALUES] = valid_values

    if self._always_null:
        self.value = None
        return

    try:
        candidate = self.to_valid_value(self._value)
    except ValueError:
        self.value = self._get_default_value()
        return

    valid_values_dict = self._properties.get(PROP_VALID_VALUES)
    if valid_values_dict and candidate not in valid_values_dict.values():
        self.value = self._get_default_value()
    else:
        self.value = candidate


_ORIGINAL_OVERRIDE_PROPERTIES = Characteristic.override_properties
Characteristic.override_properties = _override_properties_quiet
_LOGGER.debug(
    "Patched pyhap.characteristic.Characteristic.override_properties "
    "(was %s)",
    _ORIGINAL_OVERRIDE_PROPERTIES.__qualname__,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Migrate a legacy configuration.yaml entry to a config entry."""
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data={},
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Confirm at INFO level that the import-time patch is active."""
    _LOGGER.info(
        "pyhap.characteristic.Characteristic.override_properties patch active"
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry. The monkey-patch remains active until HA restart."""
    return True
