"""P6 (PREREG.md section 6): does turning thinking on lower list-only mistakes (type C) more than type B?

Usage:
    python3 src/p6.py

Reads the per-list results that src/analyze.py saved for qwen3-8b-think and qwen3-8b-nothink (both labeled
with the thinking-off pair answers of the same Qwen3 8B weights) and writes data/processed/results/p6_thinking.json.

For each list length: the type C share with thinking on minus the type C share with thinking off, and the same
for type B, with 95% ranges from 2,000 redraws of lists within each cell (seed 41, as in analyze.py). Both setups
answered the same 240 lists, so each redraw picks the same lists for both (a paired redraw).
Written by Claude Code, Oct 12, 2026, after the thinking-on run finished.
"""

import json
from collections import defaultdict

import numpy as np

from analyze import BOOT_SEED, N_BOOT, RESULTS, share_of

ON, OFF = "qwen3-8b-think", "qwen3-8b-nothink"


def difference(on_rows, off_rows, kind, rng):
    on_by_id = {r["id"]: r for r in on_rows}
    off_by_id = {r["id"]: r for r in off_rows}
    cells = defaultdict(list)
    for r in off_rows:
        cells[r["band"]].append(r["id"])

    def stat(ids):
        return share_of(kind)([on_by_id[i] for i in ids]) - share_of(kind)([off_by_id[i] for i in ids])

    ids = [i for members in cells.values() for i in members]
    point = stat(ids)
    draws = []
    for _ in range(N_BOOT):
        sample = [members[k] for members in cells.values() for k in rng.integers(0, len(members), len(members))]
        d = stat(sample)
        if not np.isnan(d):
            draws.append(d)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"value": round(point, 4), "ci95": [round(float(lo), 4), round(float(hi), 4)],
            "on": round(share_of(kind)([on_by_id[i] for i in ids]), 4),
            "off": round(share_of(kind)([off_by_id[i] for i in ids]), 4)}


def main():
    on = json.loads((RESULTS / f"{ON}_lists.json").read_text(encoding="utf-8"))
    off = json.loads((RESULTS / f"{OFF}_lists.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(BOOT_SEED)
    out = {"setups": {"thinking_on": ON, "thinking_off": OFF}, "by_length": {}}
    for length in (5, 10, 20):
        on_rows = [r for r in on if r["length"] == length]
        off_rows = [r for r in off if r["length"] == length]
        out["by_length"][length] = {kind: difference(on_rows, off_rows, kind, rng) for kind in ("C", "B")}
    (RESULTS / "p6_thinking.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for length, row in out["by_length"].items():
        print(length, {k: (v["off"], v["on"], v["value"], v["ci95"]) for k, v in row.items()})


if __name__ == "__main__":
    main()
