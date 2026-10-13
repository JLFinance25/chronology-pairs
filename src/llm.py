"""Calling local models through Ollama, with every call saved as raw data.

One settings preset per model configuration, so the same scripts run any model (PLAN.md, "one
script works for every model"). Every call is appended to a JSONL file under data/raw/model_runs/,
keyed so an interrupted run resumes where it stopped instead of starting over.
"""

import json
import time
from datetime import datetime, timezone

import requests

OLLAMA_CHAT = "http://localhost:11434/api/chat"
# The Windows PC's Ollama, reached from the Mac through an SSH tunnel:
#   ssh -f -N -o ServerAliveInterval=15 -L 127.0.0.1:11500:127.0.0.1:11434 pc
# Moved from port 11435 on Oct 12, 2026: that tunnel stopped passing traffic.
PC_CHAT = "http://127.0.0.1:11500/api/chat"

# Settings checked Oct 12, 2026 against the model pages and `ollama show`:
#   Qwen3: thinking can be on or off; with thinking on, the model page says not to use greedy
#          decoding and recommends temperature 0.6, top_p 0.95, top_k 20, min_p 0.
#   gpt-oss: reasoning cannot be turned off; levels are low, medium, high (default medium).
CONFIGS = {
    "qwen3-8b-nothink": {"model": "qwen3:8b", "think": False,
                         "options": {"temperature": 0, "seed": 0, "num_ctx": 4096}},
    "qwen3-14b-nothink": {"model": "qwen3:14b", "think": False,
                          "options": {"temperature": 0, "seed": 0, "num_ctx": 4096}},
    "qwen3-8b-think": {"model": "qwen3:8b", "think": True,
                       "options": {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "min_p": 0,
                                   "seed": 0, "num_ctx": 20480}},
    "gpt-oss-20b-low": {"model": "gpt-oss:20b", "think": "low",
                        "options": {"temperature": 0, "seed": 0, "num_ctx": 8192}},
    # Added Oct 12 (PREREG.md Deviations). No thinking mode, so "think" is left out of the request.
    "llama3.1-8b": {"model": "llama3.1:8b", "think": None, "host": "pc",
                    "options": {"temperature": 0, "seed": 0, "num_ctx": 4096}},
}

# Longest reply allowed per task. A reply cut off at this limit counts as invalid.
MAX_TOKENS = {"pair": 16, "year": 16, "list": 400}
MAX_TOKENS_THINKING = {"pair": 4096, "year": 4096, "list": 16384}

# One connection reused for the whole run (added Oct 12, 2026, 21:40 UTC). Opening a new connection for
# every call used up the PC's local ports after ~13,800 fast calls (HTTP 500).
# This changes only how requests travel, not what is sent, so answers are unaffected.
SESSION = requests.Session()


def chat(config_name, prompt, task, logprobs=False):
    cfg = CONFIGS[config_name]
    thinking = cfg["think"] not in (False, None)
    options = dict(cfg["options"])
    options["num_predict"] = (MAX_TOKENS_THINKING if thinking else MAX_TOKENS)[task]
    body = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": options,
        "keep_alive": "30m",
    }
    if cfg["think"] is not None:
        body["think"] = cfg["think"]
    url = PC_CHAT if cfg.get("host") == "pc" else OLLAMA_CHAT
    if logprobs:
        body["logprobs"] = True
        body["top_logprobs"] = 5
    start = time.time()
    # Retry if the connection drops (the PC is reached over a network tunnel). A resent request
    # gets the same answer at temperature 0, so retrying cannot change results.
    for attempt in range(6):
        try:
            # 15 minutes is far longer than any answer should take (the longest pilot answer
            # took 91 s); a request stuck longer than that is retried.
            response = SESSION.post(url, json=body, timeout=900)
            response.raise_for_status()
            break
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as error:
            # Oct 12: also retry server errors (5xx). The PC's Ollama briefly returned 500s when Windows
            # ran out of local connection ports during fast runs. Client errors (4xx) still stop the run.
            response_code = getattr(getattr(error, "response", None), "status_code", None)
            if attempt == 5 or (response_code is not None and response_code < 500):
                raise
            time.sleep(5 * 2 ** attempt)
    data = response.json()
    message = data.get("message", {})
    return {
        "config": config_name, "model": cfg["model"], "think": cfg["think"], "options": options,
        "host": cfg.get("host", "mac"),
        "prompt": prompt, "content": message.get("content", ""), "thinking": message.get("thinking", ""),
        "done_reason": data.get("done_reason"), "prompt_tokens": data.get("prompt_eval_count"),
        "output_tokens": data.get("eval_count"), "seconds": round(time.time() - start, 3),
        "logprobs": data.get("logprobs") if logprobs else None,
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


class RunLog:
    """Append-only JSONL log of model calls, keyed for resuming."""

    def __init__(self, path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.done = {}
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    record = json.loads(line)
                    self.done[record["key"]] = record

    def run(self, key, config_name, prompt, task, logprobs=False, **extra):
        if key in self.done:
            return self.done[key]
        record = {"key": key, "task": task, **extra, **chat(config_name, prompt, task, logprobs)}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.done[key] = record
        return record
