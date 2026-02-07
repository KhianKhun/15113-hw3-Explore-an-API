from __future__ import annotations

import math
from typing import Any, Dict, List

SPACE_FACTOR = 1

def _measure(text: str, font: Any | None) -> int:
    if font is None:
        return len(text)
    return int(font.measure(text))


def _pad_to_width(text: str, target_width: int, font: Any | None, space_width: int) -> str:
    current = _measure(text, font)
    pad_px = max(target_width - current, 0)
    if space_width <= 0:
        pad_spaces = 0
    else:
        pad_spaces = math.ceil(pad_px / space_width)
    return text + (" " * (pad_spaces * SPACE_FACTOR))

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


def _format_detail_lines(
    details: List[tuple[str, str]],
    column_widths: List[int],
    font: Any | None,
    space_width: int,
) -> str:
    parts = []
    for idx, (label, value) in enumerate(details):
        segment = f"{label}: {value}"
        seg_width = _measure(segment, font)
        width = column_widths[idx] if idx < len(column_widths) else seg_width
        pad_px = max(width - seg_width, 0)
        if space_width <= 0:
            pad_spaces = 0
        else:
            pad_spaces = math.ceil(pad_px / space_width)
        parts.append(segment + (" " * (pad_spaces * SPACE_FACTOR)))
    return " | ".join(parts)


def format_days(
    summaries: List[Dict[str, Any]],
    days: int,
    show_temp_range: bool,
    show_weather: bool,
    show_wind: bool,
    target_unit: str,
    font: Any | None = None,
) -> List[str]:
    lines: List[str] = []
    enabled_labels: List[str] = []
    if show_temp_range:
        enabled_labels.append("Temp range")
    if show_weather:
        enabled_labels.append("Conditions")
    if show_wind:
        enabled_labels.append("Wind")

    space_width = _measure(" ", font)
    labels = [s.get("label", s.get("date", "Day")) for s in summaries[:days]]
    max_label_width = max((_measure(label, font) for label in labels), default=0)
    length_matrix: List[List[int]] = []
    for s in summaries[:days]:
        row_lengths: List[int] = []
        if show_temp_range:
            from_unit = s.get("unit")
            low = _convert_temp(s.get("temp_low"), from_unit, target_unit)
            high = _convert_temp(s.get("temp_high"), from_unit, target_unit)
            temp_value = "N/A" if low is None and high is None else f"{low:.0f}-{high:.0f} {target_unit}"
            row_lengths.append(_measure(f"Temp range: {temp_value}", font))
        if show_weather:
            cond_value = s.get("short_forecast", "")
            row_lengths.append(_measure(f"Conditions: {cond_value}", font))
        if show_wind:
            wind_value = f"{s.get('wind_dir', '')} {s.get('wind_speed', '')}".strip() or "N/A"
            row_lengths.append(_measure(f"Wind: {wind_value}", font))
        length_matrix.append(row_lengths)

    column_widths: List[int] = []
    if length_matrix:
        col_count = max(len(row) for row in length_matrix)
        for col in range(col_count):
            max_len = max((row[col] for row in length_matrix if col < len(row)), default=0)
            column_widths.append(max_len + space_width)

    for idx, s in enumerate(summaries[:days]):
        label = labels[idx] if idx < len(labels) else s.get("label", s.get("date", "Day"))
        padded_label = _pad_to_width(label, max_label_width, font, space_width)
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
                f"{padded_label}: "
                + _format_detail_lines(details, column_widths, font, space_width)
            )
        else:
            lines.append(f"{s.get('label', s.get('date', 'Day'))}")

    return lines
