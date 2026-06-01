"""Config flow for GeoSphere Austria Warnings."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .api import GeoSphereApiClient, GeoSphereApiError
from .const import (
    CONF_LOCATION_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _build_schema(
    hass: HomeAssistant,
    lat: float | None = None,
    lon: float | None = None,
    name: str = "",
    interval: int = DEFAULT_SCAN_INTERVAL,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_LATITUDE,
                default=lat if lat is not None else hass.config.latitude,
            ): cv.latitude,
            vol.Required(
                CONF_LONGITUDE,
                default=lon if lon is not None else hass.config.longitude,
            ): cv.longitude,
            vol.Required(
                CONF_LOCATION_NAME,
                default=name or hass.config.location_name,
            ): cv.string,
            vol.Optional(CONF_SCAN_INTERVAL, default=interval): vol.All(
                vol.Coerce(int), vol.Range(min=10, max=1440)
            ),
        }
    )


class GeoSphereWarningsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GeoSphere Austria Warnings."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            lat = user_input[CONF_LATITUDE]
            lon = user_input[CONF_LONGITUDE]
            name = user_input[CONF_LOCATION_NAME]

            # Prevent duplicate entries for same coordinates
            await self.async_set_unique_id(f"{lat}_{lon}")
            self._abort_if_unique_id_configured()

            # Validate by doing a live API call
            session = async_get_clientsession(self.hass)
            client = GeoSphereApiClient(session, lat, lon)
            try:
                await client.get_warnings()
            except GeoSphereApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during config flow validation")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_LATITUDE: lat,
                        CONF_LONGITUDE: lon,
                        CONF_LOCATION_NAME: name,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(self.hass),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> GeoSphereWarningsOptionsFlow:
        """Return the options flow handler."""
        return GeoSphereWarningsOptionsFlow(config_entry)


class GeoSphereWarningsOptionsFlow(config_entries.OptionsFlow):
    """Handle options updates (e.g. change scan interval)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                self.hass,
                lat=current[CONF_LATITUDE],
                lon=current[CONF_LONGITUDE],
                name=current[CONF_LOCATION_NAME],
                interval=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ),
        )