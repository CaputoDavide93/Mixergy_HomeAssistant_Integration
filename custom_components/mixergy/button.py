"""Button platform for the Mixergy integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import MixergyConfigEntry, MixergyCoordinator
from .entity import MixergyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MixergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mixergy button entities."""
    coordinator = entry.runtime_data
    async_add_entities([MixergyClearHolidayButton(coordinator)])


class MixergyClearHolidayButton(MixergyEntity, ButtonEntity):
    """Button to clear holiday mode dates."""

    _attr_translation_key = "clear_holiday"
    _attr_icon = "mdi:airplane-off"

    def __init__(self, coordinator: MixergyCoordinator) -> None:
        """Initialise the button entity."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.data.info.serial_number}_clear_holiday"
        )

    async def async_press(self) -> None:
        """Clear the holiday dates."""
        await self.coordinator.client.clear_holiday_dates()
        await self.coordinator.async_request_refresh()
