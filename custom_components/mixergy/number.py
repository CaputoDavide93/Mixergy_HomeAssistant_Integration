"""Number platform for the Mixergy integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import MixergyApiClient, TankData
from .coordinator import MixergyConfigEntry, MixergyCoordinator
from .entity import MixergyEntity


@dataclass(frozen=True, kw_only=True)
class MixergyNumberEntityDescription(NumberEntityDescription):
    """Describe a Mixergy number entity."""

    value_fn: Callable[[TankData], float | None]
    set_value_fn: Callable[
        [MixergyApiClient, float], Coroutine[Any, Any, None]
    ]
    available_fn: Callable[[TankData], bool] = lambda _: True


NUMBER_DESCRIPTIONS: tuple[MixergyNumberEntityDescription, ...] = (
    MixergyNumberEntityDescription(
        key="target_temperature_control",
        translation_key="target_temperature_control",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=45,
        native_max_value=70,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:thermometer",
        value_fn=lambda data: data.settings.target_temperature,
        set_value_fn=lambda client, v: client.set_target_temperature(int(v)),
    ),
    MixergyNumberEntityDescription(
        key="target_charge_control",
        translation_key="target_charge_control",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        mode=NumberMode.SLIDER,
        icon="mdi:water-percent",
        value_fn=lambda data: data.measurement.target_charge,
        set_value_fn=lambda client, v: client.set_target_charge(int(v)),
    ),
    MixergyNumberEntityDescription(
        key="cleansing_temperature_control",
        translation_key="cleansing_temperature_control",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=51,
        native_max_value=55,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:thermometer-water",
        value_fn=lambda data: data.settings.cleansing_temperature,
        set_value_fn=lambda client, v: client.set_cleansing_temperature(
            int(v)
        ),
    ),
    # ── PV Controls ──────────────────────────────────────────────────
    MixergyNumberEntityDescription(
        key="pv_cut_in_threshold",
        translation_key="pv_cut_in_threshold",
        native_min_value=0,
        native_max_value=500,
        native_step=50,
        mode=NumberMode.SLIDER,
        icon="mdi:solar-power-variant",
        value_fn=lambda data: data.settings.pv_cut_in_threshold,
        set_value_fn=lambda client, v: client.set_pv_cut_in_threshold(int(v)),
        available_fn=lambda data: data.info.has_pv_diverter,
    ),
    MixergyNumberEntityDescription(
        key="pv_charge_limit",
        translation_key="pv_charge_limit",
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=0,
        native_max_value=100,
        native_step=10,
        mode=NumberMode.SLIDER,
        icon="mdi:solar-power",
        value_fn=lambda data: data.settings.pv_charge_limit,
        set_value_fn=lambda client, v: client.set_pv_charge_limit(int(v)),
        available_fn=lambda data: data.info.has_pv_diverter,
    ),
    MixergyNumberEntityDescription(
        key="pv_target_current",
        translation_key="pv_target_current",
        native_min_value=-1,
        native_max_value=0,
        native_step=0.1,
        mode=NumberMode.BOX,
        icon="mdi:current-ac",
        value_fn=lambda data: data.settings.pv_target_current,
        set_value_fn=lambda client, v: client.set_pv_target_current(v),
        available_fn=lambda data: data.info.has_pv_diverter,
    ),
    MixergyNumberEntityDescription(
        key="pv_over_temperature",
        translation_key="pv_over_temperature",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=45,
        native_max_value=60,
        native_step=1,
        mode=NumberMode.SLIDER,
        icon="mdi:thermometer-alert",
        value_fn=lambda data: data.settings.pv_over_temperature,
        set_value_fn=lambda client, v: client.set_pv_over_temperature(int(v)),
        available_fn=lambda data: data.info.has_pv_diverter,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MixergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mixergy number entities."""
    coordinator = entry.runtime_data

    async_add_entities(
        MixergyNumber(coordinator, description)
        for description in NUMBER_DESCRIPTIONS
    )


class MixergyNumber(MixergyEntity, NumberEntity):
    """Representation of a Mixergy number control."""

    entity_description: MixergyNumberEntityDescription

    def __init__(
        self,
        coordinator: MixergyCoordinator,
        description: MixergyNumberEntityDescription,
    ) -> None:
        """Initialise the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.info.serial_number}_{description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.entity_description.available_fn(self.coordinator.data)
        )

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.entity_description.set_value_fn(
            self.coordinator.client, value
        )
        await self.coordinator.async_request_refresh()
