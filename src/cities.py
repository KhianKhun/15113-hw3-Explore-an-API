"""
cities.py

City database for the GUI app.
Format:
  CITY_DB[name] = (lat, lon)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, List


DATA_PATH = Path(__file__).with_name("cities_filtered.tsv")


def _load_city_db(path: Path) -> Dict[str, Tuple[float, float]]:
    if not path.exists():
        return {}

    import csv

    def _clean_row(row: Dict[str, str]) -> Dict[str, str]:
        cleaned: Dict[str, str] = {}
        for key, value in row.items():
            clean_key = key.strip() if isinstance(key, str) else key
            clean_value = value.strip() if isinstance(value, str) else value
            cleaned[clean_key] = clean_value
        return cleaned

    city_db: Dict[str, Tuple[float, float]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            row = _clean_row(row)
            name = (row.get("NAME") or "").strip()
            state = (row.get("USPS") or "").strip()
            lat = (row.get("INTPTLAT") or "").strip()
            lon = (row.get("INTPTLONG") or "").strip()
            if not (name and state and lat and lon):
                continue
            try:
                city_db[f"{name}, {state}"] = (float(lat), float(lon))
            except ValueError:
                continue
    return city_db


# Main city lookup table
CITY_DB: Dict[str, Tuple[float, float]] = _load_city_db(DATA_PATH)

# Sorted list for UI dropdown / autocomplete
ALL_CITIES: List[str] = sorted(CITY_DB.keys())
