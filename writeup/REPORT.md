# Chronology Pairs: do small AI models' "which came first?" mistakes explain why they can't sort long lists of events?

**Study directed by Jayden Ling. Code, analysis and write-up by Claude Code (an AI agent), checked by Jayden.**

Draft of October 12, 2026. **Status: written by Claude, not yet read through and approved by Jayden.**

---

## One-page summary

**The question.** AI language models usually say correctly which of two events came first, yet they rarely put a
long list of events in exactly the right order. An earlier paper found this and left the reason open
(Wongchamcharoen and Glasserman, "Do Large Language Models (LLMs) Understand Chronology?", 2025,
https://arxiv.org/abs/2511.14214, abstract opened Oct 12, 2026). This study asks, for small models that run on a home
computer: (1) how far apart in time do two events need to be before a model answers "which came first?" right *and*
the same way when the two are swapped? (2) When a model sorts a list, are its mistakes ones it also makes on those
two events alone, or do they appear only in the list?

**What was done.** 120 real events, one per year from 1900 to 2019, dated from Wikipedia and checked against Wikidata.
Three models with thinking off (Qwen3 8B, Qwen3 14B, Llama 3.1 8B) were asked about all 7,140 pairs of events, each
pair twice with the order swapped, plus "what year did this happen?" for each event. They also sorted 240 lists of 5,
10 or 20 events. Qwen3 8B with thinking on sorted the same 240 lists. Every mistake in a list was traced back to the
model's own answer on that pair. The scoring rules and predictions were fixed in `PREREG.md` before the main runs.

**What we found.** (Ranges are 95% ranges from redrawing events or lists; sources are listed under each table below.)
1. **No model becomes reliable on pairs, even for events decades apart.** For events more than 25 years apart, the
   share of pairs answered right both ways is 68% for Qwen3 8B (range 60% to 75%), 86% for Qwen3 14B (80% to 91%) and
   29% for Llama 3.1 8B (22% to 36%), against the 95% this study set as "reliable". Most errors are *flips*: the
   answer changes when the two events are swapped. The models also lean toward the first option shown: "A" was the
   answer 69% (Qwen3 8B), 54% (Qwen3 14B) and 79% (Llama) of the time.
2. **Steady answers fit one timeline.** When a model gives the same answer both ways for all three pairs in a set of
   three events, those answers almost never go in a circle (A before B, B before C, C before A): 14 circles where
   random placement of the same mistakes would give about 3,281 (Qwen3 8B), 140 vs about 12,424 (Qwen3 14B), and 30 vs
   about 6,015 (Llama). The inconsistency is in the flips, not in circles.
3. **Most list mistakes already show up in the pairs.** Of the side-by-side events a model put in the wrong order,
   the share it got right when asked about that pair alone ("list-only" mistakes) was 19% to 31% for Qwen3 8B, 16% to
   20% for Llama and 35% to 47% for Qwen3 14B, depending on list length. By the pre-registered rules, Qwen3 8B shows
   "a real long-list penalty" (0.80 more wrong neighbors per 20-event list than its pair answers predict, range 0.33
   to 1.28). But that verdict depends on how cut-off replies are read (see Deviations): read the other way, it is
   "in between". Qwen3 14B and Llama are "in between". Separately, long lists often break: only 25% (Qwen3 8B), 50%
   (Qwen3 14B) and 28% (Llama) of 20-event answers listed every event exactly once.
4. **Thinking makes lists much better, but not mainly by removing list-only mistakes.** With thinking on, Qwen3 8B
   got 57% of 5-event lists exactly right (3% with thinking off) and made 5.3 fewer wrong neighbors per 20-event list
   than its thinking-off pair answers predict (range 4.7 to 5.9 fewer). The prediction that thinking would cut
   list-only mistakes more than other mistakes (P6) was **not supported**: the list-only share barely moved (31% to
   24% at 20 events; difference -7 points, range -16 to +2). About half of the mistakes left with thinking on are
   on events whose year the model got wrong when asked directly (52% at 20 events, against 12% with thinking off).

**What it means.** For these small models, the long-list failure is mostly not something new that appears with
length. It is largely the same uncertainty seen on single pairs, mainly answers that change with the order of the
question, plus a separate problem of leaving events out of long lists. Thinking helps a lot, and what it leaves
behind looks more like not knowing the date. For someone using a small model to put events in time order: with
thinking off, do not trust the order of events less than about 25 years apart, and check that nothing was dropped.

**Limits.** Four models and 120 events, all from 1900 to 2019. Llama ran on a different computer (a Windows PC) from
the Qwen models (a Mac). The 20-event results rest on 15 to 33 complete lists per model. One verdict depends on a
scoring choice made after results were seen (reported both ways). The event descriptions were written by an AI.
Details are under "Limits" below.

---

## Full report

### 1. Questions and predictions

The study asks two questions (`PREREG.md` section 1):
- **Q1, date resolution:** the smallest gap in years at which a model answers "which came first?" right both ways for
  at least 95% of pairs, with at most 5% flips, in that gap band and every wider one.
- **Q2, where list mistakes come from:** what share of a model's list mistakes it also makes on the same two events
  alone.

Six predictions were written before the main runs (`PREREG.md` section 2). How each turned out is in section 4.5.

### 2. Methods

**Events.** 120 events, one per year 1900 to 2019. For each year a month was picked at random with a saved seed, and
the first event in that month on the year's English Wikipedia page that happened on one specific day, had a matching
Wikidata date (exact day) and had articles in at least 20 language editions was used (`PLAN.md` decisions 2 and 3,
section 8). Each event was rewritten as a short description with no numbers or order words, so the wording does not
give the answer away. Jayden spot-checked 10 event dates against the sources (all correct, `WORKLOG.md`). Files:
`data/processed/events.csv`; downloads and licenses in `data/raw/SOURCES.md` (Wikipedia text CC BY-SA 4.0; Wikidata
CC0; pages pulled Oct 12, 2026).

**Questions** (exact wording in `PREREG.md` section 4):
- *Pair:* "Which of these two events happened first? A: ... B: ... Answer with only the letter A or B." Every pair is
  asked twice, once in each order: 14,280 questions per model.
- *Year:* "In what year did this event happen? ... Answer with the year only." All 120 events.
- *List:* events shown with random two-letter codes; the model answers with a numbered list of codes. 240 lists:
  lengths 5, 10 and 20, with neighbors in true order 1 to 2, 3 to 5 or 6 to 10 years apart (20 events with 6 to 10
  years is left out). Every model gets the same lists (`data/processed/main_lists.json`).

**Models** (Ollama 0.40.3, run locally, nothing sent online; `PREREG.md` section 3 and Deviations):

| Setup | Model | Machine | Settings |
|---|---|---|---|
| Qwen3 8B | `qwen3:8b` (ID 500a1f067a9f) | Mac (Apple M5 Pro, 24 GB) | thinking off, temperature 0 |
| Qwen3 14B | `qwen3:14b` (ID bdbd181c33f2) | Mac | thinking off, temperature 0 |
| Llama 3.1 8B | `llama3.1:8b` (ID 46e0c10c039e) | Windows PC (RTX 3060 Ti, 8 GB) | no thinking mode, temperature 0 |
| Qwen3 8B, thinking on | `qwen3:8b` | Mac | lists only; temperature 0.6, top_p 0.95, top_k 20 (the model page's thinking settings) |

Each thinking-off model answered 15,170 questions (120 year, 14,280 pair, 240 list, plus 530 repeats to check that
the same question gets the same answer). Raw replies: `data/raw/model_runs/main/<setup>.jsonl`.

**Scoring** (`PREREG.md` section 5):
- Each *pair* is **stable-right** (right both ways), **stable-wrong** (wrong both ways) or a **flip** (the answer changes
  when the order is swapped).
- A *list* is **valid** if its first N entries name each event exactly once. In valid lists, every pair of
  side-by-side events in the wrong order is a **wrong neighbor pair**. A list is exactly right only if it has none, so
  every list mistake can be traced to one pair. Each wrong neighbor pair gets a type from the model's own pair answers:
  **B** (wrong on the pair alone too), **U** (a flip on the pair alone) or **C** (right on the pair alone, so a
  "list-only" mistake). It is also flagged **A, misdated** if the model's own year answers put the two events in that
  wrong order.
- **List penalty:** the model's wrong neighbor pairs minus the number expected if the list were sorted using only its
  pair answers (each event scores a point for every pair question that named it as earlier). Positive means the list
  is worse than the pair answers predict.
- Thinking-on lists are labeled with the thinking-off pair and year answers of the same Qwen3 8B model.

**Error ranges** (`PREREG.md` section 6): pair results from 2,000 redraws of the 120 events; list results from 2,000
redraws of lists within each length and spacing group, which may be too narrow because lists share events. Circles
are compared with 1,000 random reshuffles of each model's steady wrong answers within each gap band.

**Code:** `src/analyze.py` (all pre-registered results), `src/p6.py` (P6), `src/make_figures.py` (charts),
`src/explore_cutoff.py` (an exploratory check, section 5). Written by Claude Code; the analysis code was tested on two
made-up models with known answers before any main data was looked at (`PREREG.md` Deviations, clarification 4).

**Independent check.** A separate AI helper (Claude Sonnet), given only `PREREG.md`, `events.csv` and the raw replies,
and not the analysis code or results, wrote its own scoring code and recomputed the pair shares, first-option lean,
circle counts, valid-list shares and the B/U/C mix of list mistakes for all four setups (Oct 12, 2026). Every one
matched the numbers below. It did not recompute error ranges, the list penalty or the misdated flag. Its script and
output are in `verification/`.

### 3. Results

**Sources for every number below:** `data/processed/results/<setup>.json`, the tables in
`data/processed/results/tables/` (`pairs_by_gap.csv`, `cycles.csv`, `lists_by_length.csv`,
`list_mistakes_by_length.csv`), `data/processed/results/p6_thinking.json` and
`data/processed/results/explore_cutoff_qwen3-8b-nothink.txt`, all made Oct 12, 2026 from the raw replies.

#### 3.1 Pairs: no date resolution for any model (Q1)

Share of pairs answered right both ways, by years between the two events (95% range in brackets):

| Gap (years) | Qwen3 8B | Qwen3 14B | Llama 3.1 8B |
|---|---|---|---|
| 1 | 18% [8 to 32] | 36% [23 to 50] | 19% [8 to 32] |
| 2 | 23% [11 to 36] | 48% [35 to 62] | 19% [8 to 31] |
| 3 to 5 | 25% [18 to 34] | 53% [45 to 63] | 22% [15 to 30] |
| 6 to 10 | 29% [23 to 36] | 56% [48 to 63] | 24% [18 to 31] |
| 11 to 25 | 37% [31 to 43] | 68% [62 to 74] | 26% [21 to 32] |
| more than 25 | 68% [60 to 75] | 86% [80 to 91] | 29% [22 to 36] |
| Flips, more than 25 years | 29% [23 to 36] | 9% [6 to 13] | 59% [51 to 66] |

![Date resolution](../figures/fig1_date_resolution.png)

- **Date resolution: not reached for any model.** No gap band, not even "more than 25 years", reached 95% right both
  ways with at most 5% flips.
- **First-option lean.** Share of all pair answers that were "A": Qwen3 8B 69%, Qwen3 14B 54%, Llama 79%.
- **Year question.** Exact years named, out of 120: Qwen3 8B 87, Qwen3 14B 102, Llama 97.
- Every pair reply from every model was readable (0 unreadable out of 14,280 each).

#### 3.2 Circles among steady answers

Sets of three events where all three pairs were answered the same way both ways, and how many of those go in a circle:

| | Steady triples | Circles seen | Circles expected if the same steady mistakes were placed at random (95% of shuffles) |
|---|---|---|---|
| Qwen3 8B | 66,393 | 14 | 3,281 (3,012 to 3,602) |
| Qwen3 14B | 188,198 | 140 | 12,424 (11,931 to 12,961) |
| Llama 3.1 8B | 27,761 | 30 | 6,015 (5,829 to 6,199) |

None of the 1,000 shuffles came as close to the seen count, for any model (p < 0.001). When these models give a steady
answer, the steady answers line up on a single timeline, even where that timeline is wrong.

#### 3.3 Lists: where the mistakes come from (Q2)

| | Length | Valid lists | Wrong neighbor pairs | B: wrong alone too | U: flip alone | C: list-only [range] | List penalty per list [range] |
|---|---|---|---|---|---|---|---|
| Qwen3 8B | 5 | 100% | 168 | 20% | 61% | 19% [14 to 24] | 0.00 [-0.23 to 0.23] |
| | 10 | 88% | 319 | 16% | 59% | 25% [21 to 30] | -0.06 [-0.34 to 0.22] |
| | 20 | 25% | 141 | 13% | 56% | 31% [25 to 38] | +0.80 [0.33 to 1.28] |
| Qwen3 14B | 5 | 100% | 142 | 41% | 25% | 35% [28 to 41] | -0.04 [-0.23 to 0.14] |
| | 10 | 94% | 338 | 33% | 20% | 47% [42 to 52] | +0.42 [0.13 to 0.70] |
| | 20 | 50% | 270 | 31% | 22% | 47% [42 to 52] | +0.13 [-0.64 to 0.86] |
| Llama 3.1 8B | 5 | 100% | 151 | 19% | 65% | 16% [9 to 23] | -0.32 [-0.53 to -0.09] |
| | 10 | 94% | 332 | 20% | 60% | 20% [16 to 24] | -0.42 [-0.69 to -0.15] |
| | 20 | 28% | 147 | 18% | 64% | 18% [14 to 24] | -0.29 [-1.63 to 1.18] |

![Where list mistakes come from](../figures/fig2_list_mistakes.png)

**Pre-registered verdicts** (`PREREG.md` section 6: "mostly in the pairs" needs list-only at most 20% at every length
and a penalty range including zero; "a real long-list penalty" needs list-only rising to at least 50% at 20 events, or
a penalty range above zero at 20 events; otherwise "in between"):
- **Qwen3 8B: a real long-list penalty**, through the penalty at 20 events (+0.80, range 0.33 to 1.28). The list-only
  share rose (19% to 31%) but stayed under 50%. **This depends on a scoring choice** (section 5): if the 16 lists that
  wrote every event and then hit the reply length limit count as unreadable, the verdict is "in between" (penalty
  +0.50, range 0.00 to 1.00, from only 6 valid 20-event lists).
- **Qwen3 14B: in between.** List-only mistakes are common (35% to 47%), and reach 47% at 20 events, just under the 50%
  line. The penalty is above zero at 10 events (+0.42) but not at 20, which is the length the rule uses.
- **Llama 3.1 8B: in between.** List-only mistakes stay under 20% at every length (19.9% at 10 events only just
  passes), but its penalty is *below* zero at 5 and 10 events: its lists had fewer wrong neighbors than its pair
  answers predict.

**Leaving events out.** Long lists often break before any ordering question arises. Lists of 20 with every event
exactly once: Qwen3 8B 25%, Qwen3 14B 50%, Llama 28% (`lists_by_length.csv`). Every broken 20-event list left at
least one event out.

![List penalty and integrity](../figures/fig3_penalty_and_integrity.png)

#### 3.4 Thinking on (Qwen3 8B, same lists)

| Length | Exactly right, thinking off / on | Valid, off / on | Wrong neighbors per valid list, off / on | List-only share, off / on (difference [range]) | Wrong-alone-too share, off / on (difference [range]) |
|---|---|---|---|---|---|
| 5 | 3% / 57% | 100% / 100% | 1.9 / 0.5 | 19% / 18% (-1 [-13 to +12]) | 20% / 31% (+11 [-1 to +25]) |
| 10 | 0% / 26% | 88% / 94% | 4.0 / 1.2 | 25% / 28% (+3 [-6 to +11]) | 16% / 25% (+9 [+0.4 to +18]) |
| 20 | 0% / 0% | 25% / 55% | 9.4 / 3.0 | 31% / 24% (-7 [-16 to +2]) | 13% / 17% (+4 [-3 to +12]) |

Wrong neighbors per valid list = wrong neighbor pairs divided by the number of valid lists (from
`lists_by_length.csv` and `list_mistakes_by_length.csv`). Differences are in percentage points, thinking on minus off,
with ranges from paired redraws of the same lists (`p6_thinking.json`).

- Thinking on, lists beat what the thinking-off pair answers predict, by 1.4 (5 events), 2.7 (10) and 5.3 (20) wrong
  neighbors per list (ranges 1.2 to 1.5, 2.4 to 2.9 and 4.7 to 5.9).
- **P6 not supported.** Thinking cut every kind of mistake by roughly the same proportion, so the list-only share did
  not fall more than the wrong-alone-too share. At 10 events the wrong-alone-too share actually rose.
- With thinking on, 60%, 49% and 52% of the remaining wrong neighbors (5, 10, 20 events) were on events whose years
  the model had put in that wrong order when asked directly. With thinking off: 19%, 16% and 12%.

#### 3.5 Predictions scorecard

| Prediction | Result |
|---|---|
| P1: Qwen3 8B gets more pairs right both ways as the gap grows; flips are most common at 1 to 2 years | **Mostly supported.** Right both ways rises in every band (18% to 68%). Flips are highest at 1 and 2 years (66%, 63%), but the ranges up to 25 years overlap; the only clear drop is beyond 25 years. |
| P2: Qwen3 14B beats Qwen3 8B in every gap band | **Supported** in all six bands. The ranges overlap at 1 year and barely at 2. |
| P3: circles among steady answers are rarer than chance | **Supported** for all three models (p < 0.001). |
| P4: thinking off, the list-only share grows with length | **Supported** for Qwen3 8B (19% to 31%, non-overlapping ranges); **partly** for Qwen3 14B (rises 5 to 10, flat 10 to 20); **not supported** for Llama (flat). |
| P5: lists break more often as they get longer | **Supported** for every setup (20-event valid share 25% to 55%). |
| P6: thinking cuts list-only mistakes more than wrong-alone-too mistakes | **Not supported.** |

### 4. Deviations and judgment calls

Every change after `PREREG.md` was committed is dated in its "Deviations" section. In short:
1. **Llama 3.1 8B added** (Oct 12, before any of its answers existed), on Jayden's Windows PC, to test whether Qwen3
   results hold for a model from another company.
2. **Llama rerun.** The first Llama attempt ran partly under different PC settings (a memory-saving cache and a
   different attention method) and partly under defaults. Those answers were set aside, unused, and Llama was rerun
   from the start with the PC on Ollama defaults. The rerun crashed once at 13,710 of 14,280 pair questions (a Windows
   network error) and was resumed with the same settings; no question was asked twice.
3. **gpt-oss 20B skipped.** It was optional ("if time allows"). No prediction depends on it.
4. **Cut-off list replies** (decided after the first list results were seen). `PREREG.md` section 3 says a reply that
   hits the length limit is unreadable; section 5 says a list that keeps writing past N is scored on its first N
   entries. Jayden chose the section 5 reading, which the analysis code already used (that code was committed before
   any main data was looked at), knowing that it changes Qwen3 8B's verdict. Both results are reported above.
5. **Analysis fixes, no rule changes:** the circle reshuffles now loop over gap bands in a fixed order, so the
   pre-registered seed gives the same result every run (this moved only Qwen3 8B's expected count, from 3,278 to
   3,281). P6 uses paired redraws because both setups answered the same lists (`src/p6.py`).
6. **Repeat check.** All 530 repeated questions got identical answers for both Qwen3 models. For Llama, all 500 pair
   repeats matched, but only 24 of 30 list repeats did, all differing ones being 20-event lists. Why is not known.
   The analysis scores the first answer, as planned.

### 5. Limits

- **Few models and one kind of event.** Four setups, all small, and 120 well-documented events from 1900 to 2019.
  Bigger models may behave differently.
- **Two computers.** Llama ran on a Windows PC, the Qwen3 models on a Mac, with the same Ollama version and default
  settings. A Llama vs Qwen difference could partly be a machine difference.
- **Small samples for long lists.** The 20-event results rest on 15 (Qwen3 8B), 30 (Qwen3 14B), 17 (Llama) and 33
  (thinking on) valid lists, and the list ranges may be too narrow because lists share events.
- **A verdict that hangs on a scoring choice** made after results were seen (section 4, item 4).
- **The event descriptions were written by an AI** (Claude), with an automatic check for numbers and order words and
  Jayden's spot-check of 10 dates.
- **The list-only share depends on how often a model is right on pairs.** A model that gets more pairs right has more
  chances for "list-only" mistakes, so comparing that share across models needs care (section 6).

### 6. Exploratory observations (not in `PREREG.md`; ideas, not results)

- **Llama hardly uses what it knows on pair questions.** It named the exact year for 97 of 120 events, yet on single
  pair questions more than 25 years apart it was right only 58% of the time (`per_question_accuracy` in
  `llama3.1-8b.json`), not far above the 50% of guessing. A guess: its lean toward "A" drowns out its knowledge.
- **The list-only share tracks pair skill across models.** Right both ways on pairs 1 to 10 years apart vs list-only
  share: Qwen3 8B 18% to 29% vs 19% to 31%; Llama 19% to 24% vs 16% to 20%; Qwen3 14B 36% to 56% vs 35% to 47%. So a
  higher list-only share may mostly mean a model that gets more pairs right.

### 7. How to reproduce

See `README.md`. Every result above can be remade from the saved raw replies without running any model:
`python3 src/analyze.py`, `python3 src/p6.py`, `python3 src/make_figures.py`.

### 8. Sources

- Wongchamcharoen, P. K., and Glasserman, P. (2025). "Do Large Language Models (LLMs) Understand Chronology?"
  arXiv:2511.14214. https://arxiv.org/abs/2511.14214 (abstract opened Oct 12, 2026).
- English Wikipedia year pages 1900 to 2019 (CC BY-SA 4.0) and Wikidata (CC0), pulled Oct 12, 2026; details and
  revision IDs in `data/raw/SOURCES.md`.
- Models: Qwen3 (Apache 2.0) and Llama 3.1 (Llama 3.1 Community License), via Ollama 0.40.3; licenses as recorded
  in `PREREG.md` section 3 and Deviations (opened Oct 12, 2026).
