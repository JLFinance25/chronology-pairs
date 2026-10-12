"""Step 6: the pre-registered analysis (PREREG.md sections 5 and 6).

Usage:
    python3 src/analyze.py                 # every setup with data
    python3 src/analyze.py qwen3-8b-nothink

Reads data/raw/model_runs/main/<setup>.jsonl and writes data/processed/results/<setup>.json plus
tables. Anything not described in PREREG.md is marked "exploratory".
"""

import itertools
import json
import math
import random
import sys
from collections import defaultdict

import numpy as np

from common import PROCESSED, RAW
from prompts import parse_list, parse_pair, parse_year

RUNS = RAW / "model_runs" / "main"
RESULTS = PROCESSED / "results"
N_BOOT = 2000
N_SHUFFLE = 1000
BOOT_SEED, SHUFFLE_SEED, TIE_SEED = 41, 42, 33

BANDS = [("1", 1, 1), ("2", 2, 2), ("3-5", 3, 5), ("6-10", 6, 10), ("11-25", 11, 25), ("26+", 26, 10_000)]
# Thinking-on lists are compared with the thinking-off pair and year answers of the same weights.
REFERENCE = {"qwen3-8b-think": "qwen3-8b-nothink"}
SETUPS = ["qwen3-8b-nothink", "qwen3-14b-nothink", "qwen3-8b-think", "gpt-oss-20b-low"]


def band_of(gap):
    for name, lo, hi in BANDS:
        if lo <= gap <= hi:
            return name
    raise ValueError(gap)


def load_calls(setup):
    path = RUNS / f"{setup}.jsonl"
    if not path.exists():
        return None
    calls = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    main = {c["key"]: c for c in calls if not c["key"].endswith("|repeat")}
    repeats = {c["key"][: -len("|repeat")]: c for c in calls if c["key"].endswith("|repeat")}
    return main, repeats


# ---------------- pairs ----------------

def pair_table(main):
    """{(earlier_year, later_year): label} plus per-call answers {(shown_A, shown_B): 'A'/'B'/None}."""
    answers = {(c["year_a"], c["year_b"]): parse_pair(c["content"]) for c in main.values() if c["task"] == "pair"}
    labels = {}
    for (a, b), ans in answers.items():
        if a < b and (b, a) in answers:
            first, second = ans, answers[(b, a)]
            if first is None or second is None:
                labels[(a, b)] = "unreadable"
                continue
            right1, right2 = first == "A", second == "B"
            labels[(a, b)] = ("stable-right" if right1 and right2 else
                              "stable-wrong" if not right1 and not right2 else "flip")
    return answers, labels


def year_answers(main):
    return {c["year"]: parse_year(c["content"]) for c in main.values() if c["task"] == "year"}


