# Pairwise Temporal Judgments and List Ordering in Small Language Models

**Jayden Ling** · [Report](writeup/REPORT.md) · [Pre-registration](PREREG.md) · [Data](data/) · [Code](src/)

Directed by Jayden Ling, who chose the research question from candidate ideas, set the core design (event rules,
selection and wording), approved the plan, the pre-registration and every run, and made each later decision. Code,
analysis and drafting by Claude Code (an AI agent) under his direction. See [Contributions](#contributions).

Large language models largely preserve the local order of events, yet they rarely place a long list of events in
exactly the correct order (Wongchamcharoen and Glasserman, 2025). This study examines small models that run on consumer
hardware. It finds that these models often do not answer "which came first?" reliably even for pairs of events, and
asks whether their errors on long lists are already present in their judgments about pairs of events, or arise only when
lists become long.

![Date resolution](figures/fig1_date_resolution.png)

## Principal results

| | Qwen3 8B | Qwen3 14B | Llama 3.1 8B |
|---|---|---|---|
| Pairs more than 25 years apart answered correctly in both orders (pre-registered threshold: at least 95%, with at most 5% reversals) | 68% | 86% | 29% |
| Pair answers that chose the first option presented | 69% | 54% | 79% |
| Exact year given, out of 120 events | 87 | 102 | 97 |
| List errors that occur only within lists, by list length | 19% to 31% | 35% to 47% | 16% to 20% |
| 20-event answers containing every event exactly once | 25% | 50% | 28% |

All three models were run with reasoning disabled. Year answers that could not be read are not counted as exact
(1 for Qwen3 14B, 3 for Llama 3.1 8B; `data/processed/results/<setup>.json`, `year_check`). Sources and 95% intervals
are given in [`writeup/REPORT.md`](writeup/REPORT.md), section 3.

- **No model reached a reliable "date resolution".** No gap between events, including more than 25 years, met the
  pre-registered threshold.
- **Pre-registered verdicts on the origin of list errors.** Under the pre-registered decision rules, Qwen3 8B shows
  "a real long-list penalty" (a tentative verdict: it rests on 15 complete 20-event lists and depends on a scoring
  decision made after results were seen and on random tie-breaking), while Qwen3 14B, Llama 3.1 8B and Qwen3 8B with
  reasoning enabled are classified "in between". Most list errors fell on pairs that the model had also answered
  incorrectly or inconsistently (69% to 84% for Qwen3 8B and Llama 3.1 8B, 53% to 65% for Qwen3 14B, depending on
  list length), but such pairs are common among close events, so this does not by itself show that list errors arise
  from pair errors. An exploratory re-analysis that removes the models' preference for the first option weakens the
  pair-level account: about half of list errors (40% to 53%) then coincide with an incorrect pair judgment
  ([report, section 7](writeup/REPORT.md)).
- **Reasoning improved list ordering substantially** (Qwen3 8B ordered 57% of 5-event lists exactly with reasoning
  enabled, against 3% with it disabled), consistent with the improvement from added reasoning effort reported by
  Wongchamcharoen and Glasserman (2025). The reasoning setup also differed in sampling temperature, context size and
  reply length limit (report, section 5). The prediction that reasoning would specifically reduce errors that occur
  only within lists was not established: the direction matched at every list length, but the pre-registration set no
  test and the change in the list-only share alone is not distinguishable from zero.

## Overview

- **Data.** 120 historical events, one per year from 1900 to 2019, drawn from Wikipedia and verified against
  Wikidata. The short event descriptions shown to the models were written by an AI system and checked against the
  sources.
- **Models.** Four setups: Qwen3 8B, Qwen3 14B and Llama 3.1 8B with reasoning disabled, and Qwen3 8B with reasoning
  enabled.
- **Design.** Each pair of events was presented twice, once in each order (14,280 questions per model), and each
  model ordered the same 240 lists of 5, 10 or 20 events. Every error in a list is traced to the model's own answer
  on the corresponding pair.
- **Pre-registration.** The hypotheses, prompts and decision rules were committed to this project's git repository
  in [`PREREG.md`](PREREG.md) before the main data were collected (the only timestamps are those of the git history;
  there is no external registry). All later changes are dated in its Deviations section. The pre-registration's
  opening sentence attributes "small" models to the 2025 paper in error (report, section 4).
- **Scoring.** Answers are scored against verified dates by deterministic code; no AI system grades another's
  answers. A second, separately written scoring program (another AI model, given the pre-registration and the raw
  replies) reproduced the pair shares, first-option rates, cycle counts and list composition (`verification/`). It
  did not recompute intervals, the list penalty or any verdict.

## Setup

The results were produced with Python 3.14.

```
pip install -r requirements.txt
```

## Usage

The raw model replies are included, so every result and figure can be regenerated without running a model:

```
python3 src/analyze.py                         # pre-registered analysis -> data/processed/results/
python3 src/p6.py                              # reasoning enabled vs disabled (prediction P6)
python3 src/explore_debias.py                  # exploratory analysis: first-option preference removed (report, section 7)
python3 src/explore_cutoff.py qwen3-8b-nothink # exploratory: cut-off lists as unreadable; prints to the terminal
                                               # (saved as data/processed/results/explore_cutoff_qwen3-8b-nothink.txt)
python3 src/make_figures.py                    # figures -> figures/
python3 -I verification/independent_check.py   # separately written recomputation of the pair shares, cycle counts and list composition
```

Rerunning the models requires [Ollama](https://ollama.com) 0.40.3 with `qwen3:8b`, `qwen3:14b` and `llama3.1:8b`
(model identifiers are listed in `PREREG.md`), followed by `python3 src/run_main.py --config <setup>` (see the
script's documentation). Answers may differ slightly on other hardware.

## Repository contents

| Path | Contents |
|---|---|
| `PLAN.md`, `PREREG.md` | Study plan and pre-registration: hypotheses, exact prompts, scoring, decision rules and deviations |
| `data/processed/events.csv` | The 120 events, with dates and the wording shown to models |
| `data/processed/main_lists.json` | The 240 lists |
| `data/raw/model_runs/main/` | Every model reply, one JSON record per call |
| `data/raw/SOURCES.md` | Every download, with date and license |
| `data/processed/results/` | Results files and tables |
| `figures/` | Figures |
| `src/` | All code |
| `verification/` | Separately written recomputation of the pair shares, cycle counts and list composition |
| `WORKLOG.md` | Record of contributions by date |

## Contributions

**Jayden Ling**
- Chose the research question from candidate ideas and set the core design: 120 events, one per year from 1900 to 2019, each verified
  against two sources; a fixed random-month rule for selecting events; and event wording that does not reveal dates.
- Approved the study plan and every download and model run. The pre-registration was drafted by the AI agent and
  committed before any main-run call; Jayden Ling approved the main runs.
- Decided each change made after pre-registration: adding Llama 3.1 8B as a model from a second developer,
  discarding and repeating a run made under inconsistent settings, omitting the optional gpt-oss 20B setup, and the
  scoring of replies that reached the length limit.
- Checked 10 event dates against the sources.

**AI agent, under Jayden Ling's direction**
- Wrote the code, ran the models, carried out the analysis, and drafted the plan, pre-registration, report and this
  README.

A dated record is kept in [`WORKLOG.md`](WORKLOG.md).

## Sources and licenses

Event information is drawn from English Wikipedia (CC BY-SA 4.0) and Wikidata (CC0); see `data/raw/SOURCES.md`.
Models: Qwen3 (Apache 2.0) and Llama 3.1 (Llama 3.1 Community License). Related work: Wongchamcharoen, P. K., and
Glasserman, P. (2025), "Do Large Language Models (LLMs) Understand Chronology?", https://arxiv.org/abs/2511.14214.

## License

Code: MIT License (see [`LICENSE`](LICENSE)). Report and figures: CC BY 4.0. Data: CC BY-SA 4.0, because several
data files contain or adapt text from English Wikipedia. Details are in [`LICENSE`](LICENSE).

## Citation

```bibtex
@misc{ling2026chronologypairs,
  author       = {Ling, Jayden},
  title        = {Pairwise Temporal Judgments and List Ordering in Small Language Models},
  year         = {2026},
  howpublished = {\url{https://github.com/JLFinance25/chronology-pairs}},
  note         = {Code, analysis and drafting by an AI agent; see the repository README}
}
```
