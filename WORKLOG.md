# Work Log

A record of who did what, by date. The study was designed and directed by Jayden Ling; the code, analysis and
drafting were produced by Claude Code (an AI agent) under his direction. Times are UTC unless stated otherwise.

This log was condensed and edited for a formal tone on October 12, 2026. The original, more detailed entries remain
in the repository history.

## October 12, 2026

### Planning
- **Jayden Ling** selected this project from a set of candidate ideas and made the main design decisions: 120 events
  (one per year, 1900 to 2019, verified against Wikipedia and Wikidata), the random-month selection rule, and event
  wording that does not reveal dates. He decided that Claude Code would write the code, analysis and write-up while
  he directed the study, approved each model run and download, and checked the results, under the credit line in
  `PLAN.md`.
- **Claude Code** conducted the planning questions, checked the terms of the tools considered, confirmed the locally
  available models, and wrote `PLAN.md`. No code was written, no model was run and no data was downloaded at this
  stage.
- **Jayden Ling** approved `PLAN.md` and the Step 1 downloads.

### Step 1: answer key
- **Claude Code** wrote `src/common.py`, `src/pick_months.py`, `src/fetch_year_pages.py`, `src/select_events.py` and
  `src/build_answer_key.py`; downloaded the 120 Wikipedia year pages and the matching Wikidata dates (logged in
  `data/raw/SOURCES.md`); selected one event per year; wrote the 120 event descriptions
  (`data/manual/event_wording.csv`); and built `data/processed/events.csv`. Two selection rules were tightened before
  any model was run, both recorded in `PLAN.md` section 8: an exact-day Wikidata match and a notability floor of 20
  language editions. Answer-key fingerprint: `09b8fb5d6f705c0c1ea957cb4a53e52836787a6f5e8c6aca4d5e2ebb6c5f4916`.
- **Jayden Ling** spot-checked 10 event dates against the sources (all correct) and approved the pilot.

### Step 2: pilot
- **Claude Code** wrote `src/llm.py`, `src/prompts.py`, `src/pilot.py`, `src/pilot2.py`, `src/pilot3.py`,
  `src/pilot_report.py`, `src/make_main_lists.py` and `src/run_main.py`, and ran 906 pilot calls. The pilot showed
  that the planned list answer format produced near-random orders, so the format was changed to numbered codes
  (`PLAN.md` section 8). Claude Code generated the 240 main lists and wrote `PREREG.md`, which was committed before any
  main-run call.
- **Jayden Ling** approved the numbered list format and the main runs.

### Step 3: main runs
- **Claude Code** started the main runs at 19:05 on the Mac, wrote `src/analyze.py`, tested it on two simulated
  models with known answers, and added pre-analysis clarifications to `PREREG.md`.
- **Qwen3 8B (thinking off)** finished at about 20:01: 15,170 calls, no unreadable pair replies, and all 530 repeated
  questions answered identically. Claude Code ran the pre-registered analysis on it.
- **Llama 3.1 8B added.** Jayden Ling approved adding Llama 3.1 8B, run on his Windows PC, to test whether the Qwen3
  results hold for a model from another developer. This was recorded in `PREREG.md` before any of its answers existed.
- **Runs paused for a hardware comparison.** At Jayden Ling's request, Claude Code paused the Qwen3 14B and Llama runs
  to compare the speed of the Mac and the PC with matching settings. This set the PC's Ollama to its default settings.
- **Llama rerun.** Claude Code found that the first Llama attempt had run under two different PC configurations.
  Jayden Ling decided to set those answers aside (`llama3.1-8b.mixed-settings.jsonl`, unused) and to rerun Llama from
  the start on default settings. He also decided to skip the optional gpt-oss 20B setup. Both decisions were recorded
  in the `PREREG.md` Deviations before any of the affected answers were analyzed.
- **Llama crash and resume.** The rerun stopped at 21:24 after 13,710 of 14,280 pair questions, when the PC returned a
  server error caused by Windows running out of local network ports. Claude Code changed `src/llm.py` to reuse one
  connection per run and to retry server errors (tested on a simulated server; no change to the model, prompts or
  settings). With Jayden Ling's approval the run resumed from its saved file at 21:34 and finished at 21:39: 15,170
  calls, no duplicates, no unreadable pair replies. All 500 repeated pair questions matched; 24 of 30 repeated lists
  matched.
- **A trial run on the PC** of the thinking-on setup was started automatically after the crash. It failed on its first
  list, produced no data, and was not used.
- **Qwen3 14B (thinking off)** finished at 22:12 on the Mac: 15,170 calls, no duplicates, no unreadable pair replies,
  and all 530 repeated questions answered identically.
