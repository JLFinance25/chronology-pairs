# Pre-registration: Chronology Pairs

**Date:** October 12, 2026. Written after the pilot and **before any main-run model call**.
**Credit:** Study directed by Jayden Ling. Code, analysis and write-up by Claude Code (an AI agent), checked by Jayden.
**Status:** fixed once committed. Any later change goes in the dated "Deviations" section at the end, never as a quiet edit.

Pilot data (`data/raw/model_runs/pilot/`) is used only for planning and never in the results. The predictions below were written after seeing the pilot, which is summarized in section 9.

---

## 1. Questions

Small AI models usually answer "which came first?" correctly for two events, yet rarely put a long list of events in exactly the right order (Wongchamcharoen and Glasserman, 2025, https://arxiv.org/abs/2511.14214, to be re-opened before citing).

- **Q1, date resolution.** How many years apart must two events be before a model answers "which came first?" correctly and consistently (the same answer with the events swapped, and no circles such as A before B, B before C, C before A)?
- **Q2, where list mistakes come from.** When a model sorts a list, what share of its mistakes does it also make on those two events alone, and what share appear only in the list?

## 2. Predictions

These are guesses. All tests are two-sided, and every outcome is reported.

- **P1.** For Qwen3 8B with thinking off, the share of stable-right pairs (defined in section 5) rises with the year gap. Flips are most common at gaps of 1 to 2 years.
- **P2.** Qwen3 14B has a higher stable-right share than Qwen3 8B in every gap band.
- **P3.** Among triples whose three pairs are all stable, circular triples are rarer than in the shuffle baseline (section 6). That would mean the mistakes fit a consistent but blurry timeline.
- **P4.** For models with thinking off, list-only mistakes (type C) make up a larger share of wrong neighbor pairs as lists get longer.
- **P5.** Integrity failures (an event left out, repeated or invented within the answer) become more common as lists get longer, for every setup.
- **P6.** Turning thinking on (same Qwen3 8B weights) lowers the share of type C mistakes more than it lowers type B.

## 3. Materials (fixed)

**Events**
- `data/processed/events.csv`: 120 events, one per year from 1900 to 2019. How they were chosen and checked is in `PLAN.md` decisions 2 and 3, and section 8.
- SHA-256 of the file: `eb78b0b86008f725414b777716217e43abda9548be791dc81b2eaddf17eee16b`.
- Fingerprint of year plus wording: `09b8fb5d6f705c0c1ea957cb4a53e52836787a6f5e8c6aca4d5e2ebb6c5f4916`.

**Lists**
- `data/processed/main_lists.json`: 240 lists, seed 20261013, made by `src/make_main_lists.py`.
- SHA-256: `d9726ba6815816b3951640d9f3b62427bf409e4b8156f3fda27f446b66612a3b`.
- Lengths 5, 10 and 20, crossed with the gap between neighboring events in true order: tight (1 to 2 years), medium (3 to 5) and wide (6 to 10). Length 20 with wide gaps is left out. That makes 8 cells of 30 lists each. Every model gets the same lists.

**Models** (Ollama 0.40.3 on an Apple M5 Pro Mac with 24 GB of memory; local, nothing sent online)

| Setup | Model (Ollama ID) | Thinking | Settings |
|---|---|---|---|
| `qwen3-8b-nothink` | qwen3:8b (`500a1f067a9f`, Q4_K_M) | off | temperature 0, seed 0 |
| `qwen3-14b-nothink` | qwen3:14b (`bdbd181c33f2`, Q4_K_M) | off | temperature 0, seed 0 |
| `qwen3-8b-think` | qwen3:8b | on | temperature 0.6, top_p 0.95, top_k 20, min_p 0, seed 0 (the model page's thinking settings; it advises against greedy decoding with thinking on) |
| `gpt-oss-20b-low` (optional, run last if time allows) | gpt-oss:20b (`17052f91a42e`, MXFP4) | reasoning "low" (it cannot be turned off) | temperature 0, seed 0 |

Both model families are Apache 2.0 (model pages, opened Oct 12, 2026). The reply length limits are in `src/llm.py`. A reply cut off at the limit counts as unreadable.

## 4. Questions asked (exact wording)

**Pair** (wording A). Every ordered pair of the 120 events is asked once, so each of the 7,140 pairs is asked twice, with the events swapped: 14,280 calls per setup. The calls run in a fixed shuffled order (seed 31).
```
Which of these two events happened first?
A: {event}
B: {event}
Answer with only the letter A or B.
```

**Year**, all 120 events, for each thinking-off setup and gpt-oss:
```
In what year did this event happen?
{event}
Answer with the year only.
```

**List** (format D). Each event gets a random two-letter code. The codes use no vowels and no Roman-numeral letters, so they don't spell words or suggest an order.
```
Put these events in chronological order, from earliest to latest.

{code}: {event}
...

Answer with a numbered list of the codes only, one per line, earliest first, like this:
1. XX
2. XX
```

**Who answers what**
- Thinking-off setups and gpt-oss answer the year, pair and list questions.
- `qwen3-8b-think` answers the list questions only. Its list mistakes are compared with the thinking-off pair answers and year answers of the same Qwen3 8B weights.

**Repeat check:** 500 randomly chosen pair calls and 30 lists are asked a second time (seed 32), to check that temperature 0 gives the same answer twice.

## 5. Scoring

**Reading replies**
- A pair reply counts if it reads as the single letter A or B. Otherwise it is unreadable.
- A year reply counts if it contains a four-digit year (the first one is used).
- A list reply is read from its first N numbered entries, where N is the list length. If the model keeps writing past N, that is recorded as "didn't stop" and doesn't count against it.

**Each pair**, from its two answers:
- **stable-right:** right both ways.
- **stable-wrong:** wrong both ways.
- **flip:** the answer changes when the events are swapped.
- **unreadable:** if either reply can't be read. These pairs are counted and left out of the shares.

**Gap bands** (pairs per band): 1 year (119), 2 (118), 3 to 5 (348), 6 to 10 (560), 11 to 25 (1,530), more than 25 (4,465).

**Date resolution:** the smallest gap band where that band and every wider band have at least 95% stable-right and at most 5% flips. If no band qualifies, the result is "not reached," and the full curve is still reported.

**Position bias:** the share of all readable pair replies that are "A."

**List integrity:** a list is valid if its first N entries are N different codes from the list, with none invented. For invalid lists, the counts of missing, repeated and invented codes are reported.

**Wrong neighbor pairs:** in a valid list, two consecutive entries where the first event actually happened later. A list is exactly right if and only if it has none. Each wrong neighbor pair is labeled from the same model's pair answers for those two events:
- **B, wrong alone too:** stable-wrong.
- **U, unsure alone:** flip.
- **C, list-only:** stable-right.
- **X:** unreadable pair.

Separately, each one is flagged **A, misdated** if the model's own year answers put the two events in the list's (wrong) order or give them the same year.

**Pair-based prediction (win counting):**
- For each list, its events are also ordered using only the model's saved pair answers. Each event scores one point for every pair question that named it as earlier, out of 2(N-1) questions.
- Events are ranked by score, highest first. Ties are broken at random (seed 33).
- The wrong neighbor pairs in that order are the prediction. **List penalty** = observed wrong neighbor pairs minus predicted, for each valid list.

**Also reported:** exact match (the share of all lists that are perfectly right), and Kendall tau (a score from -1 to 1 for how close an order is to the true order) for valid lists.

## 6. Analysis

**Error ranges**
- Pair results get 95% ranges from 2,000 redraws of the 120 events with replacement (pairs of an event with its own copy are skipped).
- List results get 95% ranges from 2,000 redraws of lists within each cell. Lists share events, so these ranges may be too narrow, and the write-up will say so.

**Circular triples**
- Only triples whose three pairs are all stable count. A triple (x, y, z) in true order is circular when its labels for (xy, yz, xz) are right, right, wrong, or wrong, wrong, right.
- **Baseline:** 1,000 shuffles. Each shuffle randomly reassigns the stable-wrong labels among the stable pairs within each gap band, keeping each band's count, and then recounts circular triples.
- **p-value:** the share of shuffles at least as far from the shuffle mean as the real count.
- This runs once on the full data, not inside the error-range redraws.

**Decision rules for Q2** (fixed in PLAN.md section 5), applied to each setup. The headline setup is `qwen3-8b-nothink`.
- **"The collapse is mostly in the pairs"** if type C is at most 20% of wrong neighbor pairs at every length, and the list penalty's 95% range includes zero.
- **"A real long-list penalty"** if type C rises with length and is at least 50% at length 20, or if the list penalty's 95% range is above zero at length 20.
- Otherwise: **"in between."** Integrity failures are always reported on their own.

**P6:** the type C share for `qwen3-8b-think` minus the type C share for `qwen3-8b-nothink`, at each length, with redraw ranges. The same is done for type B.

**Secondary analysis** (also fixed now): all lists, including invalid ones. Each code's first appearance within the first N entries is used, missing codes are skipped, and the same wrong-neighbor labels apply.

**Exploratory (labeled as such in the write-up):**
- the probability the model gave its answer (logprobs) vs the year gap;
- position bias by gap;
- the list's middle year as a possible era effect;
- the year question's accuracy by decade.

## 7. Running rules

- Every model call is saved as it happens (`data/raw/model_runs/main/<setup>.jsonl`). An interrupted run resumes and never repeats a finished call, except for the pre-registered repeat check.
- **Order:** `qwen3-8b-nothink`, then `qwen3-14b-nothink`, then `qwen3-8b-think`, then `gpt-oss-20b-low` if time allows. Jayden approves the start of each run.
- If a model file changes during the study (a different Ollama ID), the run stops and a deviation is logged.

## 8. Analysis code

The analysis script will be written while the runs go. It must follow this document. Anything it does that isn't described here is labeled exploratory.

## 9. What the pilot showed (planning only)

The pilot used 25 random events (seed 2026) and 854 calls, plus two short follow-ups with 52 calls.
- **Pair questions:** 0 unreadable out of 725 replies. Repeat calls at temperature 0 were identical (29 of 29). Wordings A and B agreed on 92 of 100 answers, so A was kept. About a third of the 300 pilot pairs flipped when swapped, and 66% of answers were "A."
- **Year question:** Qwen3 8B gave the exact year for 20 of 25 events, so the notability-floor stop rule was not triggered.
- **List format:**
  - With the planned codes-only, comma-separated answer, Qwen3 8B with thinking off produced near-random orders, even for 5 events (Kendall tau about 0). On 20 events it fell into endless repetition.
  - A numbered answer (format D) and a rewrite-the-lines answer (format C) both gave orders well above chance (tau about 0.4 to 0.7).
  - Format D was chosen because it is faster and marks where the answer ends. The model often keeps numbering past N, so only the first N entries are scored.
- **No collapse to explain?** No pilot setup got a 20-event list exactly right, so that stop rule was not triggered.
- **Time:** Qwen3 8B takes about 0.12 s per pair question with thinking off. Projected main-run time is about 1 hour (Qwen3 8B, thinking off), 1 hour (Qwen3 14B), 4 hours (Qwen3 8B, thinking on, lists only) and 5 hours (gpt-oss).

## Deviations

- **Oct 12, 2026, clarifications only.** Written while the main runs were in progress, before any main-run data was analyzed or looked at. They pin down wording that was ambiguous, and change no rule.
  1. "Type C rises with length" means the type C share at length 20 is higher than at length 5.
  2. "The list penalty's 95% range includes zero" (the "mostly in the pairs" rule) must hold at every length: 5, 10 and 20.
  3. Seeds for the analysis: 41 for the error-range redraws, 42 for the cycle shuffles, and 33 for the win-counting tie-breaks (combined with the setup and list ID).
  4. The analysis code (`src/analyze.py`) was tested on two made-up models with known answers before use: a consistent but blurry timeline, and random lists.
- **Oct 12, 2026, 20:07 UTC, an added setup, recorded before any of its answers existed.**
  - **What:** the setup `llama3.1-8b` was added, Jayden's OK given in chat. Model: Llama 3.1 8B (`llama3.1:8b`, Ollama ID `46e0c10c039e`, Q4_K_M), Meta, Llama 3.1 Community License. It has no thinking mode. Settings: temperature 0, seed 0, the same reply limits as the other thinking-off setups.
  - **Hardware:** Jayden's Windows PC (RTX 3060 Ti, 8 GB), same Ollama version (0.40.3), reached from the Mac over an SSH tunnel. The questions, prompts, lists, seeds, repeat check and the whole analysis are identical to the Qwen3 thinking-off setups.
  - **Why it was added:** to test whether results seen for Qwen3 8B also hold for a model from a different company. The main one is the strong preference for the first-listed option.
  - **Effect on the other setups:** none. They, the analysis and the decision rules are unchanged.
- **Oct 12, 2026, about 21:10 UTC, Llama rerun and gpt-oss skipped, both decided by Jayden in chat before any Llama or gpt-oss answers were analyzed or looked at.**
  - **Llama rerun:** the first `llama3.1-8b` attempt (8,874 calls: 120 year and 8,754 pair questions) mixed two PC Ollama setups: the year calls and 7,998 pair calls ran with flash attention on, a q8_0 key-value cache and a default context of 8192, and 756 pair calls ran on Ollama defaults after the PC was switched to match the Mac for a speed test. Since these settings can change answers slightly, that file is set aside, unused, as `data/raw/model_runs/main/llama3.1-8b.mixed-settings.jsonl`, and `llama3.1-8b` was rerun from the start with the PC on Ollama defaults (no OLLAMA_* tuning variables, the same as the Mac). Same model ID, questions, settings and seeds.
  - **gpt-oss skipped:** `gpt-oss-20b-low` was optional in section 3 ("run last if time allows"). It is not run: it would take about 5 hours on the Mac, and its role as a check on a different company's model is now covered by Llama 3.1 8B. P1 to P6 do not depend on it.
  - **Effect on the other setups:** none.
