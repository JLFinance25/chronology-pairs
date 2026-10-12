# Work Log

Who did what, by date. Add a line or two every session.

## 2026-10-12
- Jayden: kept this as a backup idea after choosing `../phantom-answers` as the main project; asked for a folder for each finalist.
- Claude: ran the idea search that produced this idea and its refuter fixes; set up this folder, README and SOURCES.md. No project code written by Claude.

## 2026-10-12 (planning session)
- Jayden: answered the planning questions; chose 120 events (one per year, 1900 to 2019, checked on Wikipedia and Wikidata), the random-month picking rule, and no-leak event wording. Decided that for this project Claude writes all code, analysis and write-up while he directs, approves each run and checks results, with the public credit line in PLAN.md.
- Claude: ran the planning questions; checked Google AI tool terms (Gemini API requires 18+), Colab and Kaggle GPU limits, and JEI and arXiv rules; checked this Mac (Ollama already has qwen3:8b, qwen3:14b, gpt-oss:20b); wrote PLAN.md, including the scoring, model and scope decisions Jayden handed to Claude. No code written, no models run, nothing downloaded.
- Jayden (later Oct 12): approved PLAN.md, the integrity change, and the Step 1 downloads; chose to run everything on the MacBook.
- Claude (later Oct 12): Step 1, the answer key. Wrote `src/common.py`, `pick_months.py`, `fetch_year_pages.py`, `select_events.py` and `build_answer_key.py`. Downloaded 120 Wikipedia year pages and Wikidata dates (logged in `data/raw/SOURCES.md`). Picked one event per year, wrote the 120 no-leak descriptions in `data/manual/event_wording.csv`, and built `data/processed/events.csv`. Tightened two rules before any model run, both recorded in PLAN.md section 8: exact-day Wikidata match, and a notability floor of 20 language editions. Answer key fingerprint: 09b8fb5d6f705c0c1ea957cb4a53e52836787a6f5e8c6aca4d5e2ebb6c5f4916. No models run.
- Jayden (later Oct 12): spot-checked 10 event dates (all OK) and approved the pilot.
- Claude (later Oct 12): Step 2, the pilot, on this Mac. Wrote `src/llm.py`, `prompts.py`, `pilot.py`, `pilot2.py`, `pilot3.py`, `pilot_report.py`, `make_main_lists.py` and `run_main.py`. 906 pilot calls in total. The pilot found that the planned list format gave near-random orders, so lists switched to a numbered format, logged in PLAN.md section 8. Made the 240 main lists. Wrote PREREG.md. No main-run calls yet.
