"""Exploratory (not in PREREG.md): pair judgments with the first-option ("A") bias removed, using saved logprobs.

Usage:
    python3 src/explore_debias.py

The thinking-off models chose the first option ("A") in 54% to 79% of pair answers (src/analyze.py). A model that
always answers "A" gives a flip on every pair, so some pairs that PREREG.md section 5 labels "flip" may reflect the
position of the events rather than uncertainty about their order. Every saved pair reply has the log-probabilities
of its first answer token, and these include both "A" and "B" for all 42,840 thinking-off pair calls (checked below;
the chosen letter is always the more probable of the two). This script uses only those saved replies; it runs no
model.

1. Debiased pair judgment. In each order, P(A) and P(B) are renormalized to sum to 1. The probability that the
   earlier event is judged earlier is P(A) when it was shown first and P(B) when it was shown second; the debiased
   probability p is the mean over the two orders. The pair is judged correctly if p > 0.5. (This is the same as the
   two orders' log-odds summing to more than zero, so the right/wrong call does not depend on averaging
   probabilities rather than log-odds. The "clearly decided" counts do, so they are also given with log-odds
   averaging, as a check.)
2. Lists (Q2 without the pair-accuracy confound). For every pair of events in each valid list (all pairs, not only
   neighbors), does the list put them in the order the debiased pair judgment favors? Also a pair-based ordering of
   each list from summed debiased probabilities, compared with the pre-registered win counting.
3. The exploratory items listed in PREREG.md section 6: answer probability vs gap, position bias by gap, the list's
   middle year (era), and year-question accuracy by decade.

Intervals: pair results, 2,000 redraws of the 120 events (seed 41; the same redraws as src/analyze.py); list
results, 2,000 redraws of lists within each cell (seed 41, src/analyze.py's boot_lists).

Writes data/processed/results/exploratory_debias.json and data/processed/results/tables/exploratory_debias.csv.
Written by Claude Code on Oct 12, 2026, after the pre-registered results were final. Nothing here changes them.
"""

import csv
import json
import math
import random
from collections import defaultdict

import numpy as np

import analyze as A
from prompts import parse_list, parse_pair

PAIR_SETUPS = ["qwen3-8b-nothink", "qwen3-14b-nothink", "llama3.1-8b"]
CLEAR = 0.25  # a pair is "clearly decided" if |p - 0.5| > 0.25
ERAS = ["1900-1939", "1940-1979", "1980-2019"]  # by middle year; a list centred on 1939.5 counts as 1900-1939
OUT_JSON = A.RESULTS / "exploratory_debias.json"
OUT_CSV = A.RESULTS / "tables" / "exploratory_debias.csv"


def r4(x):
    return None if x is None or math.isnan(x) else round(float(x), 4)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def era_of(year):
    return ERAS[0] if year < 1940 else ERAS[1] if year < 1980 else ERAS[2]


# ---------------- pairs ----------------

def pair_calls(main):
    """{(shown_A, shown_B): first-token logprobs of "A" and "B", the answer, and the answer's probability}."""
    out = {}
    for c in main.values():
        if c["task"] != "pair":
            continue
        first = c["logprobs"][0]
        top = {t["token"]: t["logprob"] for t in first["top_logprobs"]}
        answer = parse_pair(c["content"])
        assert "A" in top and "B" in top, c["key"]
        assert answer == first["token"] and (top["A"] > top["B"]) == (answer == "A"), c["key"]
        out[(c["year_a"], c["year_b"])] = {"lA": top["A"], "lB": top["B"], "answer": answer,
                                           "p_answer": math.exp(first["logprob"]), "mass": math.exp(top["A"]) + math.exp(top["B"])}
    return out


