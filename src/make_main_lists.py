"""Make the 240 main-run lists (PLAN.md decision 10). The same lists are used for every model.

8 cells: lengths 5, 10, 20 crossed with the gap between neighboring events (in true order):
tight 1 to 2 years, medium 3 to 5, wide 6 to 10. Length 20 with wide gaps is left out because it
needs at least 114 of the 119 available years. 30 lists per cell.

For each list: draw the 19 (or 9, or 4) gaps uniformly within the band, then a start year so the
list fits inside 1900 to 2019, then shuffle the order shown to the model and give each event a
random two-letter code. Writes data/processed/main_lists.json.
"""

import csv
import json
import random

from common import FIRST_YEAR, LAST_YEAR, PROCESSED
from prompts import make_codes

LISTS_SEED = 20261013
PER_CELL = 30
BANDS = {"tight": (1, 2), "medium": (3, 5), "wide": (6, 10)}
CELLS = [(5, "tight"), (5, "medium"), (5, "wide"), (10, "tight"), (10, "medium"), (10, "wide"),
         (20, "tight"), (20, "medium")]


def main():
    events = {int(r["year"]): r["event_text"] for r in csv.DictReader((PROCESSED / "events.csv").open(encoding="utf-8"))}
    rng = random.Random(LISTS_SEED)
    lists = []
    for length, band in CELLS:
        lo, hi = BANDS[band]
        for k in range(PER_CELL):
            gaps = [rng.randint(lo, hi) for _ in range(length - 1)]
            span = sum(gaps)
            start = rng.randint(FIRST_YEAR, LAST_YEAR - span)
            years = [start]
            for g in gaps:
                years.append(years[-1] + g)
            shown = years[:]
            rng.shuffle(shown)
            codes = make_codes(rng, length)
            lists.append({
                "id": f"n{length}-{band}-{k:02d}", "length": length, "band": band,
                "years_shown": shown, "codes": codes, "texts": [events[y] for y in shown],
                "true_order_years": years, "middle_year": (years[0] + years[-1]) / 2,
            })
    out = PROCESSED / "main_lists.json"
    out.write_text(json.dumps({"seed": LISTS_SEED, "lists": lists}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {out}: {len(lists)} lists in {len(CELLS)} cells")


if __name__ == "__main__":
    main()
