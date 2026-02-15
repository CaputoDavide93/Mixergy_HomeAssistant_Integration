"""Constants for the Mixergy integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "mixergy"
MANUFACTURER: Final = "Mixergy Ltd"

# Config keys
CONF_SERIAL_NUMBER: Final = "serial_number"

# Coordinator update interval (seconds)
UPDATE_INTERVAL: Final = 30

# Heat source options for the select entity
HEAT_SOURCE_OPTIONS: Final = ["electric", "indirect", "heat_pump"]
