"""Step 2c: third pilot. Numbered list format (D) with thinking on and with gpt-oss, on the
pilot's 10- and 20-event lists. Pilot data is never used in the main analysis."""

from common import RAW
from llm import RunLog
from pilot import ask_list, pilot_design

OUT = RAW / "model_runs" / "pilot" / "pilot3_calls.jsonl"


def main():
    _, _, _, _, lists = pilot_design()
    chosen = [l for l in lists if l["id"] in ("L10-0", "L10-1", "L20-0", "L20-1")]
    log = RunLog(OUT)
    for config in ("qwen3-8b-think", "gpt-oss-20b-low"):
        print(f"-> {config}, format D", flush=True)
        for lst in chosen:
            ask_list(log, config, "D", lst)
    print("Done", flush=True)


if __name__ == "__main__":
    main()