def pair_arrays(calls, labels, model_years):
    """One entry per unordered pair (earlier, later), in sorted order."""
    pairs = sorted(labels)
    c1 = [calls[(a, b)] for a, b in pairs]  # earlier event shown as A
    c2 = [calls[(b, a)] for a, b in pairs]  # earlier event shown as B
    x1 = np.array([c["lA"] - c["lB"] for c in c1])  # log-odds that the earlier event is judged earlier
    x2 = np.array([c["lB"] - c["lA"] for c in c2])
    p = (sigmoid(x1) + sigmoid(x2)) / 2
    p_logit = sigmoid((x1 + x2) / 2)
    s = x1 + x2
    corr1 = np.array([c["answer"] == "A" for c in c1], dtype=float)
    corr2 = np.array([c["answer"] == "B" for c in c2], dtype=float)
    label = np.array([labels[q] for q in pairs])
    is_flip = (label == "flip").astype(float)
    n_a = np.array([(u["answer"] == "A") + (v["answer"] == "A") for u, v in zip(c1, c2)], dtype=float)
    pans1 = np.array([c["p_answer"] for c in c1])
    pans2 = np.array([c["p_answer"] for c in c2])
    weaker = np.minimum(np.abs(x1), np.abs(x2))  # log-odds of the chosen letter in the less confident order
    years = [(model_years.get(a), model_years.get(b)) for a, b in pairs]
    return {
        "pairs": pairs, "p": p, "s": s, "label": label,
        "gap": np.array([b - a for a, b in pairs]),
        "mid": np.array([(a + b) / 2 for a, b in pairs]),
        "ones": np.ones(len(pairs)),
        "correct": np.where(s > 0, 1.0, np.where(s == 0, 0.5, 0.0)),
        "p_correct": p,
        "confidence": np.maximum(p, 1 - p),
        "confidence_logit": np.maximum(p_logit, 1 - p_logit),
        "stable_right": (label == "stable-right").astype(float),
        "is_flip": is_flip,
        "flip_both_A": is_flip * (n_a == 2),
        "flip_debiased_right": is_flip * (s > 0),
        "flip_clear_right": is_flip * (p > 0.5 + CLEAR),
        "flip_clear_wrong": is_flip * (p < 0.5 - CLEAR),
        "flip_clear_right_logit": is_flip * (p_logit > 0.5 + CLEAR),
        "flip_clear_wrong_logit": is_flip * (p_logit < 0.5 - CLEAR),
        "flip_both_above_099": is_flip * (weaker > math.log(99)),  # chosen letter above 0.99 in both orders
        "year_order": np.array(["unreadable" if ya is None or yb is None else "right" if ya < yb else
                                "wrong" if ya > yb else "same year" for ya, yb in years]),
        "n_A": n_a, "two": np.full(len(pairs), 2.0),
        "sum_P_A": sigmoid(np.array([c["lA"] - c["lB"] for c in c1])) + sigmoid(np.array([c["lA"] - c["lB"] for c in c2])),
        "sum_p_answer": pans1 + pans2,
        "n_correct_calls": corr1 + corr2, "n_wrong_calls": 2 - corr1 - corr2,
        "sum_p_answer_correct": pans1 * corr1 + pans2 * corr2,
        "sum_p_answer_wrong": pans1 * (1 - corr1) + pans2 * (1 - corr2),
    }


def event_weights(pairs):
    """Pair weights for 2,000 redraws of the events, drawn exactly as src/analyze.py's pair_summary draws them."""
    years = sorted({y for q in pairs for y in q})
    index = {y: k for k, y in enumerate(years)}
    rng = np.random.default_rng(A.BOOT_SEED)
    m = np.array([rng.multinomial(len(years), [1 / len(years)] * len(years)) for _ in range(A.N_BOOT)], dtype=np.float32)
    i = np.array([index[a] for a, _ in pairs])
    j = np.array([index[b] for _, b in pairs])
    return m[:, i] * m[:, j]


def ratio(arr, num, den, mask, w):
    """Weighted ratio sum(num)/sum(den) over the pairs in mask, with its 95% range over the event redraws."""
    n, d = arr[num][mask], arr[den][mask]
    point = n.sum() / d.sum() if d.sum() else float("nan")
    with np.errstate(invalid="ignore", divide="ignore"):
        draws = (w @ n) / (w @ d)
    draws = draws[~np.isnan(draws)]
    lo, hi = np.percentile(draws, [2.5, 97.5]) if len(draws) else (float("nan"), float("nan"))
    return {"value": r4(point), "ci95": [r4(lo), r4(hi)]}


