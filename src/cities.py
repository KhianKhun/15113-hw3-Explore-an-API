"""
cities.py

A small city database for the GUI app.
Format:
  CITY_DB[name] = (lat, lon)
"""

from __future__ import annotations

from typing import Dict, Tuple, List


# Main city lookup table
CITY_DB: Dict[str, Tuple[float, float]] = {
    "Pittsburgh, PA": (40.4406, -79.9959),
    "Philadelphia, PA": (39.9526, -75.1652),
    "New York, NY": (40.7128, -74.0060),
    "Boston, MA": (42.3601, -71.0589),
    "Washington, DC": (38.9072, -77.0369),
    "Chicago, IL": (41.8781, -87.6298),
    "Los Angeles, CA": (34.0522, -118.2437),
    "San Francisco, CA": (37.7749, -122.4194),
    "San Diego, CA": (32.7157, -117.1611),
    "Seattle, WA": (47.6062, -122.3321),
    "Portland, OR": (45.5152, -122.6784),
    "Austin, TX": (30.2672, -97.7431),
    "Dallas, TX": (32.7767, -96.7970),
    "Houston, TX": (29.7604, -95.3698),
    "Miami, FL": (25.7617, -80.1918),
    "Atlanta, GA": (33.7490, -84.3880),
    "Denver, CO": (39.7392, -104.9903),
    "Phoenix, AZ": (33.4484, -112.0740),
    "Las Vegas, NV": (36.1699, -115.1398),
}

# Sorted list for UI dropdown / autocomplete
ALL_CITIES: List[str] = sorted(CITY_DB.keys())
