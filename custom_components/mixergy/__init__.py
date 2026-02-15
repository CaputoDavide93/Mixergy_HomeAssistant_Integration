"""The Mixergy integration."""

from __future__ import annotations

import logging
from datetime import datetime

import voluptuous as vol

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import MixergyApiClient
from .const import CONF_SERIAL_NUMBER, DOMAIN
from .coordinator import MixergyConfigEntry, MixergyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

# Service constants
SERVICE_SET_HOLIDAY = "set_holiday_dates"
ATTR_START_DATE = "start_date"
ATTR_END_DATE = "end_date"


async def async_setup_entry(hass: HomeAssistant, entry: MixergyConfigEntry) -> bool:
    """Set up Mixergy from a config entry."""
    session = async_get_clientsession(hass)

    client = MixergyApiClient(
        session=session,
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        serial_number=entry.data[CONF_SERIAL_NUMBER],
    )

    coordinator = MixergyCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services (only once for the domain)
    _register_services(hass)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: MixergyConfigEntry
) -> bool:
    """Unload a Mixergy config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove services when the last entry is unloaded
    loaded_entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if unload_ok and not loaded_entries:
        hass.services.async_remove(DOMAIN, SERVICE_SET_HOLIDAY)

    return unload_ok


def _register_services(hass: HomeAssistant) -> None:
    """Register Mixergy services."""

    async def handle_set_holiday(call: ServiceCall) -> None:
        """Handle the set_holiday_dates service call."""
        start_date: datetime = call.data[ATTR_START_DATE]
        end_date: datetime = call.data[ATTR_END_DATE]

        # Apply to all configured tanks
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.runtime_data and isinstance(
                entry.runtime_data, MixergyCoordinator
            ):
                coordinator: MixergyCoordinator = entry.runtime_data
                try:
                    await coordinator.client.set_holiday_dates(
                        start_date, end_date
                    )
                    await coordinator.async_request_refresh()
                except Exception:
                    _LOGGER.exception(
                        "Failed to set holiday dates for tank %s",
                        entry.data.get(CONF_SERIAL_NUMBER),
                    )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_HOLIDAY):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_HOLIDAY,
            handle_set_holiday,
            schema=vol.Schema(
                {
                    vol.Required(ATTR_START_DATE): cv.datetime,
                    vol.Required(ATTR_END_DATE): cv.datetime,
                }
            ),
        )
