#!/usr/bin/env python3
"""Independent recomputation of headline numbers for the chronology-pairs study.

Written Oct 12, 2026 by a separate AI helper (Claude Sonnet) that was given only PREREG.md, events.csv and the
raw replies, not src/analyze.py or any results, as a check on the main analysis.

Written from PREREG.md sections 5 and 6 only. Standard library only. Reads raw JSONL files
and data/processed/events.csv; never touches the network, a model or any server.

Usage: python3 -I independent_check.py
Writes independent_check.md next to this script.
"""
import csv
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the project folder
RUNS = os.path.join(ROOT, "data/raw/model_runs/main")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_MD = os.path.join(OUT_DIR, "independent_check.md")

OFF_SETUPS = ["qwen3-8b-nothink", "qwen3-14b-nothink", "llama3.1-8b"]
THINK = "qwen3-8b-think"
LENGTHS = [5, 10, 20]
BANDS = [("1 year", 1, 1), ("2 years", 2, 2), ("3 to 5", 3, 5), ("6 to 10", 6, 10),
         ("11 to 25", 11, 25), (">25", 26, 10**9)]
EXPECTED_BAND_COUNTS = {"1 year": 119, "2 years": 118, "3 to 5": 348, "6 to 10": 560,
                        "11 to 25": 1530, ">25": 4465}

notes = []  # diagnostics gathered while running; written into the md file


def load_events():
    with open(os.path.join(ROOT, "data/processed/events.csv"), newline="") as f:
        years = [int(r["year"]) for r in csv.DictReader(f)]
    assert len(years) == 120 and len(set(years)) == 120, "expected 120 distinct years"
    return sorted(years)


def load_setup(setup):
    """Non-repeat records only. Malformed (e.g. half-written last) lines are skipped and counted."""
    recs, bad, repeats = [], 0, 0
    with open(os.path.join(RUNS, setup + ".jsonl")) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if "|repeat" in r["key"]:
                repeats += 1
                continue
            recs.append(r)
    return recs, bad, repeats



JUDGMENT_CALLS = [
    "Pair replies: readable = the whole reply is the single letter A or B (spaces, quotes, markdown stars and a final "
    "period would be tolerated). In all three files every non-repeat pair reply is exactly 'A' or 'B', so unreadable = 0 "
    "and the rule changes nothing. All pair replies ended with done_reason 'stop'.",
    "Pair label: right/wrong is judged from the year fields (year_a, year_b) of each record, not from the prompt text. "
    "A flip = one order right and the other wrong (this includes always answering 'A' or always 'B'). "
    "Gap = difference in true years; band counts came out at exactly 119/118/348/560/1530/4465 for every setup.",
    "Position bias: counted over all 14,280 non-repeat pair replies (each ordered pair once), not over pairs.",
    "Circular triples: triple taken in true year order x<y<z over all 120 events; circular = labels (xy,yz,xz) "
    "right,right,wrong or wrong,wrong,right, where right/wrong mean stable-right/stable-wrong. A triple with any flip "
    "or unreadable pair is skipped (not counted in the all-stable total). No shuffle baseline.",
    "List parsing (written from PREREG section 5): a 'numbered entry' is a line starting with a number followed by '.' "
    "or ')' (leading spaces, stars, underscores, backticks, '>' or '-' tolerated). The entry's code is the first "
    "letters/digits token after the number. Lines without a number (e.g. Llama's 'Here is the list...' preamble, or "
    "notes) are ignored. Only the first N numbered entries are read; anything after is ignored (so Qwen3 8B's "
    "repetition loops and Qwen3 14B's second 'corrected' list after the first N entries do not count against it).",
    "List validity: valid only if there are exactly N numbered entries read, all different, all codes from that list. "
    "A reply with fewer than N numbered entries (e.g. 9 of 10, 19 of 20) is invalid (a code is missing). A repeated code "
    "or an entry that is not one of the list's codes also makes the list invalid. Codes are matched case-sensitively "
    "(no entry matched only after upper-casing).",
    "Cut-off replies: lists whose reply hit the 400-token limit are still scored on their first N entries if those are "
    "valid (PREREG section 5 reading, as adopted in the PREREG Deviations). This affects only qwen3-8b-nothink (16 of its 184 valid lists; see "
    "table). Under the stricter section 3 reading ('cut off counts as unreadable') those lists would be invalid.",
    "Wrong neighbor pairs: only in valid lists; consecutive entries where the first event's true year is later. Labeled "
    "C/U/B/X from the pair label of that unordered pair for the same setup (Qwen3 8B-think uses qwen3-8b-nothink "
    "labels). The 'misdated' flag (year answers), win counting, list penalty, Kendall tau and error ranges were not "
    "computed. 'Exactly right' counts valid lists with zero wrong neighbor pairs (extra).",
    "qwen3-8b-think: the file contains all 240 non-repeat list records. Every "
    "reply ended with done_reason 'stop'; the `content` field is used (the final answer) and not `thinking`. List ids, "
    "codes and true years are identical across all four files.",
]


