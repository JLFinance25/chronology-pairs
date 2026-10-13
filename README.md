# Chronology Pairs

**Study directed by Jayden Ling. Code, analysis and write-up by Claude Code (an AI agent), checked by Jayden.**

AI language models can usually say which of two events came first, yet they rarely put a long list of events in
exactly the right order. This study asks, for small models that run on a home computer: are the mistakes in long
lists ones the model already makes on two events at a time, or do they appear only when the list gets long?

**Report:** [`writeup/REPORT.md`](writeup/REPORT.md), with a one-page summary at the top.

## In short

- 120 real events (one per year, 1900 to 2019, from Wikipedia, checked against Wikidata). Four setups: Qwen3 8B,
  Qwen3 14B and Llama 3.1 8B with thinking off, and Qwen3 8B with thinking on.
- Every pair of events was asked about twice, once in each order (14,280 questions per model), and each model sorted
  the same 240 lists of 5, 10 or 20 events. Every mistake in a list is traced back to the model's own answer on that
  pair.
- No model became reliable on pairs, even for events more than 25 years apart (68%, 86% and 29% right both ways,
  against a 95% bar). Most list mistakes were already uncertain or wrong on the pair alone. Thinking made lists much
  better, but did not mainly remove "list-only" mistakes.
- The rules and predictions were pre-registered in [`PREREG.md`](PREREG.md) before the main runs. Every later change is
  dated in its "Deviations" section.
- Answers are scored against verified dates by code. No AI grades another AI's answers.

## Reproduce the results

The raw model replies are saved, so every number and chart can be remade without running a model.

```
pip install numpy matplotlib
python3 src/analyze.py           # pre-registered analysis -> data/processed/results/
python3 src/p6.py                # thinking on vs off (prediction P6)
python3 src/make_figures.py      # charts -> figures/
python3 -I verification/independent_check.py   # separate re-check of the headline numbers
```

To rerun the models themselves you need [Ollama](https://ollama.com) 0.40.3 with `qwen3:8b`, `qwen3:14b` and
`llama3.1:8b` (model IDs in `PREREG.md`), then `python3 src/run_main.py --config <setup>` (see its docstring).
Answers can differ slightly on other hardware.

## What's where

| Path | What |
|---|---|
| `PLAN.md`, `PREREG.md` | The plan and the pre-registration (hypotheses, exact prompts, scoring, decision rules, deviations) |
| `data/processed/events.csv` | The 120 events with dates and the wording shown to models |
| `data/processed/main_lists.json` | The 240 lists |
| `data/raw/model_runs/main/` | Every model reply, one JSON line per call |
| `data/raw/SOURCES.md` | Every download, with date and license |
| `data/processed/results/` | Results files and tables |
| `figures/` | Charts |
| `src/` | All code |
| `verification/` | An independent re-check of the headline numbers |
| `WORKLOG.md` | Who did what, by date |

## Credits and licenses

Event information comes from English Wikipedia (CC BY-SA 4.0) and Wikidata (CC0); see `data/raw/SOURCES.md`. Models:
Qwen3 (Apache 2.0) and Llama 3.1 (Llama 3.1 Community License). Prior work: Wongchamcharoen and Glasserman, "Do Large
Language Models (LLMs) Understand Chronology?" (2025), https://arxiv.org/abs/2511.14214.