PAIR_STATS = {  # name: (numerator, denominator)
    "debiased_correct_share": ("correct", "ones"),
    "mean_p_correct": ("p_correct", "ones"),
    "mean_confidence": ("confidence", "ones"),
    "mean_confidence_logodds_average": ("confidence_logit", "ones"),
    "prereg_stable_right_share": ("stable_right", "ones"),
    "flip_share": ("is_flip", "ones"),
    "flips_with_both_answers_A": ("flip_both_A", "is_flip"),
    "flips_debiased_correct": ("flip_debiased_right", "is_flip"),
    "flips_clearly_correct": ("flip_clear_right", "is_flip"),
    "flips_clearly_wrong": ("flip_clear_wrong", "is_flip"),
    "flips_clearly_correct_logodds_average": ("flip_clear_right_logit", "is_flip"),
    "flips_clearly_wrong_logodds_average": ("flip_clear_wrong_logit", "is_flip"),
    "flips_both_orders_above_0.99": ("flip_both_above_099", "is_flip"),
    "share_A_answers": ("n_A", "two"),
    "mean_renormalized_P_A": ("sum_P_A", "two"),
    "mean_p_answer": ("sum_p_answer", "two"),
    "mean_p_answer_when_correct": ("sum_p_answer_correct", "n_correct_calls"),
    "mean_p_answer_when_wrong": ("sum_p_answer_wrong", "n_wrong_calls"),
}
COUNTS = ["ones", "is_flip", "flip_debiased_right", "flip_clear_right", "flip_clear_wrong",
          "flip_clear_right_logit", "flip_clear_wrong_logit"]


def pair_analysis(arr):
    w_all = event_weights(arr["pairs"])
    bands = np.array([A.band_of(g) for g in arr["gap"]])
    groups = [(name, bands == name) for name, _, _ in A.BANDS] + [("all", np.ones(len(bands), dtype=bool))]
    out = {"by_gap_band": {}}
    for name, mask in groups:
        w = w_all[:, mask]
        row = {"counts": {("pairs" if k == "ones" else k): int(arr[k][mask].sum()) for k in COUNTS}}
        row.update({stat: ratio(arr, num, den, mask, w) for stat, (num, den) in PAIR_STATS.items()})
        out["by_gap_band"][name] = row
    # Validity check: are flips judged correctly more often when the model's own year answers order them correctly?
    out["flips_by_own_year_answers"] = {}
    for order in ("right", "wrong", "same year", "unreadable"):
        mask = (arr["year_order"] == order) & (arr["is_flip"] == 1)
        if mask.any():
            out["flips_by_own_year_answers"][order] = {
                "flips": int(mask.sum()), "debiased_correct": ratio(arr, "correct", "ones", mask, w_all[:, mask])}
    names = [b[0] for b in A.BANDS]
    out["debiased_date_resolution"] = next(
        (names[k] for k in range(len(names))
         if all(out["by_gap_band"][b]["debiased_correct_share"]["value"] >= 0.95 for b in names[k:])), "not reached")
    # Era of the pair (midpoint), for pairs at most 10 years apart so the gap mix is similar across eras.
    out["by_era_pairs_gap_1_to_10"] = {}
    eras = np.array([era_of(m) for m in arr["mid"]])
    for era in ERAS:
        mask = (arr["gap"] <= 10) & (eras == era)
        w = w_all[:, mask]
        out["by_era_pairs_gap_1_to_10"][era] = {
            "pairs": int(mask.sum()),
            "debiased_correct_share": ratio(arr, "correct", "ones", mask, w),
            "prereg_stable_right_share": ratio(arr, "stable_right", "ones", mask, w),
        }
    return out


def year_by_decade(model_years):
    out = {}
    for decade in range(1900, 2020, 10):
        ys = [y for y in model_years if decade <= y < decade + 10]
        readable = [y for y in ys if model_years[y] is not None]
        errors = [abs(model_years[y] - y) for y in readable]
        out[f"{decade}s"] = {"events": len(ys), "exact": sum(e == 0 for e in errors),
                             "within_1_year": sum(e <= 1 for e in errors), "unreadable": len(ys) - len(readable),
                             "median_abs_error": float(np.median(errors)) if errors else None}
    return out


