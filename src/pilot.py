"""Step 2: the pilot (PLAN.md section 6). Pilot data is never used in the main analysis.

On 25 randomly chosen events it measures speed, unreadable replies, whether temperature 0 repeats
itself, whether list answers follow the code letters instead of the dates, and how long thinking
takes. Usage:
    python3 src/pilot.py --smoke   # 3 calls to check that everything connects
    python3 src/pilot.py           # the full pilot (resumes if interrupted)
"""

import argparse
import csv
import itertools
import random

from common import PROCESSED, RAW
from llm import RunLog
from prompts import LIST, PAIR, YEAR, list_lines, make_codes

PILOT_SEED = 2026
OUT = RAW / "model_runs" / "pilot" / "pilot_calls.jsonl"


def load_events():
    return [{"year": int(r["year"]), "text": r["event_text"]}
            for r in csv.DictReader((PROCESSED / "events.csv").open(encoding="utf-8"))]


def pilot_design():
    rng = random.Random(PILOT_SEED)
    events = rng.sample(load_events(), 25)
    pairs = list(itertools.combinations(events, 2))  # 300 pairs
    wording_b_pairs = rng.sample(pairs, 50)
    repeat_pairs = rng.sample(pairs, 25)
    lists = []
    for length, count in ((5, 6), (10, 6), (20, 4)):
        for k in range(count):
            chosen = rng.sample(events, length)
            codes = make_codes(rng, length)
            lists.append({"id": f"L{length}-{k}", "events": chosen, "codes": codes})
    return events, pairs, wording_b_pairs, repeat_pairs, lists


def ask_pair(log, config, wording, first, second, tag=""):
    prompt = PAIR[wording].format(a=first["text"], b=second["text"])
    key = f"pair|{config}|{wording}|{first['year']}|{second['year']}{tag}"
    return log.run(key, config, prompt, "pair", logprobs=True, wording=wording,
                   year_a=first["year"], year_b=second["year"])


def ask_list(log, config, wording, lst, tag=""):
    prompt = LIST[wording].format(lines=list_lines(lst["codes"], [e["text"] for e in lst["events"]]))
    key = f"list|{config}|{wording}|{lst['id']}{tag}"
    return log.run(key, config, prompt, "list", wording=wording, list_id=lst["id"], codes=lst["codes"],
                   years=[e["year"] for e in lst["events"]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    events, pairs, wording_b_pairs, repeat_pairs, lists = pilot_design()

    if args.smoke:
        log = RunLog(RAW / "model_runs" / "pilot" / "smoke_calls.jsonl")
        a, b = pairs[0]
        for r in (ask_pair(log, "qwen3-8b-nothink", "A", a, b),
                  log.run("smoke-year", "qwen3-8b-nothink", YEAR.format(event=a["text"]), "year"),
                  ask_list(log, "qwen3-8b-nothink", "A", lists[0])):
            print(f"{r['task']}: {r['content']!r} | thinking chars {len(r['thinking'])} | "
                  f"{r['seconds']}s | done {r['done_reason']} | logprobs {'yes' if r.get('logprobs') else 'no'}")
        return

    log = RunLog(OUT)
    steps = [
        ("year questions, qwen3 8B", lambda: [log.run(f"year|qwen3-8b-nothink|{e['year']}", "qwen3-8b-nothink",
                                                       YEAR.format(event=e["text"]), "year", year=e["year"])
                                              for e in events]),
        ("pairs, wording A, both orders", lambda: [(ask_pair(log, "qwen3-8b-nothink", "A", x, y),
                                                    ask_pair(log, "qwen3-8b-nothink", "A", y, x)) for x, y in pairs]),
        ("pairs, wording B", lambda: [(ask_pair(log, "qwen3-8b-nothink", "B", x, y),
                                       ask_pair(log, "qwen3-8b-nothink", "B", y, x)) for x, y in wording_b_pairs]),
        ("pairs, repeat check", lambda: [ask_pair(log, "qwen3-8b-nothink", "A", x, y, tag="|repeat")
                                         for x, y in repeat_pairs]),
        ("lists, wording A and B", lambda: [ask_list(log, "qwen3-8b-nothink", w, l) for w in "AB" for l in lists]),
        ("lists, repeat check", lambda: [ask_list(log, "qwen3-8b-nothink", "A", l, tag="|repeat") for l in lists[:4]]),
        ("lists, thinking on", lambda: [ask_list(log, "qwen3-8b-think", "A", l)
                                        for l in [x for x in lists if x["id"] in ("L10-0", "L10-1", "L20-0", "L20-1")]]),
        ("speed, qwen3 14B", lambda: [ask_pair(log, "qwen3-14b-nothink", "A", x, y) for x, y in pairs[:40]] +
                                     [ask_list(log, "qwen3-14b-nothink", "A", l) for l in lists if l["id"] in ("L20-0", "L20-1")]),
        ("speed, gpt-oss 20B low", lambda: [ask_pair(log, "gpt-oss-20b-low", "A", x, y) for x, y in pairs[:20]] +
                                           [ask_list(log, "gpt-oss-20b-low", "A", l) for l in lists if l["id"] in ("L20-0", "L20-1")]),
    ]
    for name, step in steps:
        print(f"-> {name}", flush=True)
        step()
    print(f"Pilot done. Calls saved in {OUT}")


if __name__ == "__main__":
    main()
