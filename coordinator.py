"""DataUpdateCoordinator for GeoSphere Austria Warnings."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GeoSphereApiClient, GeoSphereApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeoSphereWarningsCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Coordinator to fetch and cache GeoSphere warning data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: GeoSphereApiClient,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )
        self._client = client

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch latest warnings from the API."""
        try:
            return await self._client.get_warnings()
        except GeoSphereApiError as err:
            raise UpdateFailed(f"GeoSphere API error: {err}") from err