# ---------------- lists ----------------

def list_rows(setup, lists, arr):
    """One row per list; valid lists get all-pairs agreement counts and the debiased pair-based ordering."""
    main = A.load_calls(setup)[0]
    saved = {r["id"]: r for r in json.loads((A.RESULTS / f"{setup}_lists.json").read_text(encoding="utf-8"))}
    p = dict(zip(arr["pairs"], arr["p"]))
    judged = dict(zip(arr["pairs"], arr["correct"]))  # 1 if the debiased judgment is right, 0.5 on an exact tie
    label = dict(zip(arr["pairs"], arr["label"]))

    def before(u, v):  # debiased probability that u is judged earlier than v
        return p[(u, v)] if u < v else 1 - p[(v, u)]

    rows = []
    for lst in lists:
        parsed = parse_list(main[f"list|{lst['id']}"]["content"], lst["codes"], line_format=True)
        row = {"id": lst["id"], "length": lst["length"], "band": lst["band"], "middle_year": lst["middle_year"],
               "valid": parsed["valid"], "valid_n": float(parsed["valid"]), "one": 1.0}
        assert parsed["valid"] == saved[lst["id"]]["valid"]
        if parsed["valid"]:
            year_of = dict(zip(lst["codes"], lst["years_shown"]))
            order = [year_of[c] for c in parsed["order"]]
            c = defaultdict(float)
            for i in range(len(order)):
                for j in range(i + 1, len(order)):
                    u, v = order[i], order[j]  # the list puts u before v
                    q = (min(u, v), max(u, v))
                    list_right, pair_right = float(u < v), judged[q]
                    agree = pair_right if list_right else 1 - pair_right
                    c["pairs"] += 1
                    c["list_right"] += list_right
                    c["pair_right"] += pair_right
                    c["agree"] += agree
                    c["list_wrong"] += 1 - list_right
                    c["both_wrong"] += (1 - list_right) * (1 - pair_right)
                    c[f"n_{label[q]}"] += 1
                    c[f"agree_{label[q]}"] += agree
                    if j == i + 1:
                        c["adjacent"] += 1
                        c["adj_pair_wrong"] += 1 - pair_right
                        if u > v:
                            c["adj_wrong"] += 1
                            c["adj_wrong_pair_wrong"] += 1 - pair_right
                            c[f"adj_wrong_{label[q]}"] += 1
                            c[f"adj_wrong_{label[q]}_pair_wrong"] += 1 - pair_right
            assert c["adj_wrong"] == len(saved[lst["id"]]["wrong"])
            years = sorted(lst["years_shown"])
            score = {e: sum(before(e, f) for f in years if f != e) for e in years}
            shuffled = years[:]
            random.Random(f"{A.TIE_SEED}|{setup}|{lst['id']}|debiased").shuffle(shuffled)
            predicted = sorted(shuffled, key=lambda e: -score[e])
            row.update(c)
            row["tau"] = saved[lst["id"]]["tau"]
            row["debiased_predicted_wrong"] = float(sum(u > v for u, v in zip(predicted, predicted[1:])))
            row["debiased_predicted_tau"] = A.kendall_tau(predicted)
            row["debiased_penalty"] = c["adj_wrong"] - row["debiased_predicted_wrong"]
            row["prereg_predicted_wrong"] = float(saved[lst["id"]]["predicted_wrong"])
            row["prereg_penalty"] = float(saved[lst["id"]]["penalty"])
        rows.append(row)
    cell_tau = defaultdict(list)
    for r in rows:
        if r["valid"]:
            cell_tau[(r["length"], r["band"])].append(r["tau"])
    for r in rows:
        if r["valid"]:
            r["tau_vs_cell_mean"] = r["tau"] - float(np.mean(cell_tau[(r["length"], r["band"])]))
    return rows


def sum_ratio(num, den):
    def stat(rows):
        d = sum(r.get(den, 0.0) for r in rows)
        return sum(r.get(num, 0.0) for r in rows) / d if d else float("nan")
    return stat