# ---------------------------------------------------------------- pairs
def parse_pair(content):
    """'A' or 'B' if the whole reply is that single letter (ignoring spaces, quotes, markdown, a final period)."""
    t = content.strip().strip("*_`\"' ").rstrip(".").strip()
    return t if t in ("A", "B") else None


def band_of(gap):
    for name, lo, hi in BANDS:
        if lo <= gap <= hi:
            return name
    raise ValueError(gap)


def pair_labels(recs, years):
    """Return (labels, stats). labels[(lo, hi)] in {'R','W','F','X'} (stable-right/-wrong, flip, unreadable)."""
    seen = defaultdict(dict)  # (lo, hi) -> {'lo_first': right?, 'hi_first': right?}  (None if unreadable)
    n_a = n_readable = n_unreadable = n_nonexact = 0
    for r in recs:
        if r["task"] != "pair":
            continue
        ya, yb = r["year_a"], r["year_b"]
        assert r["key"] == "pair|%d|%d" % (ya, yb), r["key"]
        reply = parse_pair(r["content"])
        if reply is None:
            n_unreadable += 1
        else:
            n_readable += 1
            n_a += reply == "A"
            if r["content"] != reply:
                n_nonexact += 1
        lo, hi = min(ya, yb), max(ya, yb)
        order = "lo_first" if ya == lo else "hi_first"
        assert order not in seen[(lo, hi)], "duplicate ordered pair %s" % r["key"]
        if reply is None:
            seen[(lo, hi)][order] = None
        elif order == "lo_first":
            seen[(lo, hi)][order] = reply == "A"  # lo shown as A: right iff the reply is A
        else:
            seen[(lo, hi)][order] = reply == "B"  # lo shown as B: right iff the reply is B
    assert len(seen) == 7140, len(seen)
    labels = {}
    for k, d in seen.items():
        assert len(d) == 2, k
        r1, r2 = d["lo_first"], d["hi_first"]
        if r1 is None or r2 is None:
            labels[k] = "X"
        elif r1 and r2:
            labels[k] = "R"
        elif (not r1) and (not r2):
            labels[k] = "W"
        else:
            labels[k] = "F"
    stats = {"n_replies_readable": n_readable, "n_replies_unreadable": n_unreadable,
             "n_A": n_a, "n_nonexact": n_nonexact}
    return labels, stats


def band_table(labels):
    out = {}
    for name, _, _ in BANDS:
        out[name] = Counter()
    for (lo, hi), lab in labels.items():
        out[band_of(hi - lo)][lab] += 1
    for name in out:
        n = sum(out[name].values())
        if n != EXPECTED_BAND_COUNTS[name]:
            notes.append("WARNING band %s has %d pairs, expected %d" % (name, n, EXPECTED_BAND_COUNTS[name]))
    return out


