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

    city_db: Dict[str, Tuple[float, float]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            name = row.get("NAME")
            state = row.get("USPS")
            lat = row.get("INTPTLAT")
            lon = row.get("INTPTLONG")
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