def pair_summary(labels, answers):
    years = sorted({y for p in labels for y in p})
    index = {y: i for i, y in enumerate(years)}
    pairs = sorted(labels)
    band_names = [b[0] for b in BANDS]
    kinds = ["stable-right", "stable-wrong", "flip", "unreadable"]
    band_idx = np.array([band_names.index(band_of(b - a)) for a, b in pairs])
    kind_idx = np.array([kinds.index(labels[p]) for p in pairs])
    i_idx = np.array([index[a] for a, _ in pairs])
    j_idx = np.array([index[b] for _, b in pairs])

    def shares(weights):
        out = {}
        for k, name in enumerate(band_names):
            in_band = band_idx == k
            readable = in_band & (kind_idx != 3)
            total = weights[readable].sum()
            out[name] = {kinds[t]: (weights[in_band & (kind_idx == t)].sum() / total if total else float("nan"))
                         for t in range(3)}
        return out

    point = shares(np.ones(len(pairs)))
    rng = np.random.default_rng(BOOT_SEED)
    boot = defaultdict(list)
    for _ in range(N_BOOT):
        m = rng.multinomial(len(years), [1 / len(years)] * len(years))
        s = shares((m[i_idx] * m[j_idx]).astype(float))
        for b in band_names:
            for t in kinds[:3]:
                boot[(b, t)].append(s[b][t])
    table = {}
    for b in band_names:
        n_band = int((band_idx == band_names.index(b)).sum())
        n_unreadable = int(((band_idx == band_names.index(b)) & (kind_idx == 3)).sum())
        table[b] = {"pairs": n_band, "unreadable": n_unreadable}
        for t in kinds[:3]:
            lo, hi = np.nanpercentile(boot[(b, t)], [2.5, 97.5])
            table[b][t] = {"share": round(float(point[b][t]), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)]}

    resolution = "not reached"
    for k in range(len(band_names)):
        if all(table[b]["stable-right"]["share"] >= 0.95 and table[b]["flip"]["share"] <= 0.05
               for b in band_names[k:]):
            resolution = band_names[k]
            break

    readable = [a for a in answers.values() if a is not None]
    per_question = defaultdict(lambda: [0, 0])
    for (a, b), ans in answers.items():
        if ans is not None:
            per_question[band_of(abs(b - a))][0] += (ans == "A") == (a < b)
            per_question[band_of(abs(b - a))][1] += 1
    return {
        "by_gap_band": table,
        "date_resolution": resolution,
        "position_bias_share_A": round(readable.count("A") / len(readable), 4) if readable else None,
        "per_question_accuracy": {b: round(r / n, 4) for b, (r, n) in per_question.items() if n},
        "unreadable_replies": sum(a is None for a in answers.values()),
        "pair_calls": len(answers),
    }


def cycle_test(labels):
    """Circular triples among all-stable triples vs shuffles of the wrong labels within gap bands."""
    years = sorted({y for p in labels for y in p})
    pos = {p: k for k, p in enumerate(sorted(labels))}
    stable = np.array([labels[p] in ("stable-right", "stable-wrong") for p in sorted(labels)])
    wrong = np.array([labels[p] == "stable-wrong" for p in sorted(labels)])
    band = np.array([band_of(b - a) for a, b in sorted(labels)])
    xy, yz, xz = [], [], []
    for x, y, z in itertools.combinations(years, 3):
        xy.append(pos[(x, y)])
        yz.append(pos[(y, z)])
        xz.append(pos[(x, z)])
    xy, yz, xz = np.array(xy), np.array(yz), np.array(xz)
    all_stable = stable[xy] & stable[yz] & stable[xz]

    def count(w):
        circular = (~w[xy] & ~w[yz] & w[xz]) | (w[xy] & w[yz] & ~w[xz])
        return int((circular & all_stable).sum())

    observed = count(wrong)
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffled = []
    for _ in range(N_SHUFFLE):
        w = wrong.copy()
        for b in set(band):
            idx = np.where((band == b) & stable)[0]
            w[idx] = rng.permutation(w[idx])
        shuffled.append(count(w))
    shuffled = np.array(shuffled)
    centre = shuffled.mean()
    p = float((np.abs(shuffled - centre) >= abs(observed - centre)).mean())
    return {"all_stable_triples": int(all_stable.sum()), "observed_circular": observed,
            "shuffle_mean": round(float(centre), 2), "shuffle_ci95": [int(np.percentile(shuffled, 2.5)),
                                                                     int(np.percentile(shuffled, 97.5))],
            "p_two_sided": round(p, 4)}


# ---------------- lists ----------------

def neighbor_labels(order_years, labels, model_years):
    """Wrong neighbor pairs in an order, each labeled B/U/C/X plus an A (misdated) flag."""
    out = []
    for u, v in zip(order_years, order_years[1:]):
        if u > v:  # u placed before v, but v happened earlier
            label = labels.get((v, u))
            kind = {"stable-wrong": "B", "flip": "U", "stable-right": "C"}.get(label, "X")
            mu, mv = model_years.get(u), model_years.get(v)
            out.append({"type": kind, "misdated": mu is not None and mv is not None and mu <= mv})
    return out


