"""Base entity for the Mixergy integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import MixergyCoordinator


class MixergyEntity(CoordinatorEntity[MixergyCoordinator]):
    """Base class for all Mixergy entities.

    Uses CoordinatorEntity properly — should_poll defaults to False,
    and state updates are driven entirely by the coordinator.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: MixergyCoordinator) -> None:
        """Initialise the entity."""
        super().__init__(coordinator)

        serial = coordinator.data.info.serial_number

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=MANUFACTURER,
            name=f"Mixergy Tank ({serial})",
            model=coordinator.data.info.model_code,
            sw_version=coordinator.data.info.firmware_version,
            suggested_area="utility_room",
        )
