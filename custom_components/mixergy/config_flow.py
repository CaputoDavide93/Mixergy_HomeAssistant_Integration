"""Config flow for the Mixergy integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    MixergyApiClient,
    MixergyAuthError,
    MixergyConnectionError,
    MixergyTankNotFoundError,
)
from .const import CONF_SERIAL_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_SERIAL_NUMBER): str,
    }
)

STEP_REAUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class MixergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mixergy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial = user_input[CONF_SERIAL_NUMBER].upper().strip()

            # Prevent duplicate entries for the same tank
            await self.async_set_unique_id(serial)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            client = MixergyApiClient(
                session=session,
                username=user_input[CONF_USERNAME].strip(),
                password=user_input[CONF_PASSWORD],
                serial_number=serial,
            )

            try:
                await client.test_credentials()
            except MixergyAuthError:
                errors["base"] = "invalid_auth"
            except MixergyConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during authentication")
                errors["base"] = "unknown"
            else:
                try:
                    await client.test_connection()
                except MixergyTankNotFoundError:
                    errors[CONF_SERIAL_NUMBER] = "tank_not_found"
                except MixergyConnectionError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected error during tank lookup")
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=f"Mixergy Tank ({serial})",
                        data={
                            CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_SERIAL_NUMBER: serial,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-authentication when the token/credentials become invalid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle re-auth credential input."""
        errors: dict[str, str] = {}

        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = MixergyApiClient(
                session=session,
                username=user_input[CONF_USERNAME].strip(),
                password=user_input[CONF_PASSWORD],
                serial_number=reauth_entry.data[CONF_SERIAL_NUMBER],
            )

            try:
                await client.test_credentials()
            except MixergyAuthError:
                errors["base"] = "invalid_auth"
            except MixergyConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during re-authentication")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={
                        CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=STEP_REAUTH_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                CONF_SERIAL_NUMBER: reauth_entry.data[CONF_SERIAL_NUMBER],
            },
        )
