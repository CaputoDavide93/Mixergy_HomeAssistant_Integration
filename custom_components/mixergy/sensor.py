"""Sensor platform for the Mixergy integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import TankData
from .coordinator import MixergyConfigEntry, MixergyCoordinator
from .entity import MixergyEntity


@dataclass(frozen=True, kw_only=True)
class MixergySensorEntityDescription(SensorEntityDescription):
    """Describe a Mixergy sensor."""

    value_fn: Callable[[TankData], float | int | str | datetime | None]
    available_fn: Callable[[TankData], bool] = lambda _: True


SENSOR_DESCRIPTIONS: tuple[MixergySensorEntityDescription, ...] = (
    # ── Temperature sensors ──────────────────────────────────────────
    MixergySensorEntityDescription(
        key="hot_water_temperature",
        translation_key="hot_water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.measurement.hot_water_temperature,
    ),
    MixergySensorEntityDescription(
        key="coldest_water_temperature",
        translation_key="coldest_water_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.measurement.coldest_water_temperature,
    ),
    MixergySensorEntityDescription(
        key="target_temperature",
        translation_key="target_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.settings.target_temperature,
    ),
    MixergySensorEntityDescription(
        key="cleansing_temperature",
        translation_key="cleansing_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.settings.cleansing_temperature,
    ),
    # ── Charge sensors ───────────────────────────────────────────────
    MixergySensorEntityDescription(
        key="charge",
        translation_key="charge",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        suggested_display_precision=0,
        value_fn=lambda data: data.measurement.charge,
    ),
    MixergySensorEntityDescription(
        key="target_charge",
        translation_key="target_charge",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
        suggested_display_precision=0,
        value_fn=lambda data: data.measurement.target_charge,
    ),
    # ── Power sensors ────────────────────────────────────────────────
    MixergySensorEntityDescription(
        key="electric_power",
        translation_key="electric_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (
            data.measurement.clamp_power_w
            if data.measurement.electric_heat_source
            else 0
        ),
    ),
    MixergySensorEntityDescription(
        key="pv_power",
        translation_key="pv_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
        value_fn=lambda data: data.measurement.pv_power_kw,
        available_fn=lambda data: data.info.has_pv_diverter,
    ),
    MixergySensorEntityDescription(
        key="clamp_power",
        translation_key="clamp_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.measurement.clamp_power_w,
        available_fn=lambda data: data.info.has_pv_diverter,
    ),
    # ── Heat source sensor ───────────────────────────────────────────
    MixergySensorEntityDescription(
        key="active_heat_source",
        translation_key="active_heat_source",
        device_class=SensorDeviceClass.ENUM,
        options=["electric", "indirect", "heatpump", "none"],
        icon="mdi:fire",
        value_fn=lambda data: data.measurement.active_heat_source.value,
    ),
    MixergySensorEntityDescription(
        key="default_heat_source",
        translation_key="default_heat_source",
        device_class=SensorDeviceClass.ENUM,
        options=["electric", "indirect", "heat_pump"],
        icon="mdi:fire-circle",
        value_fn=lambda data: data.schedule.default_heat_source,
    ),
    # ── Holiday date sensors ─────────────────────────────────────────
    MixergySensorEntityDescription(
        key="holiday_start",
        translation_key="holiday_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:airplane-takeoff",
        value_fn=lambda data: data.schedule.holiday_start,
    ),
    MixergySensorEntityDescription(
        key="holiday_end",
        translation_key="holiday_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:airplane-landing",
        value_fn=lambda data: data.schedule.holiday_end,
    ),
    # ── Info sensors ─────────────────────────────────────────────────
    MixergySensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        icon="mdi:chip",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.info.firmware_version,
    ),
    MixergySensorEntityDescription(
        key="model",
        translation_key="model",
        icon="mdi:water-boiler",
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.info.model_code,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MixergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mixergy sensor entities."""
    coordinator = entry.runtime_data

    async_add_entities(
        MixergySensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class MixergySensor(MixergyEntity, SensorEntity):
    """Representation of a Mixergy sensor."""

    entity_description: MixergySensorEntityDescription

    def __init__(
        self,
        coordinator: MixergyCoordinator,
        description: MixergySensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.data.info.serial_number}_{description.key}"
        )

    @property
    def native_value(self) -> float | int | str | datetime | None:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def available(self) -> bool:
        """Return True if the entity is available."""
        return (
            super().available
            and self.entity_description.available_fn(self.coordinator.data)
        )
