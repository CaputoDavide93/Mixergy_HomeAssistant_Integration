"""DataUpdateCoordinator for the Mixergy integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    MixergyApiClient,
    MixergyAuthError,
    MixergyConnectionError,
    TankData,
)
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

MixergyConfigEntry = ConfigEntry[MixergyCoordinator]


class MixergyCoordinator(DataUpdateCoordinator[TankData]):
    """Coordinator to manage fetching Mixergy tank data."""

    config_entry: MixergyConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: MixergyApiClient,
        config_entry: MixergyConfigEntry,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> TankData:
        """Fetch data from the Mixergy API."""
        try:
            return await self.client.fetch_all()
        except MixergyAuthError as err:
            # Triggers HA reauth flow
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="auth_failed",
            ) from err
        except MixergyConnectionError as err:
            raise UpdateFailed(
                f"Error communicating with Mixergy API: {err}"
            ) from err