- **Qwen3 8B (thinking on), lists only.** Jayden Ling approved running this setup on the Mac. It started at 22:12, was
  interrupted once when the host application restarted, resumed from its saved file, and finished at 01:27 on
  October 13 (UTC): 240 lists.

### Step 4: analysis
- **Claude Code** (a separate analysis session) ran the pre-registered analysis for Llama 3.1 8B and Qwen3 14B and
  updated the charts. Code changes, none of which alter a pre-registered rule: Llama added and gpt-oss removed in
  `src/analyze.py` and `src/make_figures.py`; the circle-check shuffles made reproducible for the pre-registered seed
  (this moved only Qwen3 8B's expected count, from 3,277.95 to 3,280.88); the repeat check split into pairs and lists;
  and an exploratory script added (`src/explore_cutoff.py`).
- **Cut-off list replies.** Claude Code identified that `PREREG.md` can be read in two ways for lists that list every
  event and then reach the reply length limit, and that the reading changes Qwen3 8B's verdict. Jayden Ling decided,
  after this result was known, to apply the section 5 reading already used by the analysis code, and approved the
  wording of the Deviations entry that records the decision. Both results are reported.

### Step 5: report
- **Claude Code** analyzed the thinking-on lists, wrote `src/p6.py` for prediction P6, produced the final charts for
  all four setups, and wrote `writeup/REPORT.md` and `README.md`.
- **Independent check.** A separate AI helper (Claude Sonnet), given only `PREREG.md`, the event list and the raw
  replies, wrote its own scoring code and recomputed the headline pair, circle and list numbers. All matched
  (`verification/`).
- **Jayden Ling** asked that all public documents use a formal tone and that private planning notes be removed.
  Claude Code revised `README.md`, `writeup/REPORT.md`, `PLAN.md` and this log accordingly. `PREREG.md` was not
  rewritten, because it is a dated record.
- **README layout and credit wording.** At Jayden Ling's request, Claude Code restructured `README.md` to follow the
  layout common to published research repositories (results table and figure first, Setup, Usage, Contributions,
  Citation) and reworded the credit line to state his decisions specifically. No result or number was changed.
  Jayden Ling approved the new README. The same credit wording was then applied, with his approval, to
  `writeup/REPORT.md`, the header of this log and the repository description, and noted in `PLAN.md` section 8.
  `PREREG.md` was not changed, because it is a dated record.
- **Pending:** Jayden Ling's review and approval of `writeup/REPORT.md`.
- **Pre-publication pass.** At Jayden Ling's request to finish the study before release, Claude Code added the
  remaining pre-registered list measures to the report (exact match, Kendall tau, the misdated share and the
  secondary all-lists analysis), aligned the figure labels with the report's terms, cited the model license texts
  (checked by a separate AI helper: publishing model replies without weights carries no license obligation), and added
  `requirements.txt`. A fresh copy of the repository reproduced every result, table and figure byte for byte. No result
  changed.

### Step 6: exploratory analysis (not pre-registered)
- **Background.** After the report was drafted, Claude Code noted that the models' strong preference for the first
  option confounds the "reversal" category: a model that always answers "A" reverses on every pair. It proposed an
  exploratory re-analysis using the saved answer probabilities, with no new model calls. Jayden Ling deferred it.
- **Claude Code** (a separate analysis session) carried it out at about 03:10 on October 13 (UTC), using only the
  saved replies; no model was run. It wrote `src/explore_debias.py`, which removes the first-option preference by
  averaging each pair's answer probabilities over both orders, compares every pair of events in each valid list with
  these debiased judgments, and covers the four exploratory items listed in `PREREG.md` section 6. Outputs:
  `data/processed/results/exploratory_debias.json` and `data/processed/results/tables/exploratory_debias.csv`. Checks:
  both answer letters were present in all 42,840 thinking-disabled pair replies; the script reproduces the
  pre-registered pair shares and intervals and the adjacent-error counts exactly; repeated runs give byte-identical
  output. `src/analyze.py` and all pre-registered results are unchanged.
- **Claude Code** added section 7, "Exploratory analyses (not pre-registered)", to `writeup/REPORT.md` and renumbered
  the two sections after it. The main finding qualifies the report's interpretation: after the preference is
  removed, 40% to 53% of adjacent list errors coincide with an incorrect pair judgment, compared with 53% to 84% under
  the pre-registered labels. The Summary and `README.md` were not changed.
- **Pending:** Jayden Ling's review of section 7, and his decision on whether the Summary and `README.md` should
  mention it.
