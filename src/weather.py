from __future__ import annotations

import requests
from typing import Any, Dict, List, Tuple

APP_USER_AGENT = "15113-HW3-Explore-API (your_email@example.com)"

HEADERS_NWS = {
    "User-Agent": APP_USER_AGENT,
    "Accept": "application/geo+json",
}


def fetch_forecast_periods(lat: float, lon: float) -> List[Dict[str, Any]]:
    """NWS: /points -> forecast URL -> periods list."""
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    r1 = requests.get(points_url, headers=HEADERS_NWS, timeout=20)
    r1.raise_for_status()
    points = r1.json()

    forecast_url = points["properties"]["forecast"]
    r2 = requests.get(forecast_url, headers=HEADERS_NWS, timeout=20)
    r2.raise_for_status()
    forecast = r2.json()

    return forecast["properties"]["periods"]


def fetch_latest_relative_humidity(lat: float, lon: float) -> float | None:
    """
    NWS: /points -> observationStations -> try multiple stations -> latest observation.
    Returns relative humidity percent (float) or None if unavailable.
    """
    points_url = f"https://api.weather.gov/points/{lat},{lon}"
    r1 = requests.get(points_url, headers=HEADERS_NWS, timeout=20)
    r1.raise_for_status()
    points = r1.json()

    stations_url = points.get("properties", {}).get("observationStations")
    if not stations_url:
        return None

    r2 = requests.get(stations_url, headers=HEADERS_NWS, timeout=20)
    r2.raise_for_status()
    stations = r2.json()

    features = stations.get("features", [])
    if not features:
        return None

    # Try several nearby stations; first one may not report RH
    for feat in features[:10]:
        station_id = feat.get("properties", {}).get("stationIdentifier")
        if not station_id:
            station_ref = feat.get("id", "")
            station_id = station_ref.rsplit("/", 1)[-1] if station_ref else None
        if not station_id:
            continue

        latest_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        r3 = requests.get(latest_url, headers=HEADERS_NWS, timeout=20)
        if r3.status_code != 200:
            continue

        obs = r3.json()
        rh = obs.get("properties", {}).get("relativeHumidity", {}).get("value")
        if rh is not None:
            return float(rh)

    return None



def summarize_now_and_tomorrow(periods: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    "Now" = first period (closest period, not real-time observation).
    Tomorrow high = first isDaytime=True after index 0
    Tomorrow low  = first isDaytime=False after that daytime period
    """
    if not periods:
        raise ValueError("Forecast periods list is empty.")

    now_p = periods[0]
    now_label = now_p.get("name", "Now")
    now_temp = now_p.get("temperature")
    now_unit = now_p.get("temperatureUnit", "F")
    now_short = now_p.get("shortForecast", "")

    # find tomorrow daytime
    day_idx = None
    for i in range(1, len(periods)):
        if periods[i].get("isDaytime") is True:
            day_idx = i
            break

    if day_idx is None:
        return {
            "now_label": now_label,
            "now_temp": now_temp,
            "now_unit": now_unit,
            "now_short": now_short,
            "tomorrow_label": None,
            "tomorrow_low": None,
            "tomorrow_high": None,
            "unit": now_unit,
        }

    day_p = periods[day_idx]
    tomorrow_label = day_p.get("name", "Tomorrow")
    tomorrow_high = day_p.get("temperature")
    unit = day_p.get("temperatureUnit", now_unit)

    # find following night
    night_p = None
    for j in range(day_idx + 1, len(periods)):
        if periods[j].get("isDaytime") is False:
            night_p = periods[j]
            break

    tomorrow_low = None
    if night_p is not None and night_p.get("temperatureUnit", unit) == unit:
        tomorrow_low = night_p.get("temperature")

    return {
        "now_label": now_label,
        "now_temp": now_temp,
        "now_unit": now_unit,
        "now_short": now_short,
        "tomorrow_label": tomorrow_label,
        "tomorrow_low": tomorrow_low,
        "tomorrow_high": tomorrow_high,
        "unit": unit,
    }


def get_weather_by_latlon(lat: float, lon: float) -> Dict[str, Any]:
    periods = fetch_forecast_periods(lat, lon)
    return summarize_now_and_tomorrow(periods)
