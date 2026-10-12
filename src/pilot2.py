"""Step 2b: second pilot, testing two list answer formats after the first pilot (PLAN.md section 6).

Same 16 pilot lists, Qwen3 8B with thinking off, formats C (rewrite full lines) and D (numbered
codes); plus the two 20-event lists on Qwen3 14B. Pilot data is never used in the main analysis.
"""

from common import RAW
from llm import RunLog
from pilot import ask_list, pilot_design

OUT = RAW / "model_runs" / "pilot" / "pilot2_calls.jsonl"


def main():
    _, _, _, _, lists = pilot_design()
    log = RunLog(OUT)
    for wording in ("C", "D"):
        print(f"-> qwen3 8B, format {wording}", flush=True)
        for lst in lists:
            ask_list(log, "qwen3-8b-nothink", wording, lst)
        print(f"-> qwen3 14B, format {wording}", flush=True)
        for lst in [l for l in lists if l["id"] in ("L20-0", "L20-1", "L10-0", "L10-1")]:
            ask_list(log, "qwen3-14b-nothink", wording, lst)
    print("Done", flush=True)


if __name__ == "__main__":
    main()
