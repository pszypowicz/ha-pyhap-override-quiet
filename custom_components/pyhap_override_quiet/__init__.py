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
"""
from __future__ import annotations

import logging

from pyhap.characteristic import (
    PROP_VALID_VALUES,
    Characteristic,
    _validate_properties,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "pyhap_override_quiet"


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


_ORIGINAL = Characteristic.override_properties
Characteristic.override_properties = _override_properties_quiet
_LOGGER.warning(
    "Patched pyhap.characteristic.Characteristic.override_properties "
    "(was %s)",
    _ORIGINAL.__qualname__,
)


async def async_setup(hass, config) -> bool:
    return True
