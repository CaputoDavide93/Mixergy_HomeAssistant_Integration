"""Diagnostics support for the Mixergy integration."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .coordinator import MixergyConfigEntry, MixergyCoordinator

REDACTED = "**REDACTED**"


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: MixergyConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: MixergyCoordinator = entry.runtime_data

    # Redact sensitive data from config
    config_data = dict(entry.data)
    config_data[CONF_USERNAME] = REDACTED
    config_data[CONF_PASSWORD] = REDACTED

    # Convert tank data to dict, redacting schedule raw data
    tank_data = asdict(coordinator.data)

    # Remove raw schedule payload (may contain account-specific data)
    if "schedule" in tank_data and "raw" in tank_data["schedule"]:
        tank_data["schedule"]["raw"] = REDACTED

    return {
        "config": config_data,
        "tank_data": tank_data,
    }
