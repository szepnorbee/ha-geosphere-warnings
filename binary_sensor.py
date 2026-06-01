"""Binary sensor platform for GeoSphere Austria Warnings."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    WARN_TYPE,
    WARN_TYPE_ICONS,
    WARN_TYPE_LABELS,
    WARN_LEVEL_LABELS,
    CONF_LOCATION_NAME,
    CONF_LATITUDE,
    CONF_LONGITUDE,
)
from .coordinator import GeoSphereWarningsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: GeoSphereWarningsCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = [
        # Overall "any warning active" sensor
        GeoSphereAnyWarningSensor(coordinator, entry),
    ]
    # One binary sensor per warning type
    for typid, key in WARN_TYPE.items():
        entities.append(
            GeoSphereTypeWarningSensor(coordinator, entry, typid, key)
        )

    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    name = entry.data.get(CONF_LOCATION_NAME, "GeoSphere Warnings")
    lat = entry.data[CONF_LATITUDE]
    lon = entry.data[CONF_LONGITUDE]
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"GeoSphere Warnings – {name}",
        manufacturer="GeoSphere Austria",
        model="WarnAPI v1",
        configuration_url=f"https://warnungen.zamg.at/wsapp/api/getWarningsForCoords?lat={lat}&lon={lon}&lang=de",
    )


class GeoSphereBaseBinarySensor(
    CoordinatorEntity[GeoSphereWarningsCoordinator], BinarySensorEntity
):
    """Base class for GeoSphere binary sensors."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GeoSphereWarningsCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = _device_info(entry)

    @property
    def _warnings(self) -> list[dict[str, Any]]:
        return self.coordinator.data or []


class GeoSphereAnyWarningSensor(GeoSphereBaseBinarySensor):
    """Binary sensor: True if ANY warning is active."""

    _attr_name = "Aktív időjárási figyelmeztetés"
    _attr_icon = "mdi:weather-lightning-rainy"

    def __init__(
        self, coordinator: GeoSphereWarningsCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry, "any_warning")

    @property
    def is_on(self) -> bool:
        return len(self._warnings) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        warnings = self._warnings
        if not warnings:
            return {"active_count": 0, "max_level": 0}
        max_level = max(w.get("warnstufeid", 0) for w in warnings)
        return {
            "active_count": len(warnings),
            "max_level": max_level,
            "max_level_label": WARN_LEVEL_LABELS.get(max_level, "?"),
        }


class GeoSphereTypeWarningSensor(GeoSphereBaseBinarySensor):
    """Binary sensor: True if a specific warning type is active."""

    def __init__(
        self,
        coordinator: GeoSphereWarningsCoordinator,
        entry: ConfigEntry,
        typid: int,
        key: str,
    ) -> None:
        super().__init__(coordinator, entry, f"warning_{key}")
        self._typid = typid
        self._attr_name = f"Figyelmeztetés: {WARN_TYPE_LABELS.get(typid, key)}"
        self._attr_icon = WARN_TYPE_ICONS.get(typid, "mdi:alert")

    @property
    def _active(self) -> dict[str, Any] | None:
        """Return the active warning for this type, or None."""
        for w in self._warnings:
            if w.get("warntypid") == self._typid:
                return w
        return None

    @property
    def is_on(self) -> bool:
        return self._active is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        w = self._active
        if w is None:
            return {"active": False}
        level = w.get("warnstufeid", 0)
        return {
            "active": True,
            "level": level,
            "level_label": WARN_LEVEL_LABELS.get(level, "?"),
            "begin": w.get("begin"),
            "end": w.get("end"),
            "warnid": w.get("warnid"),
        }