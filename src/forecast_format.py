from __future__ import annotations

from typing import Any, Dict, List


def _convert_temp(value: float | None, from_unit: str | None, to_unit: str) -> float | None:
    if value is None:
        return None
    if not from_unit or from_unit == to_unit:
        return value
    if from_unit == "F" and to_unit == "C":
        return (value - 32) * 5 / 9
    if from_unit == "C" and to_unit == "F":
        return (value * 9 / 5) + 32
    return value


def format_now(period: Dict[str, Any], humidity: float | None, target_unit: str) -> str:
    temp = period.get("temperature")
    from_unit = period.get("temperatureUnit", "F")
    temp = _convert_temp(temp, from_unit, target_unit)
    short = period.get("shortForecast", "")
    base = f"Now: {temp:.0f} {target_unit} - {short}"
    if humidity is None:
        return base
    return f"{base} | Humidity: {humidity:.0f}%"


def _format_detail_lines(details: List[tuple[str, str]], segment_widths: Dict[str, int]) -> str:
    parts = []
    for label, value in details:
        segment = f"{label}: {value}"
        width = segment_widths.get(label, len(segment))
        parts.append(segment.ljust(width))
    return " | ".join(parts)


def format_days(
    summaries: List[Dict[str, Any]],
    days: int,
    show_temp_range: bool,
    show_weather: bool,
    show_wind: bool,
    target_unit: str,
) -> List[str]:
    lines: List[str] = []
    enabled_labels: List[str] = []
    if show_temp_range:
        enabled_labels.append("Temp range")
    if show_weather:
        enabled_labels.append("Conditions")
    if show_wind:
        enabled_labels.append("Wind")

    segment_widths = {label: 0 for label in enabled_labels}
    for s in summaries[:days]:
        if "Temp range" in segment_widths:
            from_unit = s.get("unit")
            low = _convert_temp(s.get("temp_low"), from_unit, target_unit)
            high = _convert_temp(s.get("temp_high"), from_unit, target_unit)
            temp_value = "N/A" if low is None and high is None else f"{low:.0f}-{high:.0f} {target_unit}"
            segment_widths["Temp range"] = max(
                segment_widths["Temp range"], len(f"Temp range: {temp_value}")
            )
        if "Conditions" in segment_widths:
            cond_value = s.get("short_forecast", "")
            segment_widths["Conditions"] = max(
                segment_widths["Conditions"], len(f"Conditions: {cond_value}")
            )
        if "Wind" in segment_widths:
            wind_value = f"{s.get('wind_dir', '')} {s.get('wind_speed', '')}".strip() or "N/A"
            segment_widths["Wind"] = max(
                segment_widths["Wind"], len(f"Wind: {wind_value}")
            )

    for s in summaries[:days]:
        details: List[tuple[str, str]] = []
        from_unit = s.get("unit")
        if show_temp_range:
            low = _convert_temp(s.get("temp_low"), from_unit, target_unit)
            high = _convert_temp(s.get("temp_high"), from_unit, target_unit)
            if low is None and high is None:
                details.append(("Temp range", "N/A"))
            else:
                details.append(("Temp range", f"{low:.0f}-{high:.0f} {target_unit}"))
        if show_weather:
            details.append(("Conditions", s.get("short_forecast", "")))
        if show_wind:
            wind = f"{s.get('wind_dir', '')} {s.get('wind_speed', '')}".strip()
            details.append(("Wind", wind or "N/A"))

        if details:
            lines.append(
                f"{s.get('label', s.get('date', 'Day'))}: "
                + _format_detail_lines(details, segment_widths)
            )
        else:
            lines.append(f"{s.get('label', s.get('date', 'Day'))}")

    return lines
