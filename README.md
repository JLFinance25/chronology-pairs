# Pairwise Temporal Judgments and List Ordering in Small Language Models

**Study directed by Jayden Ling. Code, analysis and write-up by Claude Code (an AI agent), checked by Jayden.**

Language models usually identify correctly which of two events occurred first, yet they rarely place a long list of
events in exactly the correct order. This study examines small models that run on consumer hardware and asks whether
their errors on long lists are already present in their judgments about pairs of events, or arise only when lists
become long.

**Report:** [`writeup/REPORT.md`](writeup/REPORT.md), beginning with a one-page summary.

## Overview

- **Data.** 120 historical events, one per year from 1900 to 2019, drawn from Wikipedia and verified against
  Wikidata.
- **Models.** Four setups: Qwen3 8B, Qwen3 14B and Llama 3.1 8B with reasoning disabled, and Qwen3 8B with reasoning
  enabled.
- **Design.** Each pair of events was presented twice, once in each order (14,280 questions per model), and each
  model ordered the same 240 lists of 5, 10 or 20 events. Every error in a list is traced to the model's own answer
  on the corresponding pair.
- **Principal results.** No model reached a reliable "date resolution": for events more than 25 years apart, the
  share of pairs answered correctly in both orders was 68%, 86% and 29%, against a pre-registered threshold of 95%.
  Most list errors were already uncertain or incorrect at the pair level. Reasoning improved list ordering
  substantially but did not specifically reduce errors that occur only within lists.
- **Pre-registration.** The hypotheses, prompts and decision rules were fixed in [`PREREG.md`](PREREG.md) before the
  main data were collected. All later changes are dated in its Deviations section.
- **Scoring.** Answers are scored against verified dates by deterministic code; no AI system grades another's
  answers. The headline numbers were independently recomputed from the raw replies (`verification/`).

## Reproducing the results

The raw model replies are included, so every result and figure can be regenerated without running a model:

```
pip install numpy matplotlib
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

## Sources and licenses

Event information is drawn from English Wikipedia (CC BY-SA 4.0) and Wikidata (CC0); see `data/raw/SOURCES.md`.
Models: Qwen3 (Apache 2.0) and Llama 3.1 (Llama 3.1 Community License). Related work: Wongchamcharoen, P. K., and
Glasserman, P. (2025), "Do Large Language Models (LLMs) Understand Chronology?", https://arxiv.org/abs/2511.14214.
