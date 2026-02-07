from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


def _parse_date(period: Dict[str, Any]) -> Optional[str]:
    start = period.get("startTime")
    if not start:
        return None
    try:
        dt = datetime.fromisoformat(start)
    except ValueError:
        return None
    return dt.date().isoformat()


def _first_non_empty(periods: Iterable[Dict[str, Any]], key: str) -> Optional[Any]:
    for p in periods:
        value = p.get(key)
        if value is not None and value != "":
            return value
    return None


def _extract_numeric(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("value")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _extract_humidity(periods: Iterable[Dict[str, Any]]) -> Optional[float]:
    return _extract_numeric(_first_non_empty(periods, "relativeHumidity"))


def _extract_uv(periods: Iterable[Dict[str, Any]]) -> Optional[float]:
    return _extract_numeric(_first_non_empty(periods, "uvIndex"))


def _extract_real_feel(periods: Iterable[Dict[str, Any]]) -> Optional[float]:
    for key in ("apparentTemperature", "heatIndex", "windChill"):
        val = _extract_numeric(_first_non_empty(periods, key))
        if val is not None:
            return val
    return None


def build_day_summaries(periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_date: Dict[str, List[Dict[str, Any]]] = {}
    order: List[str] = []

    for p in periods:
        date = _parse_date(p)
        if not date:
            continue
        if date not in by_date:
            by_date[date] = []
            order.append(date)
        by_date[date].append(p)

    summaries: List[Dict[str, Any]] = []
    for date in order:
        items = by_date[date]
        day_period = next((p for p in items if p.get("isDaytime") is True), items[0])
        temps = [p.get("temperature") for p in items if isinstance(p.get("temperature"), (int, float))]
        temp_high = max(temps) if temps else None
        temp_low = min(temps) if temps else None
        unit = day_period.get("temperatureUnit")

        summaries.append(
            {
                "date": date,
                "label": day_period.get("name", date),
                "short_forecast": day_period.get("shortForecast", ""),
                "wind_speed": day_period.get("windSpeed", ""),
                "wind_dir": day_period.get("windDirection", ""),
                "temp_high": temp_high,
                "temp_low": temp_low,
                "unit": unit,
                "humidity": _extract_humidity(items),
                "uv": _extract_uv(items),
                "real_feel": _extract_real_feel(items),
            }
        )

    return summaries


def format_now(period: Dict[str, Any]) -> str:
    temp = period.get("temperature")
    unit = period.get("temperatureUnit", "F")
    short = period.get("shortForecast", "")
    return f"Now: {temp}°{unit} - {short}"


def format_days(
    summaries: List[Dict[str, Any]],
    days: int,
    show_temp_range: bool,
    show_weather: bool,
    show_wind: bool,
    show_humidity: bool,
    show_uv: bool,
    show_air: bool,
    show_real_feel: bool,
) -> List[str]:
    lines: List[str] = []
    for s in summaries[:days]:
        details: List[str] = []
        unit = s.get("unit") or ""
        if show_temp_range:
            low = s.get("temp_low")
            high = s.get("temp_high")
            if low is None and high is None:
                details.append("Temp range: N/A")
            else:
                details.append(f"Temp range: {low}–{high}°{unit}")
        if show_weather:
            details.append(f"Conditions: {s.get('short_forecast', '')}")
        if show_wind:
            wind = f"{s.get('wind_dir', '')} {s.get('wind_speed', '')}".strip()
            details.append(f"Wind: {wind or 'N/A'}")
        if show_humidity:
            humidity = s.get("humidity")
            details.append(f"Humidity: {humidity:.0f}%" if humidity is not None else "Humidity: N/A")
        if show_uv:
            uv = s.get("uv")
            details.append(f"UV Index: {uv:.0f}" if uv is not None else "UV Index: N/A")
        if show_air:
            details.append("Air quality: N/A")
        if show_real_feel:
            rf = s.get("real_feel")
            details.append(f"Real feel: {rf:.0f}°{unit}" if rf is not None else "Real feel: N/A")

        if details:
            lines.append(f"{s.get('label', s.get('date', 'Day'))}: " + " | ".join(details))
        else:
            lines.append(f"{s.get('label', s.get('date', 'Day'))}")

    return lines