def copeland_order(years, answers, rng):
    score = {}
    for e in years:
        score[e] = sum((answers.get((e, f)) == "A") + (answers.get((f, e)) == "B") for f in years if f != e)
    shuffled = years[:]
    rng.shuffle(shuffled)  # random tie-break, then a stable sort by score
    return sorted(shuffled, key=lambda e: -score[e])


def kendall_tau(order):
    n = len(order)
    if n < 2:
        return float("nan")
    s = sum((order[i] < order[j]) - (order[i] > order[j]) for i in range(n) for j in range(i + 1, n))
    return s / (n * (n - 1) / 2)


def list_results(setup, main, lists, labels, answers, model_years):
    rows = []
    for lst in lists:
        call = main.get(f"list|{lst['id']}")
        if call is None:
            continue
        parsed = parse_list(call["content"], lst["codes"], line_format=True)
        year_of = dict(zip(lst["codes"], lst["years_shown"]))
        order_years = [year_of[c] for c in parsed["order"]]
        row = {"id": lst["id"], "length": lst["length"], "band": lst["band"], "middle_year": lst["middle_year"],
               "valid": parsed["valid"], "continued_past_n": parsed["continued_past_n"],
               "missing": len(parsed["missing"]), "duplicates": len(parsed["duplicates"]),
               "invented": len(parsed["invented"]), "cut_off": call["done_reason"] == "length"}
        first_seen = list(dict.fromkeys(order_years))
        row["secondary_wrong"] = neighbor_labels(first_seen, labels, model_years)
        if parsed["valid"]:
            row["exact"] = order_years == sorted(order_years)
            row["tau"] = kendall_tau(order_years)
            row["wrong"] = neighbor_labels(order_years, labels, model_years)
            rng = random.Random(f"{TIE_SEED}|{setup}|{lst['id']}")
            predicted = copeland_order(sorted(lst["years_shown"]), answers, rng)
            row["predicted_wrong"] = sum(u > v for u, v in zip(predicted, predicted[1:]))
            row["penalty"] = len(row["wrong"]) - row["predicted_wrong"]
        else:
            row["exact"] = False
        rows.append(row)
    return rows


def boot_lists(rows, stat, rng, n=N_BOOT):
    """Point value and 95% range, redrawing lists within each cell."""
    cells = defaultdict(list)
    for r in rows:
        cells[(r["length"], r["band"])].append(r)
    point = stat(rows)
    draws = []
    for _ in range(n):
        sample = []
        for members in cells.values():
            sample.extend(members[k] for k in rng.integers(0, len(members), len(members)))
        draws.append(stat(sample))
    draws = [d for d in draws if d is not None and not math.isnan(d)]
    if point is None or not draws:
        return {"value": point, "ci95": None}
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"value": round(point, 4), "ci95": [round(float(lo), 4), round(float(hi), 4)]}


def share_of(kind, key="wrong"):
    def stat(rows):
        items = [w for r in rows for w in r.get(key, [])]
        return sum(w["type"] == kind for w in items) / len(items) if items else float("nan")
    return stat


def mean_of(field):
    def stat(rows):
        vals = [r[field] for r in rows if field in r]
        return sum(vals) / len(vals) if vals else float("nan")
    return stat


