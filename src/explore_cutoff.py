"""Exploratory (not in PREREG.md): does the Q2 verdict change if cut-off list replies count as unreadable?

PREREG.md section 3 says "a reply cut off at the limit counts as unreadable"; section 5 says a list that
keeps writing past N "doesn't count against it". src/analyze.py follows section 5, so a list that wrote
all N entries and then hit the 400-token limit is scored as valid. This script re-scores those lists as
invalid and reruns the same summary and decision rules, for comparison only.

Usage: python3 src/explore_cutoff.py [setup ...]   (reads data/processed/results/<setup>_lists.json)
"""

import json
import sys

import analyze as A


def as_unreadable(row):
    row = dict(row)
    if row["cut_off"] and row["valid"]:
        row["valid"], row["exact"] = False, False
        for key in ("wrong", "tau", "predicted_wrong", "penalty"):
            row.pop(key, None)
    return row


def main():
    for setup in sys.argv[1:] or A.SETUPS:
        path = A.RESULTS / f"{setup}_lists.json"
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        summary = A.list_summary([as_unreadable(r) for r in rows])
        print(f"{setup}: {sum(r['cut_off'] and r['valid'] for r in rows)} valid lists were cut off; "
              f"verdict if they count as unreadable: {A.decision(summary)}")
        for length, d in summary["by_length"].items():
            print(f"  length {length}: valid {d['valid_share']}, type C {d['type_share']['C']['value']} "
                  f"{d['type_share']['C']['ci95']}, penalty {d['penalty_mean']['value']} {d['penalty_mean']['ci95']}")


if __name__ == "__main__":
    main()
