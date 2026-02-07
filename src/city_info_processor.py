from __future__ import annotations

import csv
from pathlib import Path

INPUT_PATH = Path(__file__).with_name("2023_Gaz_place_national.txt")
OUTPUT_PATH = Path(__file__).with_name("cities_filtered.tsv")

LSAD_KEEP = {"25"}
FUNCSTAT_KEEP = {"A"}
MIN_ALAND = 10_000_000


def filter_cities(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8", newline="") as f_in:
        reader = csv.DictReader(f_in, delimiter="\t")
        fieldnames = reader.fieldnames or []

        with output_path.open("w", encoding="utf-8", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, delimiter="\t")
            writer.writeheader()

            for row in reader:
                if row.get("LSAD") not in LSAD_KEEP:
                    continue
                if row.get("FUNCSTAT") not in FUNCSTAT_KEEP:
                    continue
                try:
                    aland = int(row.get("ALAND", "0"))
                except ValueError:
                    continue
                if aland < MIN_ALAND:
                    continue
                writer.writerow(row)


def main() -> None:
    filter_cities(INPUT_PATH, OUTPUT_PATH)
    print(f"Wrote: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