def kappa(rows):
    """Agreement between list order and debiased pair judgment beyond what independent errors would give."""
    n = sum(r.get("pairs", 0.0) for r in rows)
    if not n:
        return float("nan")
    a_list = sum(r.get("list_right", 0.0) for r in rows) / n
    a_pair = sum(r.get("pair_right", 0.0) for r in rows) / n
    observed = sum(r.get("agree", 0.0) for r in rows) / n
    expected = a_list * a_pair + (1 - a_list) * (1 - a_pair)
    return (observed - expected) / (1 - expected) if expected < 1 else float("nan")


def independent_agreement(rows):
    n = sum(r.get("pairs", 0.0) for r in rows)
    if not n:
        return float("nan")
    a_list = sum(r.get("list_right", 0.0) for r in rows) / n
    a_pair = sum(r.get("pair_right", 0.0) for r in rows) / n
    return a_list * a_pair + (1 - a_list) * (1 - a_pair)


LIST_STATS = {
    "valid_share": sum_ratio("valid_n", "one"),
    "agreement_all_pairs": sum_ratio("agree", "pairs"),
    "agreement_if_independent": independent_agreement,
    "kappa": kappa,
    "list_correct_share_all_pairs": sum_ratio("list_right", "pairs"),
    "debiased_pair_correct_share_all_pairs": sum_ratio("pair_right", "pairs"),
    "list_errors_also_wrong_debiased": sum_ratio("both_wrong", "list_wrong"),
    "agreement_stable_right_pairs": sum_ratio("agree_stable-right", "n_stable-right"),
    "agreement_flip_pairs": sum_ratio("agree_flip", "n_flip"),
    "agreement_stable_wrong_pairs": sum_ratio("agree_stable-wrong", "n_stable-wrong"),
    "adjacent_errors_also_wrong_debiased": sum_ratio("adj_wrong_pair_wrong", "adj_wrong"),
    "adjacent_pairs_wrong_debiased": sum_ratio("adj_pair_wrong", "adjacent"),
    "adjacent_flip_errors_also_wrong_debiased": sum_ratio("adj_wrong_flip_pair_wrong", "adj_wrong_flip"),
    "mean_adjacent_errors": A.mean_of("adj_wrong"),
    "mean_prereg_predicted_errors": A.mean_of("prereg_predicted_wrong"),
    "mean_debiased_predicted_errors": A.mean_of("debiased_predicted_wrong"),
    "mean_prereg_penalty": A.mean_of("prereg_penalty"),
    "mean_debiased_penalty": A.mean_of("debiased_penalty"),
    "mean_tau": A.mean_of("tau"),
    "mean_debiased_predicted_tau": A.mean_of("debiased_predicted_tau"),
}
LIST_COUNTS = ["valid_n", "pairs", "list_wrong", "both_wrong", "n_stable-right", "n_flip", "n_stable-wrong",
               "adj_wrong", "adj_wrong_pair_wrong", "adj_wrong_stable-right", "adj_wrong_flip", "adj_wrong_stable-wrong",
               "adj_wrong_flip_pair_wrong"]


def list_analysis(rows):
    rng = np.random.default_rng(A.BOOT_SEED)
    out = {"by_length": {}, "by_era": {}}
    for length in (5, 10, 20):
        sub = [r for r in rows if r["length"] == length]
        entry = {"lists": len(sub), "counts": {k: int(sum(r.get(k, 0.0) for r in sub)) for k in LIST_COUNTS}}
        entry.update({name: A.boot_lists(sub, stat, rng) for name, stat in LIST_STATS.items()})
        out["by_length"][length] = entry
    for era in ERAS:
        sub = [r for r in rows if era_of(r["middle_year"]) == era]
        out["by_era"][era] = {
            "lists": len(sub), "valid": int(sum(r["valid"] for r in sub)),
            "lengths": {length: sum(r["length"] == length for r in sub) for length in (5, 10, 20)},
            "valid_share": A.boot_lists(sub, sum_ratio("valid_n", "one"), rng),
            "mean_tau": A.boot_lists(sub, A.mean_of("tau"), rng),
            "mean_tau_vs_cell_mean": A.boot_lists(sub, A.mean_of("tau_vs_cell_mean"), rng),
            "debiased_pair_correct_share_all_pairs": A.boot_lists(sub, sum_ratio("pair_right", "pairs"), rng),
        }
    return out


