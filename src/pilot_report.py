"""Summarize the pilot: speed, unreadable replies, repeatability, stop-rule checks, time projections.

Reads data/raw/model_runs/pilot/pilot_calls.jsonl, prints a report, and writes
data/processed/pilot_summary.json. Pilot numbers are for planning only, never for results.
"""

import json
import statistics
from collections import defaultdict

from common import PROCESSED, RAW
from prompts import parse_list, parse_pair, parse_year

CALLS = RAW / "model_runs" / "pilot" / "pilot_calls.jsonl"

# Main-run sizes from PLAN.md: 14,280 pair calls, 120 year calls, 240 lists (8 cells x 30)
# with lengths 5, 10 and 20 in the proportion 3:3:2.
MAIN_PAIRS, MAIN_YEARS, MAIN_LISTS = 14280, 120, {5: 90, 10: 90, 20: 60}


def kendall_tau(order, truth_rank):
    """-1 to 1: how close an order is to the true order (1 = identical)."""
    ranks = [truth_rank[x] for x in order]
    n = len(ranks)
    concordant = discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            if ranks[i] < ranks[j]:
                concordant += 1
            elif ranks[i] > ranks[j]:
                discordant += 1
    pairs = n * (n - 1) / 2
    return (concordant - discordant) / pairs if pairs else 1.0


def mean(xs):
    return round(statistics.mean(xs), 3) if xs else None