def list_summary(rows):
    rng = np.random.default_rng(BOOT_SEED)
    out = {"by_length": {}, "by_cell": {}}
    for length in (5, 10, 20):
        sub = [r for r in rows if r["length"] == length]
        if not sub:
            continue
        wrong = [w for r in sub for w in r.get("wrong", [])]
        out["by_length"][length] = {
            "lists": len(sub),
            "valid_share": round(sum(r["valid"] for r in sub) / len(sub), 4),
            "didnt_stop_share": round(sum(r["continued_past_n"] for r in sub) / len(sub), 4),
            "exact_share_of_all": round(sum(r["exact"] for r in sub) / len(sub), 4),
            "mean_tau_valid": mean_of("tau")(sub),
            "wrong_neighbor_pairs": len(wrong),
            "type_share": {k: boot_lists(sub, share_of(k), rng) for k in ("B", "U", "C", "X")},
            "misdated_share": round(sum(w["misdated"] for w in wrong) / len(wrong), 4) if wrong else None,
            "penalty_mean": boot_lists(sub, mean_of("penalty"), rng),
            "secondary_type_share": {k: round(share_of(k, "secondary_wrong")(sub), 4) for k in ("B", "U", "C", "X")},
        }
    for (length, band), sub in sorted(defaultdict(list, {
            k: [r for r in rows if (r["length"], r["band"]) == k] for k in {(r["length"], r["band"]) for r in rows}}).items()):
        out["by_cell"][f"{length}-{band}"] = {
            "lists": len(sub), "valid": sum(r["valid"] for r in sub), "exact": sum(r["exact"] for r in sub),
            "mean_tau_valid": mean_of("tau")(sub), "mean_penalty": mean_of("penalty")(sub),
            "type_C_share": share_of("C")(sub),
        }
    return out


def decision(summary):
    """The Q2 decision rules, PREREG.md section 6 (with the clarification in its Deviations)."""
    by = summary["by_length"]
    if not all(l in by for l in (5, 10, 20)):
        return "incomplete"
    c = {l: by[l]["type_share"]["C"]["value"] for l in (5, 10, 20)}
    pen = {l: by[l]["penalty_mean"]["ci95"] for l in (5, 10, 20)}
    mostly_pairs = all(v is not None and v <= 0.20 for v in c.values()) and \
        all(p is not None and p[0] <= 0 <= p[1] for p in pen.values())
    real_penalty = (c[20] is not None and c[5] is not None and c[20] > c[5] and c[20] >= 0.50) or \
        (pen[20] is not None and pen[20][0] > 0)
    if mostly_pairs and not real_penalty:
        return "mostly in the pairs"
    if real_penalty and not mostly_pairs:
        return "a real long-list penalty"
    return "in between"


# ---------------- run ----------------

def analyze(setup, lists):
    loaded = load_calls(setup)
    if loaded is None:
        return None
    main, repeats = loaded
    ref = REFERENCE.get(setup, setup)
    ref_main = main if ref == setup else load_calls(ref)[0]
    answers, labels = pair_table(ref_main)
    model_years = year_answers(ref_main)
    result = {"setup": setup, "pair_and_year_answers_from": ref}

    if ref == setup and labels:
        result["pairs"] = pair_summary(labels, answers)
        result["cycles"] = cycle_test(labels)
    if model_years:
        exact = [y for y, a in model_years.items() if a == y]
        result["year_check"] = {"exact": len(exact), "n": len(model_years),
                                "unreadable": sum(a is None for a in model_years.values())}
    rows = list_results(setup, main, lists, labels, answers, model_years)
    if rows:
        result["lists"] = list_summary(rows)
        result["q2_decision"] = decision(result["lists"])
    same = [repeats[k]["content"] == main[k]["content"] for k in repeats if k in main]
    result["repeat_check"] = {"identical": sum(same), "n": len(same)}
    return result, rows


def main():
    lists = json.loads((PROCESSED / "main_lists.json").read_text(encoding="utf-8"))["lists"]
    RESULTS.mkdir(parents=True, exist_ok=True)
    for setup in (sys.argv[1:] or SETUPS):
        out = analyze(setup, lists)
        if out is None:
            print(f"{setup}: no data yet")
            continue
        result, rows = out
        (RESULTS / f"{setup}.json").write_text(json.dumps(result, indent=1, default=float), encoding="utf-8")
        (RESULTS / f"{setup}_lists.json").write_text(json.dumps(rows, indent=1, default=float), encoding="utf-8")
        print(f"{setup}: wrote {RESULTS / (setup + '.json')}")


if __name__ == "__main__":
    main()
