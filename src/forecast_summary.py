from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


def _parse_date(period: Dict[str, Any]) -> Optional[str]:
    start = period.get("startTime")
    if not start:
        return None
    try:
        dt = datetime.fromisoformat(start)
    except ValueError:
        return None
    return dt.date().isoformat()


def _convert_temp(value: Optional[float], from_unit: Optional[str], to_unit: str) -> Optional[float]:
    if value is None:
        return None
    if not from_unit or from_unit == to_unit:
        return value
    if from_unit == "F" and to_unit == "C":
        return (value - 32) * 5 / 9
    if from_unit == "C" and to_unit == "F":
        return (value * 9 / 5) + 32
    return value


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
            }
        )

    return summaries


def format_now(period: Dict[str, Any], humidity: float | None, target_unit: str) -> str:
    temp = period.get("temperature")
    from_unit = period.get("temperatureUnit", "F")
    temp = _convert_temp(temp, from_unit, target_unit)
    short = period.get("shortForecast", "")
    base = f"Now: {temp:.0f} {target_unit} - {short}"
    if humidity is None:
        return base
    return f"{base} | Humidity: {humidity:.0f}%"


def format_days(
    summaries: List[Dict[str, Any]],
    days: int,
    show_temp_range: bool,
    show_weather: bool,
    show_wind: bool,
    target_unit: str,
) -> List[str]:
    lines: List[str] = []
    for s in summaries[:days]:
        details: List[str] = []
        from_unit = s.get("unit")
        if show_temp_range:
            low = _convert_temp(s.get("temp_low"), from_unit, target_unit)
            high = _convert_temp(s.get("temp_high"), from_unit, target_unit)
            if low is None and high is None:
                details.append("Temp range: N/A")
            else:
                details.append(f"Temp range: {low:.0f}-{high:.0f} {target_unit}")
        if show_weather:
            details.append(f"Conditions: {s.get('short_forecast', '')}")
        if show_wind:
            wind = f"{s.get('wind_dir', '')} {s.get('wind_speed', '')}".strip()
            details.append(f"Wind: {wind or 'N/A'}")

        if details:
            lines.append(f"{s.get('label', s.get('date', 'Day'))}: " + " | ".join(details))
        else:
            lines.append(f"{s.get('label', s.get('date', 'Day'))}")

    return lines