def main():
    calls = [json.loads(l) for l in CALLS.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_key = {c["key"]: c for c in calls}
    out = {"n_calls": len(calls)}
    print(f"Pilot calls: {len(calls)}\n")

    # ---- Speed by configuration and task
    speed = defaultdict(list)
    tokens = defaultdict(list)
    for c in calls:
        length = len(c.get("codes") or [])
        name = f"{c['config']} {c['task']}" + (f" len{length}" if length else "")
        speed[name].append(c["seconds"])
        tokens[name].append(c.get("output_tokens") or 0)
    print("SPEED (seconds per call; first call per model includes loading it)")
    out["speed"] = {}
    for name in sorted(speed):
        s = speed[name]
        out["speed"][name] = {"n": len(s), "median_s": round(statistics.median(s), 3), "mean_s": mean(s),
                              "mean_output_tokens": mean(tokens[name])}
        print(f"  {name:40} n={len(s):4}  median {statistics.median(s):7.2f}s  mean {statistics.mean(s):7.2f}s  "
              f"output tokens {statistics.mean(tokens[name]):7.0f}")

    # ---- Unreadable replies and cut-offs
    print("\nUNREADABLE REPLIES")
    out["unreadable"] = {}
    groups = defaultdict(lambda: [0, 0, 0])  # total, unreadable, cut off
    for c in calls:
        if c["task"] == "pair":
            bad = parse_pair(c["content"]) is None
        elif c["task"] == "year":
            bad = parse_year(c["content"]) is None
        else:
            bad = not parse_list(c["content"], c["codes"])["valid"]
        g = groups[f"{c['config']} {c['task']} wording {c.get('wording', '-')}"]
        g[0] += 1
        g[1] += bad
        g[2] += c["done_reason"] == "length"
    for name, (n, bad, cut) in sorted(groups.items()):
        out["unreadable"][name] = {"n": n, "unreadable_or_invalid": bad, "cut_off": cut}
        note = " (for lists: invalid = dropped, repeated or invented codes)" if "list" in name else ""
        print(f"  {name:45} {bad}/{n} unreadable or invalid, {cut} cut off{note}")

    # ---- Year check (stop rule: fewer than half exactly right -> raise the notability floor)
    years = [c for c in calls if c["task"] == "year"]
    exact = sum(parse_year(c["content"]) == c["year"] for c in years)
    within1 = sum(parse_year(c["content"]) is not None and abs(parse_year(c["content"]) - c["year"]) <= 1 for c in years)
    out["year_check"] = {"n": len(years), "exact": exact, "within_one_year": within1}
    print(f"\nYEAR CHECK (qwen3 8B): {exact}/{len(years)} exactly right, {within1}/{len(years)} within one year")
    print(f"  Stop rule 'fewer than half exactly right': {'TRIGGERED' if exact < len(years) / 2 else 'not triggered'}")

    # ---- Pairs, wording A, both orders
    def pair_label(config, wording, a, b):
        first = by_key.get(f"pair|{config}|{wording}|{a}|{b}")
        second = by_key.get(f"pair|{config}|{wording}|{b}|{a}")
        if not first or not second:
            return None
        p1, p2 = parse_pair(first["content"]), parse_pair(second["content"])
        if p1 is None or p2 is None:
            return "invalid"
        right1 = (p1 == "A") == (a < b)
        right2 = (p2 == "A") == (b < a)
        return "stable-right" if right1 and right2 else "stable-wrong" if not right1 and not right2 else "flip"

    seen, labels = set(), defaultdict(int)
    for c in calls:
        if c["task"] == "pair" and c["config"] == "qwen3-8b-nothink" and c["wording"] == "A" and "|repeat" not in c["key"]:
            pair = tuple(sorted((c["year_a"], c["year_b"])))
            if pair not in seen:
                seen.add(pair)
                labels[pair_label("qwen3-8b-nothink", "A", *pair)] += 1
    a_share = [parse_pair(c["content"]) for c in calls if c["task"] == "pair" and c["config"] == "qwen3-8b-nothink"]
    out["pairs_wording_A"] = dict(labels)
    print(f"\nPAIRS (qwen3 8B, wording A, {len(seen)} pairs asked both ways): {dict(labels)}")
    print(f"  Share of answers that are 'A': {a_share.count('A') / max(1, len(a_share)):.2f} (0.50 = no position bias)")

    # ---- Wording A vs B on the same pairs
    agree = total = 0
    for c in calls:
        if c["task"] == "pair" and c["wording"] == "B":
            other = by_key.get(f"pair|{c['config']}|A|{c['year_a']}|{c['year_b']}")
            if other:
                total += 1
                agree += parse_pair(other["content"]) == parse_pair(c["content"])
    out["wording_agreement_pairs"] = {"agree": agree, "n": total}
    print(f"  Wording A and B give the same answer on {agree}/{total} pair questions")

    # ---- Repeatability at temperature 0
    repeats = [c for c in calls if c["key"].endswith("|repeat")]
    same = sum(c["content"] == by_key[c["key"][: -len("|repeat")]]["content"] for c in repeats)
    out["repeatability"] = {"same": same, "n": len(repeats)}
    print(f"\nREPEATABILITY at temperature 0: {same}/{len(repeats)} repeated calls gave identical replies")

    # ---- Lists: exact match, Kendall tau, and whether answers follow the code letters
    print("\nLISTS")
    out["lists"] = {}
    rows = defaultdict(lambda: {"n": 0, "valid": 0, "exact": 0, "tau": [], "tau_codes": []})
    for c in calls:
        if c["task"] != "list" or c["key"].endswith("|repeat"):
            continue
        n = len(c["codes"])
        r = rows[f"{c['config']} wording {c['wording']} len{n}"]
        r["n"] += 1
        parsed = parse_list(c["content"], c["codes"])
        if not parsed["valid"]:
            continue
        r["valid"] += 1
        year_of = dict(zip(c["codes"], c["years"]))
        truth_rank = {code: rank for rank, code in enumerate(sorted(c["codes"], key=year_of.get))}
        r["exact"] += parsed["order"] == sorted(c["codes"], key=year_of.get)
        r["tau"].append(kendall_tau(parsed["order"], truth_rank))
        alpha_rank = {code: rank for rank, code in enumerate(sorted(c["codes"]))}
        r["tau_codes"].append(kendall_tau(parsed["order"], alpha_rank))
    for name, r in sorted(rows.items()):
        out["lists"][name] = {"n": r["n"], "valid": r["valid"], "exact": r["exact"], "mean_tau": mean(r["tau"]),
                              "mean_tau_vs_code_letters": mean(r["tau_codes"])}
        print(f"  {name:40} valid {r['valid']}/{r['n']}  exact {r['exact']}/{r['valid']}  "
              f"tau vs truth {mean(r['tau'])}  tau vs alphabetical codes {mean(r['tau_codes'])}")
    l20 = rows.get("qwen3-8b-nothink wording A len20")
    if l20 and l20["valid"]:
        share = l20["exact"] / l20["valid"]
        print(f"  Stop rule '90% of 20-event lists exactly right': {'TRIGGERED' if share >= 0.9 else 'not triggered'} ({share:.0%})")

    # ---- Projected main-run time (hours), using median seconds per call
    def med(name):
        return statistics.median(speed[name]) if name in speed else None

    print("\nPROJECTED MAIN-RUN TIME (hours, from pilot medians; guesses until the main runs)")
    out["projection_hours"] = {}
    for config in ("qwen3-8b-nothink", "qwen3-14b-nothink", "qwen3-8b-think", "gpt-oss-20b-low"):
        parts = {}
        if med(f"{config} pair"):
            parts["pairs"] = MAIN_PAIRS * med(f"{config} pair") / 3600
        if med(f"{config} year"):
            parts["years"] = MAIN_YEARS * med(f"{config} year") / 3600
        list_hours = 0
        for length, count in MAIN_LISTS.items():
            m = med(f"{config} list len{length}") or med(f"{config} list len20")
            if m:
                list_hours += count * m / 3600
        if list_hours:
            parts["lists"] = list_hours
        if parts:
            out["projection_hours"][config] = {k: round(v, 2) for k, v in parts.items()}
            print(f"  {config:20} " + ", ".join(f"{k} {v:.1f}" for k, v in parts.items()))

    (PROCESSED / "pilot_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nSaved {PROCESSED / 'pilot_summary.json'}")


if __name__ == "__main__":
    main()
