"""Constants for GeoSphere Austria Warnings integration."""

DOMAIN = "geosphere_warnings"

# API
API_BASE_URL = "https://warnungen.zamg.at/wsapp/api/getWarningsForCoords"
API_TIMEOUT = 30
DEFAULT_SCAN_INTERVAL = 30  # minutes

# Config entry keys
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_LOCATION_NAME = "location_name"
CONF_SCAN_INTERVAL = "scan_interval"

# Warning type IDs from GeoSphere API
WARN_TYPE = {
    1: "wind",
    2: "rain",
    3: "snow",
    4: "black_ice",
    5: "thunderstorm",
    6: "heat",
    7: "cold",
}

WARN_TYPE_LABELS = {
    1: "Vihar/Szél",
    2: "Eső",
    3: "Hó",
    4: "Jegesedés",
    5: "Zivatar",
    6: "Hőség",
    7: "Hideg",
}

WARN_TYPE_ICONS = {
    1: "mdi:weather-windy",
    2: "mdi:weather-pouring",
    3: "mdi:weather-snowy-heavy",
    4: "mdi:car-traction-control",
    5: "mdi:weather-lightning",
    6: "mdi:thermometer-high",
    7: "mdi:thermometer-low",
}

# Warning level IDs from GeoSphere API
WARN_LEVEL = {
    1: "yellow",
    2: "orange",
    3: "red",
}

WARN_LEVEL_LABELS = {
    0: "Nincs figyelmeztetés",
    1: "Sárga (Moderate)",
    2: "Narancs (Severe)",
    3: "Piros (Extreme)",
}

WARN_LEVEL_ICONS = {
    0: "mdi:shield-check",
    1: "mdi:shield-alert-outline",
    2: "mdi:shield-alert",
    3: "mdi:shield-off",
}