def circular_triples(labels, years):
    """Count all-stable triples and circular ones. Triple in true order x<y<z; labels (xy, yz, xz)."""
    total = circ = 0
    ys = years
    n = len(ys)
    for i in range(n):
        for j in range(i + 1, n):
            a = labels[(ys[i], ys[j])]
            if a not in "RW":
                continue
            for k in range(j + 1, n):
                b = labels[(ys[j], ys[k])]
                if b not in "RW":
                    continue
                c = labels[(ys[i], ys[k])]
                if c not in "RW":
                    continue
                total += 1
                if (a, b, c) in (("R", "R", "W"), ("W", "W", "R")):
                    circ += 1
    return circ, total


# ---------------------------------------------------------------- lists
ENTRY_RE = re.compile(r"^[\s*_`>-]*(\d+)\s*[.)]\s*(.*)$")
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def parse_list(content, codes, n):
    """Read the first n numbered entries (lines that start with 'number.' or 'number)').
    Each entry's code is the first alphanumeric token after the number (markdown stars/underscores/backticks
    skipped). Unnumbered lines (preambles, notes) are ignored. Returns dict with entries and integrity details."""
    entries = []
    for line in content.splitlines():
        m = ENTRY_RE.match(line)
        if not m:
            continue
        rest = m.group(2).strip().strip("*_`").strip()
        tok = TOKEN_RE.match(rest)
        entries.append(tok.group(0) if tok else "")
        if len(entries) == n:
            break
    codeset = set(codes)
    invented = [e for e in entries if e not in codeset]
    cnt = Counter(e for e in entries if e in codeset)
    repeated = sorted(c for c, v in cnt.items() if v > 1)
    missing = sorted(codeset - set(entries))
    valid = (len(entries) == n and not invented and not repeated and not missing)
    return {"entries": entries, "valid": valid, "invented": invented, "repeated": repeated,
            "missing": missing, "short": len(entries) < n}


LABEL_TO_TYPE = {"R": "C", "F": "U", "W": "B", "X": "X"}


def score_lists(recs, pair_lab, label):
    by_len = {L: {"lists": 0, "valid": 0, "wnp": Counter(), "exact": 0,
                  "inv_any_missing": 0, "inv_any_repeated": 0, "inv_any_invented": 0, "inv_short": 0,
                  "valid_cut": 0}
              for L in LENGTHS}
    n_lists = 0
    odd_case = 0
    for r in recs:
        if r["task"] != "list":
            continue
        n = r["length"]
        codes, years = r["codes"], r["years"]
        assert len(codes) == n == len(years), r["key"]
        n_lists += 1
        info = parse_list(r["content"], codes, n)
        d = by_len[n]
        d["lists"] += 1
        # sanity: a lower-case version of a real code would show up here
        odd_case += sum(1 for e in info["entries"] if e not in codes and e.upper() in codes)
        if not info["valid"]:
            d["inv_any_missing"] += bool(info["missing"])
            d["inv_any_repeated"] += bool(info["repeated"])
            d["inv_any_invented"] += bool(info["invented"])
            d["inv_short"] += info["short"]
            continue
        d["valid"] += 1
        d["valid_cut"] += r.get("done_reason") == "length"  # valid on its first N entries, but reply hit the token limit
        yr = dict(zip(codes, years))
        order_years = [yr[e] for e in info["entries"]]
        wrong = 0
        for a, b in zip(order_years, order_years[1:]):
            if a > b:  # first event actually happened later
                wrong += 1
                d["wnp"][LABEL_TO_TYPE[pair_lab[(b, a)]]] += 1
        d["exact"] += wrong == 0
    if odd_case:
        notes.append("%s: %d list entries match a code only after upper-casing" % (label, odd_case))
    assert n_lists == 240, "%s has %d non-repeat lists" % (label, n_lists)
    return by_len


