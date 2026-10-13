# Pairwise Temporal Judgments and List Ordering in Small Language Models

**Jayden Ling** · [Report](writeup/REPORT.md) · [Pre-registration](PREREG.md) · [Data](data/) · [Code](src/)

Designed and directed by Jayden Ling, who selected the research question, set the event-selection and wording
rules, and made the study's decisions, including each change after pre-registration. Code, analysis and drafting by
Claude Code (an AI agent) under his direction. See [Contributions](#contributions).

Language models usually identify correctly which of two events occurred first, yet they rarely place a long list of
events in exactly the correct order. This study examines small models that run on consumer hardware and asks whether
their errors on long lists are already present in their judgments about pairs of events, or arise only when lists
become long.

![Date resolution](figures/fig1_date_resolution.png)

## Principal results

| | Qwen3 8B | Qwen3 14B | Llama 3.1 8B |
|---|---|---|---|
| Pairs more than 25 years apart answered correctly in both orders (pre-registered threshold: 95%) | 68% | 86% | 29% |
| Pair answers that chose the first option presented | 69% | 54% | 79% |
| Exact year given, out of 120 events | 87 | 102 | 97 |
| List errors that occur only within lists, by list length | 19% to 31% | 35% to 47% | 16% to 20% |
| 20-event answers containing every event exactly once | 25% | 50% | 28% |

All three models were run with reasoning disabled. Sources and 95% intervals are given in
[`writeup/REPORT.md`](writeup/REPORT.md), section 3.

- **No model reached a reliable "date resolution".** No gap between events, including more than 25 years, met the
  pre-registered threshold.
- **Most list errors were already uncertain or incorrect at the pair level.**
- **Reasoning improved list ordering substantially** (Qwen3 8B ordered 57% of 5-event lists exactly with reasoning
  enabled, against 3% with it disabled) but did not specifically reduce errors that occur only within lists.

## Overview

- **Data.** 120 historical events, one per year from 1900 to 2019, drawn from Wikipedia and verified against
  Wikidata.
- **Models.** Four setups: Qwen3 8B, Qwen3 14B and Llama 3.1 8B with reasoning disabled, and Qwen3 8B with reasoning
  enabled.
- **Design.** Each pair of events was presented twice, once in each order (14,280 questions per model), and each
  model ordered the same 240 lists of 5, 10 or 20 events. Every error in a list is traced to the model's own answer
  on the corresponding pair.
- **Pre-registration.** The hypotheses, prompts and decision rules were fixed in [`PREREG.md`](PREREG.md) before the
  main data were collected. All later changes are dated in its Deviations section.
- **Scoring.** Answers are scored against verified dates by deterministic code; no AI system grades another's
  answers. The headline numbers were independently recomputed from the raw replies (`verification/`).

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
python3 src/make_figures.py                    # figures -> figures/
python3 -I verification/independent_check.py   # independent recomputation of the headline numbers
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
| `verification/` | Independent recomputation of the headline numbers |
| `WORKLOG.md` | Record of contributions by date |

## Contributions

**Jayden Ling**
- Selected the research question and set the core design: 120 events, one per year from 1900 to 2019, each verified
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
