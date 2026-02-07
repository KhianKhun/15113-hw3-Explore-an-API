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
