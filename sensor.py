"""Sensor platform for GeoSphere Austria Warnings."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    DOMAIN,
    WARN_LEVEL_ICONS,
    WARN_LEVEL_LABELS,
    WARN_TYPE,
    WARN_TYPE_ICONS,
    WARN_TYPE_LABELS,
)
from .coordinator import GeoSphereWarningsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: GeoSphereWarningsCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        GeoSphereWarningCountSensor(coordinator, entry),
        GeoSphereMaxLevelSensor(coordinator, entry),
        GeoSphereWarningDetailsSensor(coordinator, entry),
    ]

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


class GeoSphereBaseSensor(CoordinatorEntity[GeoSphereWarningsCoordinator], SensorEntity):
    """Base class for GeoSphere sensors."""

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
        self._attr_has_entity_name = True

    @property
    def _warnings(self) -> list[dict[str, Any]]:
        return self.coordinator.data or []


class GeoSphereWarningCountSensor(GeoSphereBaseSensor):
    """Sensor: number of active warnings."""

    _attr_name = "Aktív figyelmeztetések száma"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "db"

    def __init__(self, coordinator: GeoSphereWarningsCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "count")

    @property
    def native_value(self) -> int:
        return len(self._warnings)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {"warnings": self._warnings}


class GeoSphereMaxLevelSensor(GeoSphereBaseSensor):
    """Sensor: highest active warning level (0–3)."""

    _attr_name = "Legmagasabb figyelmeztetési szint"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: GeoSphereWarningsCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "max_level")

    @property
    def native_value(self) -> int:
        if not self._warnings:
            return 0
        return max(w.get("warnstufeid", 0) for w in self._warnings)

    @property
    def icon(self) -> str:
        return WARN_LEVEL_ICONS.get(self.native_value, "mdi:shield-alert")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        level = self.native_value
        return {
            "level_label": WARN_LEVEL_LABELS.get(level, "Ismeretlen"),
            "level_color": {0: "none", 1: "yellow", 2: "orange", 3: "red"}.get(level, "none"),
        }


class GeoSphereWarningDetailsSensor(GeoSphereBaseSensor):
    """Sensor: human-readable summary of all active warnings."""

    _attr_name = "Figyelmeztetések összefoglalója"
    _attr_icon = "mdi:weather-lightning-rainy"

    def __init__(self, coordinator: GeoSphereWarningsCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "details")

    @property
    def native_value(self) -> str:
        if not self._warnings:
            return "Nincs aktív figyelmeztetés"
        level_emoji = {1: "🟡", 2: "🟠", 3: "🔴"}
        parts = []
        for w in self._warnings:
            typid = w.get("warntypid", 0)
            level = w.get("warnstufeid", 0)
            emoji = level_emoji.get(level, "⚠️")
            label = WARN_TYPE_LABELS.get(typid, f"Típus {typid}")
            begin = w.get("begin", "?")
            end = w.get("end", "?")
            parts.append(f"{emoji} {label} ({begin} – {end})")
        # HA state max 255 chars
        result = " | ".join(parts)
        return result[:255]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        for w in self._warnings:
            typid = w.get("warntypid", 0)
            key = WARN_TYPE.get(typid, f"type_{typid}")
            attrs[f"warning_{key}"] = {
                "level": w.get("warnstufeid"),
                "level_label": WARN_LEVEL_LABELS.get(w.get("warnstufeid", 0), "?"),
                "begin": w.get("begin"),
                "end": w.get("end"),
                "warnid": w.get("warnid"),
            }
        return attrs