def check_same_lists(base, other, label):
    ba = {r["list_id"]: r for r in base if r["task"] == "list"}
    ot = {r["list_id"]: r for r in other if r["task"] == "list"}
    ok = set(ba) == set(ot) and all(ba[k]["codes"] == ot[k]["codes"] and ba[k]["years"] == ot[k]["years"]
                                    for k in ba)
    notes.append("List sets identical (ids, codes, years) for %s vs qwen3-8b-nothink: %s" % (label, ok))
    return ok


# ---------------------------------------------------------------- formatting
def pct(x, n):
    return "%.1f%%" % (100.0 * x / n) if n else "n/a"


def main():
    years = load_events()
    lines = []
    emit = lines.append

    # wait for the thinking file if it is short (instruction: up to 15 minutes, then use what's there)
    waited = 0
    while True:
        think_recs, think_bad, think_rep = load_setup(THINK)
        n_think = sum(1 for r in think_recs if r["task"] == "list")
        if n_think >= 240 or waited >= 15:
            break
        time.sleep(60)
        waited += 1
    notes.append("qwen3-8b-think: %d non-repeat list records read (%d repeat lines ignored, %d malformed lines "
                 "skipped, waited %d min)" % (n_think, think_rep, think_bad, waited))

    results = {}
    labels_by_setup = {}
    for s in OFF_SETUPS:
        recs, bad, rep = load_setup(s)
        notes.append("%s: %d non-repeat records (%d repeat lines ignored, %d malformed skipped)" % (s, len(recs), rep, bad))
        lab, st = pair_labels(recs, years)
        labels_by_setup[s] = lab
        bt = band_table(lab)
        circ, tot = circular_triples(lab, years)
        lists = score_lists(recs, lab, s)
        results[s] = {"stats": st, "bands": bt, "circ": circ, "tot": tot, "lists": lists,
                      "overall": Counter(lab.values()), "recs": recs}

    base = results["qwen3-8b-nothink"]["recs"]
    check_same_lists(base, think_recs, THINK)
    for s in OFF_SETUPS[1:]:
        check_same_lists(base, results[s]["recs"], s)
    think_lists = score_lists(think_recs, labels_by_setup["qwen3-8b-nothink"], THINK)

    # ---- markdown
    emit("# Independent check (recomputed from raw files, following PREREG sections 5 and 6)")
    emit("")
    emit("Repeat-check records (`|repeat` keys) are excluded everywhere. Thinking-off setups: "
         "qwen3-8b-nothink (8B), qwen3-14b-nothink (14B), llama3.1-8b (Llama).")
    emit("")
    emit("## 1. Pairs (shares are of readable pairs; stable-right = SR, flip = FL, stable-wrong = SW)")
    emit("")
    emit("| Setup | Band | Pairs | Readable | SR | SR % | FL | FL % | SW | SW % |")
    emit("|---|---|---|---|---|---|---|---|---|---|")
    for s in OFF_SETUPS:
        for band in ("1 year", ">25"):
            c = results[s]["bands"][band]
            n = sum(c.values())
            rd = n - c["X"]
            emit("| %s | %s | %d | %d | %d | %s | %d | %s | %d | %s |" % (
                s, band, n, rd, c["R"], pct(c["R"], rd), c["F"], pct(c["F"], rd), c["W"], pct(c["W"], rd)))
    emit("")
    emit("Position bias (share of readable pair replies that are \"A\", repeats excluded):")
    emit("")
    emit("| Setup | Readable replies | Unreadable replies | \"A\" replies | Share \"A\" |")
    emit("|---|---|---|---|---|")
    for s in OFF_SETUPS:
        st = results[s]["stats"]
        emit("| %s | %d | %d | %d | %s |" % (s, st["n_replies_readable"], st["n_replies_unreadable"],
                                             st["n_A"], pct(st["n_A"], st["n_replies_readable"])))
    emit("")
    emit("All six gap bands (extra, for reference):")
    emit("")
    emit("| Setup | " + " | ".join("%s (SR / FL)" % b[0] for b in BANDS) + " |")
    emit("|---|" + "---|" * len(BANDS))
    for s in OFF_SETUPS:
        cells = []
        for name, _, _ in BANDS:
            c = results[s]["bands"][name]
            rd = sum(c.values()) - c["X"]
            cells.append("%s / %s" % (pct(c["R"], rd), pct(c["F"], rd)))
        emit("| %s | %s |" % (s, " | ".join(cells)))
    emit("")
    emit("## 2. Circular triples (triples whose three pairs are all stable)")
    emit("")
    emit("| Setup | All-stable triples | Circular | Circular share |")
    emit("|---|---|---|---|")
    for s in OFF_SETUPS:
        r = results[s]
        emit("| %s | %d | %d | %.3f%% |" % (s, r["tot"], r["circ"], 100.0 * r["circ"] / r["tot"]))
    emit("")
    emit("(Shuffle baseline skipped, as asked. 120 events give 280,840 triples in total.)")
    emit("")
    emit("## 3. Lists")
    emit("")
    emit("Valid = first N numbered entries are N different codes from the list, none invented. "
         "Wrong neighbor pair = two consecutive entries, first one actually later. C = stable-right on the pair "
         "alone, U = flip, B = stable-wrong (X = unreadable pair). "
         "Labels for qwen3-8b-think come from qwen3-8b-nothink pair answers; others use their own.")
    emit("")
    emit("| Setup | N | Lists | Valid | Valid % | Wrong neighbor pairs | C | C % | U | U % | B | B % | X | Exactly right (valid, 0 wrong) |")
    emit("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    all_list_results = [(s, results[s]["lists"]) for s in OFF_SETUPS] + [(THINK, think_lists)]
    for s, L in all_list_results:
        for n in LENGTHS:
            d = L[n]
            w = sum(d["wnp"].values())
            emit("| %s | %d | %d | %d | %s | %d | %d | %s | %d | %s | %d | %s | %d | %d |" % (
                s, n, d["lists"], d["valid"], pct(d["valid"], d["lists"]), w,
                d["wnp"]["C"], pct(d["wnp"]["C"], w), d["wnp"]["U"], pct(d["wnp"]["U"], w),
                d["wnp"]["B"], pct(d["wnp"]["B"], w), d["wnp"]["X"], d["exact"]))
    emit("")
    emit("Why lists were invalid (a list can have several problems; counts are of lists):")
    emit("")
    emit("| Setup | N | Invalid lists | Fewer than N numbered entries | With a missing code | With a repeated code | With an invented/unreadable entry |")
    emit("|---|---|---|---|---|---|---|")
    for s, L in all_list_results:
        for n in LENGTHS:
            d = L[n]
            emit("| %s | %d | %d | %d | %d | %d | %d |" % (
                s, n, d["lists"] - d["valid"], d["inv_short"], d["inv_any_missing"],
                d["inv_any_repeated"], d["inv_any_invented"]))
    emit("")
    emit("Valid lists whose reply hit the 400-token limit after the N entries (scored on the first N entries, "
         "per the PREREG section 5 reading and the Oct 12 22:30 deviation):")
    emit("")
    emit("| Setup | N=5 | N=10 | N=20 |")
    emit("|---|---|---|---|")
    for s_, L in all_list_results:
        emit("| %s | %d | %d | %d |" % (s_, L[5]["valid_cut"], L[10]["valid_cut"], L[20]["valid_cut"]))
    emit("")
    emit("## Judgment calls")
    emit("")
    for j in JUDGMENT_CALLS:
        emit("- " + j)
    emit("")
    emit("## Run notes")
    emit("")
    for n in notes:
        emit("- " + n)
    emit("")

    text = "\n".join(lines)
    with open(OUT_MD, "w") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
