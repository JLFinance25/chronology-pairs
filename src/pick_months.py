"""Step 1a: pick a random month for each year (PLAN.md decision 2).

Writes data/processed/year_months.csv. Same seed, same months, every time.
"""

import csv
import random

from common import MONTH_SEED, PROCESSED, YEARS


def main():
    rng = random.Random(MONTH_SEED)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / "year_months.csv"
    with out.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "month"])
        for year in YEARS:
            writer.writerow([year, rng.randint(1, 12)])
    print(f"Wrote {out} (seed {MONTH_SEED})")


if __name__ == "__main__":
    main()
