"""Shared settings and a polite HTTP helper for Wikipedia and Wikidata.

Follows the Wikimedia API etiquette page (checked Oct 12, 2026): one request at a time,
batched titles, maxlag on every API call, and back off when the servers say they are busy.
"""

import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MANUAL = ROOT / "data" / "manual"

FIRST_YEAR = 1900
LAST_YEAR = 2019
YEARS = list(range(FIRST_YEAR, LAST_YEAR + 1))

# The random-month seed is fixed so anyone can rebuild the same event list.
MONTH_SEED = 20261012

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

# No personal contact details are sent (see WORKLOG for why).
USER_AGENT = (
    "ChronologyPairsResearchBot/0.1 (student research project; low-volume, read-only) "
    f"python-requests/{requests.__version__}"
)

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT

PAUSE_SECONDS = 1.0


def polite_get(url, params, max_tries=6):
    """GET with maxlag handling and exponential backoff. Returns parsed JSON."""
    wait = 5.0
    for attempt in range(1, max_tries + 1):
        response = _session.get(url, params=params, timeout=90)
        retry_after = response.headers.get("Retry-After")
        if response.status_code in (429, 503) or retry_after:
            time.sleep(float(retry_after) if retry_after else wait)
            wait *= 2
            continue
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error", {}).get("code") == "maxlag":
            time.sleep(wait)
            wait *= 2
            continue
        time.sleep(PAUSE_SECONDS)
        return data
    raise RuntimeError(f"Gave up after {max_tries} tries: {url} {params}")


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))
