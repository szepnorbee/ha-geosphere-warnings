"""GeoSphere Austria WarnAPI client."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import async_timeout

from .const import API_BASE_URL, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class GeoSphereApiError(Exception):
    """Exception for GeoSphere API errors."""


class GeoSphereApiClient:
    """Client for GeoSphere Austria WarnAPI."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._latitude = latitude
        self._longitude = longitude

    async def get_warnings(self) -> list[dict[str, Any]]:
        """Fetch current warnings for the configured coordinates.

        Returns:
            List of warning dicts, empty list if no active warnings.

        Raises:
            GeoSphereApiError: on network or parse errors.
        """
        params = {
            "lat": self._latitude,
            "lon": self._longitude,
            "lang": "de",
        }

        try:
            async with async_timeout.timeout(API_TIMEOUT):
                async with self._session.get(
                    API_BASE_URL, params=params
                ) as response:
                    response.raise_for_status()
                    data = await response.json(content_type=None)
        except aiohttp.ClientResponseError as err:
            raise GeoSphereApiError(
                f"HTTP error {err.status} fetching GeoSphere warnings"
            ) from err
        except aiohttp.ClientError as err:
            raise GeoSphereApiError(
                f"Network error fetching GeoSphere warnings: {err}"
            ) from err
        except TimeoutError as err:
            raise GeoSphereApiError("Timeout fetching GeoSphere warnings") from err

        return self._parse_response(data)

    def _parse_response(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """Parse the API response and return normalized warnings list."""
        try:
            raw_warnings = data["properties"]["warnings"]
        except (KeyError, TypeError) as err:
            _LOGGER.warning("Unexpected GeoSphere API response format: %s", err)
            return []

        warnings = []
        for item in raw_warnings:
            try:
                props = item["properties"]
                warnings.append(
                    {
                        "warnid": props.get("warnid"),
                        "warntypid": props.get("warntypid"),
                        "warnstufeid": props.get("warnstufeid"),
                        "begin": props.get("begin"),
                        "end": props.get("end"),
                        # Unix timestamps for easier comparison
                        "start_ts": int(props.get("rawinfo", {}).get("start", 0)),
                        "end_ts": int(props.get("rawinfo", {}).get("end", 0)),
                    }
                )
            except (KeyError, TypeError, ValueError) as err:
                _LOGGER.debug("Skipping malformed warning entry: %s", err)
                continue

        return warnings