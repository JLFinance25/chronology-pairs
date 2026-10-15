# Data Sources

One entry per download or dataset: link, date, what it is, and its license or terms. Files here are never edited by hand.

All downloads below were approved by Jayden on Oct 12, 2026, and made by scripts in `src/` written by Claude Code. They follow the Wikimedia API etiquette page (one request at a time, batched titles, `maxlag`, back off when busy). The User-Agent names the project but includes no personal contact details.

## 1. English Wikipedia year pages, 1900 to 2019
- **What:** the wikitext of the 120 pages titled "1900" to "2019", used to find each year's events.
- **How:** MediaWiki API, `action=query&prop=revisions`, script `src/fetch_year_pages.py`.
- **When:** 2026-10-12, 18:03 to 18:04 UTC.
- **Where:** `data/raw/wikipedia/<year>.json` (12 MB, not committed to git). Each file stores the revision ID. The exact version used can be reopened at `https://en.wikipedia.org/w/index.php?oldid=<revid>`. The revision IDs are also in `data/processed/events.csv`.
- **License:** Wikipedia text is under CC BY-SA 4.0 (and GFDL). Reuse needs credit, for example a link back to the page, plus a license notice. Source: https://en.wikipedia.org/wiki/Wikipedia:Copyrights (opened 2026-10-12).

## 2. Wikidata IDs and dates for linked articles
- **What:**
  - For each article linked from the candidate events, its Wikidata item ID (5,888 titles).
  - That item's date statements: point in time, start time, inception, publication date, official opening, first flight, launch date, first performance, dissolved, date of death (5,734 items).
  - How many Wikipedia and other sites link to it, used as the notability count (1,005 items).
- **How:**
  - English Wikipedia API `prop=pageprops` (Wikidata IDs).
  - Wikidata Query Service at https://query.wikidata.org/sparql (dates and site links).
  - Script `src/select_events.py`.
- **When:** 2026-10-12.
- **Where:** `data/raw/wikidata/*.json` (0.7 MB, not committed to git).
- **License:** Wikidata structured data is CC0 (public domain). Source: https://www.wikidata.org/wiki/Wikidata:Licensing (opened 2026-10-12).

## 3. Opening paragraphs of ten articles, for wording checks
- **What:** plain-text introductions used to word ten events uniquely without numbers:
  - 25th Academy Awards
  - 1st Academy Awards
  - Second Sudanese Civil War
  - Second Hungarian Republic
  - Mac OS X 10.0
  - 2005 United Kingdom general election
  - Jules Verne ATV
  - 2019 Estonian parliamentary election
  - Vanguard 1
  - Mercury-Atlas 9
- **How:** MediaWiki API `prop=extracts`.
- **When:** 2026-10-12, 18:24 UTC.
- **Where:** `data/raw/wikipedia/wording_checks.json`, with revision IDs.
- **License:** CC BY-SA 4.0, as in entry 1.

## Terms checked before downloading (2026-10-12)
- Wikimedia User-Agent policy: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy. It asks scripts to identify themselves and give contact info. We send a descriptive name without personal contact details. Nothing was blocked.
- MediaWiki API etiquette: https://www.mediawiki.org/wiki/API:Etiquette

## Model files
- `qwen3:8b`, `qwen3:14b` and `gpt-oss:20b` were already on this Mac before the project started; nothing was downloaded for them. Their Ollama IDs were recorded by `ollama list` at the start of the main runs (`data/raw/model_runs/main/console.log`). `gpt-oss:20b` was not used in the main study.
- `llama3.1:8b` was used on Jayden's Windows PC (added Oct 12, 2026; `PREREG.md` Deviations). Whether it was already on the PC or downloaded for this study is not recorded: UNVERIFIED. Its Ollama ID (`46e0c10c039e`, as stated in `PREREG.md`) does not appear in any saved log: UNVERIFIED.
- Licenses, checked Oct 12, 2026 (`writeup/REPORT.md` section 9): Qwen3 is Apache 2.0 (https://huggingface.co/Qwen/Qwen3-8B); Llama 3.1 is under the Llama 3.1 Community License (https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE). This repository contains model replies only, not model files.
