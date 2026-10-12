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
}

# Longest reply allowed per task. A reply cut off at this limit counts as invalid.
MAX_TOKENS = {"pair": 16, "year": 16, "list": 400}
MAX_TOKENS_THINKING = {"pair": 4096, "year": 4096, "list": 16384}


def chat(config_name, prompt, task, logprobs=False):
    cfg = CONFIGS[config_name]
    thinking = cfg["think"] not in (False, None)
    options = dict(cfg["options"])
    options["num_predict"] = (MAX_TOKENS_THINKING if thinking else MAX_TOKENS)[task]
    body = {
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
        "think": cfg["think"],
        "stream": False,
        "options": options,
        "keep_alive": "30m",
    }
    if logprobs:
        body["logprobs"] = True
        body["top_logprobs"] = 5
    start = time.time()
    response = requests.post(OLLAMA_CHAT, json=body, timeout=3600)
    response.raise_for_status()
    data = response.json()
    message = data.get("message", {})
    return {
        "config": config_name, "model": cfg["model"], "think": cfg["think"], "options": options,
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
