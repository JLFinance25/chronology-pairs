"""Step 4: the main runs (PLAN.md section 6). Resumes automatically if interrupted.

Usage examples:
    python3 src/run_main.py --config qwen3-8b-nothink --tasks years,pairs,lists,repeats
    python3 src/run_main.py --config qwen3-8b-think --tasks lists

Every call is saved to data/raw/model_runs/main/<config>.jsonl. The prompt wordings are fixed in
PREREG.md and set below; do not change them after the pre-registration.
"""

import argparse
import csv
import itertools
import json
import random

from common import PROCESSED, RAW
from llm import RunLog
from prompts import LIST, PAIR, YEAR, list_lines

PAIR_WORDING = "A"   # fixed in PREREG.md (pilot: 0 unreadable replies, identical on repeat)
LIST_WORDING = "D"   # fixed in PREREG.md (numbered codes; codes-only answers gave near-random orders)
ORDER_SEED = 31      # order in which pair calls are made (shuffled so drift can't line up with gap)
REPEAT_SEED = 32     # which calls are repeated to check that temperature 0 repeats itself
N_REPEAT_PAIRS, N_REPEAT_LISTS = 500, 30


def load_events():
    return {int(r["year"]): r["event_text"] for r in csv.DictReader((PROCESSED / "events.csv").open(encoding="utf-8"))}


def load_lists():
    return json.loads((PROCESSED / "main_lists.json").read_text(encoding="utf-8"))["lists"]


def pair_calls(events):
    """Every ordered pair: 7,140 pairs x 2 orders = 14,280 calls, in a fixed shuffled order."""
    calls = [(a, b) for a, b in itertools.permutations(sorted(events), 2)]
    random.Random(ORDER_SEED).shuffle(calls)
    return calls


def ask_pair(log, config, events, a, b, tag=""):
    prompt = PAIR[PAIR_WORDING].format(a=events[a], b=events[b])
    return log.run(f"pair|{a}|{b}{tag}", config, prompt, "pair", logprobs=True,
                   wording=PAIR_WORDING, year_a=a, year_b=b)


def ask_list(log, config, lst, tag=""):
    prompt = LIST[LIST_WORDING].format(lines=list_lines(lst["codes"], lst["texts"]))
    return log.run(f"list|{lst['id']}{tag}", config, prompt, "list", wording=LIST_WORDING, list_id=lst["id"],
                   codes=lst["codes"], years=lst["years_shown"], length=lst["length"], band=lst["band"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--tasks", default="years,pairs,lists,repeats")
    args = parser.parse_args()
    tasks = args.tasks.split(",")
    events, lists = load_events(), load_lists()
    log = RunLog(RAW / "model_runs" / "main" / f"{args.config}.jsonl")

    if "years" in tasks:
        print("-> years (120)", flush=True)
        for y, text in sorted(events.items()):
            log.run(f"year|{y}", args.config, YEAR.format(event=text), "year", year=y)
    if "pairs" in tasks:
        calls = pair_calls(events)
        print(f"-> pairs ({len(calls)})", flush=True)
        for i, (a, b) in enumerate(calls, 1):
            ask_pair(log, args.config, events, a, b)
            if i % 1000 == 0:
                print(f"   {i}/{len(calls)}", flush=True)
    if "lists" in tasks:
        print(f"-> lists ({len(lists)})", flush=True)
        for i, lst in enumerate(lists, 1):
            ask_list(log, args.config, lst)
            if i % 20 == 0:
                print(f"   {i}/{len(lists)}", flush=True)
    if "repeats" in tasks:
        rng = random.Random(REPEAT_SEED)
        print(f"-> repeats ({N_REPEAT_PAIRS} pairs, {N_REPEAT_LISTS} lists)", flush=True)
        for a, b in rng.sample(pair_calls(events), N_REPEAT_PAIRS):
            ask_pair(log, args.config, events, a, b, tag="|repeat")
        for lst in rng.sample(lists, N_REPEAT_LISTS):
            ask_list(log, args.config, lst, tag="|repeat")
    print("Done.", flush=True)


if __name__ == "__main__":
    main()