# ---------------- output ----------------

def csv_rows(result):
    rows = []

    def add(section, setup, group, measure, value, n=None):
        if isinstance(value, dict):
            ci = value.get("ci95") or [None, None]
            rows.append([section, setup, group, measure, value.get("value"), ci[0], ci[1], n])
        else:
            rows.append([section, setup, group, measure, value, None, None, n])

    for setup, res in result["pairs"].items():
        for band, row in res["by_gap_band"].items():
            for stat in PAIR_STATS:
                add("pairs_by_gap", setup, band, stat, row[stat], row["counts"]["pairs"])
            for k, v in row["counts"].items():
                add("pairs_by_gap", setup, band, f"count_{k}", v)
        add("pairs", setup, "all", "debiased_date_resolution", res["debiased_date_resolution"])
        for order, row in res["flips_by_own_year_answers"].items():
            add("flips_by_own_year_answers", setup, order, "debiased_correct_share", row["debiased_correct"], row["flips"])
        for era, row in res["by_era_pairs_gap_1_to_10"].items():
            for stat in ("debiased_correct_share", "prereg_stable_right_share"):
                add("pairs_by_era_gap_1_to_10", setup, era, stat, row[stat], row["pairs"])
    for setup, res in result["year_by_decade"].items():
        for decade, row in res.items():
            for k, v in row.items():
                add("year_by_decade", setup, decade, k, v)
    for setup, res in result["lists"].items():
        for length, row in res["by_length"].items():
            for stat in LIST_STATS:
                add("lists_by_length", setup, length, stat, row[stat], row["counts"]["valid_n"])
            for k, v in row["counts"].items():
                add("lists_by_length", setup, length, f"count_{k}", v)
        for era, row in res["by_era"].items():
            for stat in ("valid_share", "mean_tau", "mean_tau_vs_cell_mean", "debiased_pair_correct_share_all_pairs"):
                add("lists_by_era", setup, era, stat, row[stat], row["valid"])
    return rows


def main():
    lists = json.loads((A.PROCESSED / "main_lists.json").read_text(encoding="utf-8"))["lists"]
    result = {
        "status": "exploratory, not pre-registered (PREREG.md section 6 lists the last four items as exploratory)",
        "made_by": "src/explore_debias.py",
        "debiasing": "renormalize P(A), P(B) per order; p = mean over both orders of P(earlier event judged earlier)",
        "clearly_decided": f"|p - 0.5| > {CLEAR}",
        "checks": {}, "pairs": {}, "year_by_decade": {}, "lists": {},
    }
    arrays = {}
    for setup in PAIR_SETUPS:
        main_calls = A.load_calls(setup)[0]
        calls = pair_calls(main_calls)
        _, labels = A.pair_table(main_calls)
        arrays[setup] = pair_arrays(calls, labels, A.year_answers(main_calls))
        masses = [c["mass"] for c in calls.values()]
        result["checks"][setup] = {"pair_calls": len(calls), "with_A_and_B_in_top_logprobs": len(calls),
                                   "answer_is_more_probable_letter": len(calls),
                                   "min_P_A_plus_P_B": r4(min(masses)), "median_P_A_plus_P_B": r4(float(np.median(masses)))}
        result["pairs"][setup] = pair_analysis(arrays[setup])
        result["year_by_decade"][setup] = year_by_decade(A.year_answers(main_calls))
        print(f"{setup}: pairs done")
    for setup in A.SETUPS:
        ref = A.REFERENCE.get(setup, setup)
        rows = list_rows(setup, lists, arrays[ref])
        result["lists"][setup] = {"pair_answers_from": ref, **list_analysis(rows)}
        print(f"{setup}: lists done")
    OUT_JSON.write_text(json.dumps(result, indent=1), encoding="utf-8")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["section", "setup", "group", "measure", "value", "ci_low", "ci_high", "n"])
        writer.writerows(csv_rows(result))
    print(f"wrote {OUT_JSON} and {OUT_CSV}")


if __name__ == "__main__":
    main()
