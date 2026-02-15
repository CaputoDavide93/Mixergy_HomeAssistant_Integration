# 🔥 Mixergy Integration for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz)
[![GitHub Release](https://img.shields.io/github/v/release/CaputoDavide93/Mixergy_HomeAssistant_Integration)](https://github.com/CaputoDavide93/Mixergy_HomeAssistant_Integration/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![HA Version](https://img.shields.io/badge/HA-2024.4%2B-blue)](https://www.home-assistant.io/)

> Custom Home Assistant integration for [Mixergy](https://www.mixergy.io/) smart hot water tanks. Full cloud API support with real-time monitoring, temperature & charge control, PV diverter management, and holiday scheduling.

---

## ✨ Features

### 📊 Sensors (16 entities)
| Sensor | Type | Description |
|--------|------|-------------|
| Hot water temperature | Temperature | Current top-of-tank temperature |
| Coldest water temperature | Temperature | Current bottom-of-tank temperature |
| Target temperature | Temperature | Configured target temperature |
| Cleansing temperature | Temperature | Anti-legionella cleansing temperature |
| Current charge | Percentage | Current hot water charge level |
| Target charge | Percentage | Current target charge level |
| Electric heat power | Power (W) | Real power draw from clamp sensor |
| PV power | Power (kW) | Solar PV power being diverted (PV diverter only) |
| Clamp power | Power (W) | CT clamp power reading (PV diverter only) |
| Active heat source | Enum | Currently active heat source |
| Default heat source | Enum | Configured default heat source |
| Holiday start/end | Timestamp | Holiday mode dates |
| Firmware version | Text | Tank firmware version |
| Model | Text | Tank model code |

### 🔴 Binary Sensors (7 entities)
| Sensor | Description |
|--------|-------------|
| Electric heat active | Electric immersion is heating |
| Indirect heat active | Gas/oil indirect heat is active |
| Heat pump active | Heat pump is heating |
| Heating | Any heat source is actively heating |
| Low hot water | Charge is below 5% |
| No hot water | Charge is below 0.5% |
| Holiday mode | Tank is in holiday mode |

### 🎛️ Controls (13 entities)
| Entity | Type | Description |
|--------|------|-------------|
| Target temperature | Number (45-70°C) | Set the target water temperature |
| Target charge | Number (0-100%) | Set the desired charge level |
| Cleansing temperature | Number (51-55°C) | Set anti-legionella temperature |
| Default heat source | Select | Choose default heat source |
| Grid assistance (DSR) | Switch | Enable/disable demand-side response |
| Frost protection | Switch | Enable/disable frost protection |
| Medical research donation | Switch | Enable/disable distributed computing |
| PV export divert | Switch | Enable/disable PV divert (PV diverter only) |
| PV cut-in threshold | Number (0-500W) | PV diverter cut-in threshold |
| PV charge limit | Number (0-100%) | Maximum charge from PV |
| PV target current | Number (-1 to 0) | PV target current setting |
| PV over-temperature | Number (45-60°C) | Maximum PV heating temperature |
| Clear holiday dates | Button | Clear holiday mode |

### ⚡ Services
| Service | Description |
|---------|-------------|
| `mixergy.set_holiday_dates` | Set holiday start and end dates |

## 📦 Installation

### HACS (Recommended)

1. Open [HACS](https://hacs.xyz/) in Home Assistant
2. Go to **Integrations**
3. Click the 3 dots menu → **Custom repositories**
4. Add `https://github.com/CaputoDavide93/Mixergy_HomeAssistant_Integration` with category **Integration**
5. Search and install **Mixergy**
6. Restart Home Assistant

### Manual Installation

1. Download the [latest release](https://github.com/CaputoDavide93/Mixergy_HomeAssistant_Integration/releases)
2. Copy the `custom_components/mixergy` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## ⚙️ Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Mixergy**
3. Enter your Mixergy account username, password, and tank serial number
4. The integration will validate your credentials and find your tank

## 🔄 Re-authentication

If your credentials change or expire, the integration will automatically prompt you to re-authenticate through the Home Assistant UI.

## 🏗️ Architecture & Design

This integration was built from the ground up following modern Home Assistant development patterns:

- **SSL verification enabled** — all API calls use proper certificate validation
- **Token lifecycle management** — automatic re-authentication on token expiry & 401 retry
- **Modern HA patterns** — `native_value`, `native_unit_of_measurement`, `has_entity_name`, `CoordinatorEntity`
- **Proper platform separation** — binary sensors, switches, numbers, selects, and buttons on their own platforms
- **Real power readings** — uses CT clamp sensor data instead of hardcoded values
- **Reauth flow** — handles credential changes gracefully with HA's built-in reauth UI
- **Diagnostics support** — downloadable diagnostics with automatic credential redaction
- **Entity descriptions** — clean, declarative entity definitions with `EntityDescription` pattern
- **Correct coordinator usage** — single `DataUpdateCoordinator`, no double-polling
- **Standalone API client** — fully separated from HA for testability and potential reuse
- **Unique ID deduplication** — prevents configuring the same tank twice

## 🔐 Security

- All API communication uses **TLS with certificate verification** (no `verify_ssl=False`)
- Credentials stored in HA's config entry (supports HA's built-in secrets management)
- Bearer tokens are automatically refreshed before expiry
- Diagnostics output **redacts** all credentials

## 📖 Supported Devices

| Device | Support |
|--------|---------|
| Mixergy hot water tanks (all models) | ✅ Full |
| Tanks with PV diverter | ✅ Full (additional PV sensors & controls) |
| Heat pump configurations | ✅ Full |
| Indirect (gas/oil) heating | ✅ Full |
| Electric immersion | ✅ Full |

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/CaputoDavide93/Mixergy_HomeAssistant_Integration).

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ for the Home Assistant community
</p>
