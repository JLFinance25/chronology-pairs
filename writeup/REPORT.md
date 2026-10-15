# Pairwise Temporal Judgments and List Ordering in Small Language Models

**Directed by Jayden Ling, who chose the research question from candidate ideas, set the core design (event rules, selection and wording), approved the plan, the pre-registration and every run, and made each later decision. Code, analysis and drafting by Claude Code (an AI agent) under his direction.**

Report dated October 12, 2026. Exploratory analyses (section 7) added and the report checked by Jayden Ling on
October 13, 2026. Wording corrected on October 15, 2026 following a review of the study; no result,
data or code logic changed.

---

## Summary

**Question.** Large language models largely preserve the local order of events, yet they rarely place a long list of
events in exactly the correct order. Wongchamcharoen and Glasserman (2025) documented this pattern for large models and
did not establish a cause; they describe the models as struggling to maintain a single globally consistent timeline.
This study examines small models that run on consumer hardware. These models often do not answer "which came first?"
reliably even for pairs of events (section 3.1). The study asks two questions. First,
how far apart in time must two events be before a model answers "which came first?" correctly and consistently,
giving the same answer when the order of presentation is reversed? Second, when a model orders a list, are its
errors ones it also makes when asked about the same two events in isolation, or do they arise only within the list?

**Method.** The study used 120 historical events, one per year from 1900 to 2019, dated from Wikipedia and verified
against Wikidata. Three models with reasoning ("thinking") disabled (Qwen3 8B, Qwen3 14B and Llama 3.1 8B) were asked
about all 7,140 pairs of events, each pair twice in opposite orders, and were asked for the year of each event. Each
model also ordered the same 240 lists of 5, 10 or 20 events. Qwen3 8B with thinking enabled ordered the same 240
lists. Every error in a list was traced to the model's own answer on the corresponding pair. The scoring rules and
predictions were committed to this project's git repository in `PREREG.md` before the main data were collected (the
only timestamps are those of the git history; there is no external registry).

**Principal findings.** Ranges are 95% intervals from resampling events or lists; sources are given in section 3.
1. **No model reached a reliable date resolution.** For events more than 25 years apart, the share of pairs answered
   correctly in both orders was 68% for Qwen3 8B (interval 60% to 75%), 86% for Qwen3 14B (80% to 91%) and 29% for
   Llama 3.1 8B (22% to 36%), against the pre-registered threshold of 95%. For Qwen3 8B and Llama 3.1 8B at every
   gap, and for Qwen3 14B at gaps above 10 years, most errors were reversals: the answer changed when the order of the
   two events was swapped (`pairs_by_gap.csv`). For Qwen3 14B at gaps up to 10 years, answers that were wrong in both
   orders were about as frequent as reversals or more frequent. The models also favored the first option presented, which
   was chosen in 69% (Qwen3 8B), 54% (Qwen3 14B) and 79% (Llama 3.1 8B) of answers.
2. **Consistent answers form a single timeline.** Among sets of three events for which all three pairs received
   consistent answers, cyclic judgments (A before B, B before C, C before A) were almost absent: 14 cycles against
   about 3,281 expected under random placement of the same errors (Qwen3 8B), 140 against about 12,424 (Qwen3 14B),
   and 30 against about 6,015 (Llama 3.1 8B). The inconsistency lies in order-dependent reversals, not in cycles.
3. **Origin of list errors: pre-registered verdicts differ by model.** Under the pre-registered decision rules,
   Qwen3 8B shows "a real long-list penalty" (0.80 more adjacent errors per 20-event list than its pair answers
   predict, interval 0.33 to 1.28). This verdict depends on how replies that reached the length limit are scored
   (section 4) and on random tie-breaking in the prediction (section 3.3); under the alternative scoring reading it is
   "in between". Qwen3 14B, Llama 3.1 8B and Qwen3 8B with thinking enabled are classified "in between". Among adjacent
   events placed in the wrong order, the share that the model had answered correctly in both orders when asked about
   the pair alone ("list-only" errors) was 19% to 31% for Qwen3 8B, 16% to 20% for Llama 3.1 8B and 35% to 47% for
   Qwen3 14B, depending on list length; the remaining errors fell on pairs the model had also answered incorrectly or
   inconsistently. Because such pairs are common among close events (section 3.1), this does not by itself show that
   list errors arise from pair errors. An exploratory re-analysis that removes the models' preference for the first
   option (section 7) weakens the pair-level account: about half of adjacent list errors (40% to 53%) then coincide
   with an incorrect pair judgment. Separately, long lists were frequently incomplete: only 25% (Qwen3 8B),
   50% (Qwen3 14B) and 28% (Llama 3.1 8B) of 20-event answers contained every event exactly once.
4. **Reasoning improves list ordering substantially; whether it specifically removes list-only errors was not
   established.** With thinking enabled (using the model card's recommended settings, which also changed the sampling
   temperature, context size and reply length limit; section 5), Qwen3 8B ordered 57% of 5-event lists exactly (3% with
   thinking disabled) and made 5.3 fewer adjacent errors per 20-event list than its thinking-disabled pair answers
   predict (interval 4.7 to 5.9). The prediction that reasoning would reduce list-only errors more than other errors
   (P6) was not established. At every list length the list-only share fell more, or rose less, than the
   incorrect-on-pair share, the direction P6 predicted (section 3.4). The pre-registration set no test for P6, and the
   change in the list-only share alone is not distinguishable from zero at any length (31% to 24% at 20 events;
   difference -7 percentage points, interval -16 to +2). With thinking enabled, 52% of the remaining adjacent errors at
   20 events involved events whose years the model had placed in the same wrong order when asked directly, compared
   with 12% with thinking disabled.

**Interpretation.** For these small models, the pre-registered verdicts on the origin of list errors are mixed: a
long-list penalty for Qwen3 8B (a tentative verdict; section 3.3) and "in between" for the other setups. At 5 and 10
events, Qwen3 8B's list errors were about as frequent as its pair answers predict (the penalty intervals include
zero), with some sign of extra errors at 20 events. Qwen3 14B showed extra errors at 10 events but not at 20, and Llama
3.1 8B's lists contained fewer adjacent errors than its pair answers predict at 5 and 10 events. Most adjacent list
errors fell on pairs that the model had also answered incorrectly or inconsistently (for Qwen3 8B and Llama 3.1 8B,
chiefly answers that depended on the order of presentation), but such pairs are common among close events, so this does
not show that list errors arise from pair errors. Long lists also frequently omitted events. An exploratory
re-analysis qualifies the pair-level account: for the Qwen3 models, most order-dependent answers reflect a preference
for the first option presented rather than an absence of judgment (for Llama 3.1 8B, few reversals are clearly decided;
section 7.1), and once that preference is removed, list errors and pair errors overlap only in part (section 7).
Reasoning reduces errors considerably, and the errors that remain are more often attributable to incorrect knowledge
of dates. For practitioners using small models to order events, the results suggest that, without reasoning, none of
the gaps tested was reliable: reliability was lowest for events less than about 25 years apart, and even beyond 25
years only 68% (Qwen3 8B), 86% (Qwen3 14B) and 29% (Llama 3.1 8B) of pairs were answered correctly in both orders.
Outputs should also be checked for omitted items.

**Limitations.** Four model setups and 120 events from a single period (1900 to 2019). Llama 3.1 8B was run on
different hardware (a Windows PC) from the Qwen3 models (a Mac). The 20-event results rest on 15 to 33 complete lists
per setup. One verdict depends on a scoring decision made after results were seen and on random tie-breaking; both scoring
outcomes are reported. The comparison with reasoning enabled also changed sampling settings. The event descriptions
were written by an AI system. Details are given in section 5.

---

## Full report

### 1. Research questions and predictions

The study addresses two questions (`PREREG.md` section 1):
- **Q1, date resolution:** the smallest gap in years at which a model answers "which came first?" correctly in both
  orders for at least 95% of pairs, with at most 5% reversals, in that gap band and every wider band.
- **Q2, origin of list errors:** the share of a model's list errors that it also makes on the same two events in
  isolation.

Six predictions were registered before the main runs (`PREREG.md` section 2). Their outcomes are summarized in
section 3.5.

### 2. Methods

**Events.** The study used 120 events, one per year from 1900 to 2019. For each year a month was drawn at random with
a recorded seed, and the first event in that month on the year's English Wikipedia page was selected if it occurred
on a single identifiable day, matched a Wikidata date to the day, and had articles in at least 20 language editions
(`PLAN.md` decisions 2 and 3 and section 8). Each event was rewritten as a short description containing no numbers
or ordering words, so that the wording does not reveal the answer. Jayden Ling verified 10 event dates against the
sources (all correct). Files: `data/processed/events.csv`; downloads and licenses are recorded in
`data/raw/SOURCES.md` (Wikipedia text under CC BY-SA 4.0, Wikidata under CC0, retrieved October 12, 2026).

**Questions** (exact wording in `PREREG.md` section 4):
- *Pair:* "Which of these two events happened first? A: ... B: ... Answer with only the letter A or B." Each pair was
  asked in both orders, giving 14,280 questions per model.
- *Year:* "In what year did this event happen? ... Answer with the year only." All 120 events.
- *List:* events were shown with random two-letter codes, and the model answered with a numbered list of codes. There
  were 240 lists of 5, 10 and 20 events, with adjacent events (in true order) 1 to 2, 3 to 5 or 6 to 10 years apart;
  the combination of 20 events and 6 to 10 years was excluded. All models received the same lists
  (`data/processed/main_lists.json`).

**Models** (Ollama 0.40.3, run locally with no data sent to external services; `PREREG.md` section 3 and
Deviations):

| Setup | Model | Hardware | Settings |
|---|---|---|---|
| Qwen3 8B | `qwen3:8b` (ID 500a1f067a9f) | Mac (Apple M5 Pro, 24 GB) | thinking disabled, temperature 0 |
| Qwen3 14B | `qwen3:14b` (ID bdbd181c33f2) | Mac | thinking disabled, temperature 0 |
| Llama 3.1 8B | `llama3.1:8b` (ID 46e0c10c039e) | Windows PC (RTX 3060 Ti, 8 GB) | no thinking mode, temperature 0 |
| Qwen3 8B, thinking enabled | `qwen3:8b` | Mac | lists only; temperature 0.6, top_p 0.95, top_k 20 (the model card's recommended settings) |

Each thinking-disabled model answered 15,170 questions: 120 year questions, 14,280 pair questions, 240 lists, and 530
repeated questions used to confirm that identical questions receive identical answers. Raw replies are stored in
`data/raw/model_runs/main/<setup>.jsonl`.

**Scoring** (`PREREG.md` section 5):
- Each *pair* is classified as **stable-right** (correct in both orders), **stable-wrong** (incorrect in both orders)
  or a **reversal** (the answer changes when the order is swapped; called a "flip" in `PREREG.md`).
- A *list* is **valid** if its first N entries name each event exactly once. In a valid list, each pair of adjacent
  events in the wrong order is an **adjacent error** ("wrong neighbor pair" in `PREREG.md`). A list is exactly correct
  if and only if it contains no adjacent errors, so every list error can be traced to a single pair. Each adjacent
  error is classified from the model's own pair answers as **B** (stable-wrong on the pair alone), **U** (a reversal on
  the pair alone) or **C** (stable-right on the pair alone, a "list-only" error). It is additionally flagged
  **A, misdated** if the model's own year answers place the two events in that wrong order.
- **List penalty:** the number of adjacent errors minus the number expected if the list were ordered using only the
  model's pair answers (each event receives one point for every pair question in which it was named as earlier). A
  positive value means the list is worse than the pair answers predict.
- Lists produced with thinking enabled are classified using the thinking-disabled pair and year answers of the same
  Qwen3 8B model.

**Uncertainty** (`PREREG.md` section 6): intervals for pair results come from 2,000 resamples of the 120 events, and
intervals for list results from 2,000 resamples of lists within each length and spacing group. The latter may be too
narrow because lists share events. Cycle counts are compared with 1,000 random reassignments of each model's
stable-wrong answers within each gap band.

**Code.** `src/analyze.py` (all pre-registered results), `src/p6.py` (prediction P6), `src/make_figures.py` (figures)
and `src/explore_cutoff.py` (an exploratory comparison, section 4). The code was written by the AI agent. The analysis
code was tested on two simulated models with known answers before any main data were examined (`PREREG.md`
Deviations, clarification 4); that test code was not kept, so this check cannot be rerun from the repository.

**Independent verification.** A separate AI system (Claude Sonnet), given only `PREREG.md`, the event list and the raw
replies, and without access to the analysis code or results, implemented its own scoring and recomputed the pair
shares, first-option rates, cycle counts, valid-list shares and the B/U/C composition of list errors for all four
setups. All values matched those reported below. It did not recompute intervals, the list penalty or the misdated
flag. Its code and output are in `verification/`.

### 3. Results

**Sources for all figures in this section:** `data/processed/results/<setup>.json`; the tables in
`data/processed/results/tables/` (`pairs_by_gap.csv`, `cycles.csv`, `lists_by_length.csv`,
`list_mistakes_by_length.csv`); `data/processed/results/p6_thinking.json`; and
`data/processed/results/explore_cutoff_qwen3-8b-nothink.txt`. All were generated on October 12, 2026 from the raw
replies.

#### 3.1 Pair judgments: no model reached a date resolution (Q1)

Share of pairs answered correctly in both orders, by gap between the two events (95% interval in brackets):

| Gap (years) | Qwen3 8B | Qwen3 14B | Llama 3.1 8B |
|---|---|---|---|
| 1 | 18% [8 to 32] | 36% [23 to 50] | 19% [8 to 32] |
| 2 | 23% [11 to 36] | 48% [35 to 62] | 19% [8 to 31] |
| 3 to 5 | 25% [18 to 34] | 53% [45 to 63] | 22% [15 to 30] |
| 6 to 10 | 29% [23 to 36] | 56% [48 to 63] | 24% [18 to 31] |
| 11 to 25 | 37% [31 to 43] | 68% [62 to 74] | 26% [21 to 32] |
| more than 25 | 68% [60 to 75] | 86% [80 to 91] | 29% [22 to 36] |
| Reversals, more than 25 years | 29% [23 to 36] | 9% [6 to 13] | 59% [51 to 66] |

![Date resolution](../figures/fig1_date_resolution.png)

- **Date resolution was not reached by any model.** No gap band, including "more than 25 years", reached 95% correct
  in both orders with at most 5% reversals.
- **Preference for the first option.** Share of all pair answers that were "A": Qwen3 8B 69%, Qwen3 14B 54%,
  Llama 3.1 8B 79%.
- **Year questions.** Exact years given, out of 120: Qwen3 8B 87, Qwen3 14B 102, Llama 3.1 8B 97. Year answers that
  could not be read: 0, 1 and 3 respectively (`year_check` in the results files).
- All pair replies from all models were readable (0 unreadable out of 14,280 per model).

#### 3.2 Cycles among consistent judgments

Sets of three events for which all three pairs received consistent answers, and the number forming a cycle:

| | Consistent triples | Cycles observed | Cycles expected under random placement of the same errors (95% of reassignments) |
|---|---|---|---|
| Qwen3 8B | 66,393 | 14 | 3,281 (3,012 to 3,602) |
| Qwen3 14B | 188,198 | 140 | 12,424 (11,931 to 12,961) |
| Llama 3.1 8B | 27,761 | 30 | 6,015 (5,829 to 6,199) |

For every model, none of the 1,000 reassignments came as close to the observed count (p ≤ 0.001). Where these models
give consistent answers, those answers are compatible with a single ordering of events, even where that ordering is
incorrect.

#### 3.3 List ordering: the origin of errors (Q2)

| | Length | Valid lists | Adjacent errors | B: incorrect on pair | U: reversal on pair | C: list-only [interval] | List penalty per list [interval] |
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

![Origin of list errors](../figures/fig2_list_mistakes.png)

**Pre-registered verdicts.** Under `PREREG.md` section 6, the verdict is "mostly in the pairs" if list-only errors are
at most 20% at every length and the penalty interval includes zero at every length; "a real long-list penalty" if
list-only errors rise with length to at least 50% at 20 events, or if the penalty interval at 20 events lies above
zero; and "in between" otherwise.
- **Qwen3 8B: a real long-list penalty**, through the penalty at 20 events (+0.80, interval 0.33 to 1.28). The
  list-only share rose (19% to 31%) but remained below 50%. **This verdict depends on a scoring decision** (section 4):
  if the 16 lists that listed every event and then reached the reply length limit (1, 6 and 9 lists at 5, 10 and 20
  events; `verification/independent_check.md`) are treated as unreadable, the verdict is "in between" (penalty +0.50,
  interval 0.00 to 1.00, based on 6 valid 20-event lists). **Exploratory caveat (not pre-registered):** the predicted
  error count behind the penalty breaks ties between events with equal win counts at random (pre-registered seed), and
  the 20-event result rests on only 15 valid lists, so this verdict should be treated as tentative.
- **Qwen3 14B: in between.** List-only errors were common (35% to 47%) and reached 47% at 20 events, just below the 50%
  threshold. The penalty was above zero at 10 events (+0.42) but not at 20 events, the length used by the rule.
- **Llama 3.1 8B: in between.** List-only errors remained below 20% at every length (19.9% at 10 events), but the
  penalty was *below* zero at 5 and 10 events: its lists contained fewer adjacent errors than its pair answers predict.
- **Qwen3 8B with thinking enabled: in between** (`q2_decision` in `qwen3-8b-think.json`; lists classified with the
  thinking-disabled pair answers). List-only errors were 18% to 28% (above the 20% limit for "mostly in the pairs" at
  10 and 20 events) and did not reach 50%, and the penalty at 20 events was below zero (-5.3, interval -5.9 to -4.7).

**Omitted events.** Long lists were often incomplete before any ordering error arose. Share of 20-event answers
listing every event exactly once: Qwen3 8B 25%, Qwen3 14B 50%, Llama 3.1 8B 28% (`lists_by_length.csv`). Every
incomplete 20-event answer omitted at least one event.

Why lists were invalid (`PREREG.md` section 5 requires these counts; a list can have several problems, and counts are
numbers of lists out of 90 at 5 and 10 events and 60 at 20 events). Source: `verification/independent_check.md`,
which was computed from the raw replies by a separately written program.

| Setup | Length | Invalid lists | Fewer than N numbered entries | With a missing code | With a repeated code | With an invented or unreadable entry |
|---|---|---|---|---|---|---|
| Qwen3 8B | 5 | 0 | 0 | 0 | 0 | 0 |
| | 10 | 11 | 2 | 11 | 9 | 0 |
| | 20 | 45 | 2 | 45 | 40 | 6 |
| Qwen3 14B | 5 | 0 | 0 | 0 | 0 | 0 |
| | 10 | 5 | 4 | 5 | 1 | 0 |
| | 20 | 30 | 21 | 30 | 6 | 4 |
| Llama 3.1 8B | 5 | 0 | 0 | 0 | 0 | 0 |
| | 10 | 5 | 4 | 5 | 1 | 1 |
| | 20 | 43 | 42 | 43 | 5 | 2 |
| Qwen3 8B, thinking enabled | 5 | 0 | 0 | 0 | 0 | 0 |
| | 10 | 5 | 5 | 5 | 0 | 0 |
| | 20 | 27 | 27 | 27 | 0 | 0 |

![List penalty and completeness](../figures/fig3_penalty_and_integrity.png)

**Further pre-registered list measures** (`PREREG.md` sections 5 and 6). *Exact match* is the share of all lists
ordered exactly correctly. *Kendall tau* measures agreement between a valid list and the true order, from -1
(reversed) to 1 (identical). *Misdated* is the share of adjacent errors flagged A, meaning the model's own year
answers place the two events in the same wrong order. The *secondary analysis* applies the same classification to all
lists, including incomplete ones, using the first appearance of each code; its list-only shares are within 4 percentage points
of the main analysis in every case.

| | Length | Exact match | Mean Kendall tau (valid lists) | Misdated | List-only share, secondary analysis |
|---|---|---|---|---|---|
| Qwen3 8B | 5 | 3% | 0.16 | 19% | 19% |
| | 10 | 0% | 0.31 | 16% | 25% |
| | 20 | 0% | 0.33 | 12% | 29% |
| Qwen3 14B | 5 | 7% | 0.29 | 13% | 35% |
| | 10 | 0% | 0.40 | 9% | 47% |
| | 20 | 0% | 0.41 | 9% | 46% |
| Llama 3.1 8B | 5 | 3% | 0.27 | 14% | 16% |
| | 10 | 0% | 0.36 | 11% | 20% |
| | 20 | 0% | 0.34 | 8% | 22% |
| Qwen3 8B, reasoning enabled | 5 | 57% | 0.80 | 60% | 18% |
| | 10 | 26% | 0.83 | 49% | 27% |
| | 20 | 0% | 0.86 | 52% | 26% |

Source: `data/processed/results/<setup>.json` (`exact_share_of_all`, `mean_tau_valid`, `misdated_share`,
`secondary_type_share`). With reasoning disabled, exact match fell to zero for every model at 10 and 20 events, consistent
with the sharp decline in exact ordering with list length reported by Wongchamcharoen and Glasserman (2025).

#### 3.4 Effect of reasoning (Qwen3 8B, same lists)

| Length | Exactly correct, thinking off / on | Valid, off / on | Adjacent errors per valid list, off / on | List-only share, off / on (difference [interval]) | Incorrect-on-pair share, off / on (difference [interval]) |
|---|---|---|---|---|---|
| 5 | 3% / 57% | 100% / 100% | 1.9 / 0.5 | 19% / 18% (-1 [-13 to +12]) | 20% / 31% (+11 [-1 to +25]) |
| 10 | 0% / 26% | 88% / 94% | 4.0 / 1.2 | 25% / 28% (+3 [-6 to +11]) | 16% / 25% (+9 [+0.4 to +18]) |
| 20 | 0% / 0% | 25% / 55% | 9.4 / 3.0 | 31% / 24% (-7 [-16 to +2]) | 13% / 17% (+4 [-3 to +12]) |

Adjacent errors per valid list are computed as the number of adjacent errors divided by the number of valid lists
(`lists_by_length.csv`, `list_mistakes_by_length.csv`). Differences are in percentage points (thinking on minus off),
with intervals from paired resampling of the same lists (`p6_thinking.json`).

- With thinking enabled, lists outperformed the predictions of the thinking-disabled pair answers by 1.4 (5 events),
  2.7 (10 events) and 5.3 (20 events) adjacent errors per list (intervals 1.2 to 1.5, 2.4 to 2.9 and 4.7 to 5.9).
- **P6 was not established.** At every list length the list-only share fell more, or rose less, than the
  incorrect-on-pair share (differences in the table above), the direction P6 predicted. The pre-registration set no
  decision rule for P6, and the change in the list-only share alone is not distinguishable from zero at any length
  (its interval includes zero). At 10 events the incorrect-on-pair share increased (interval above zero).
- With thinking enabled, 60%, 49% and 52% of the remaining adjacent errors (5, 10 and 20 events) involved events
  whose years the model had placed in the same wrong order when asked directly, compared with 19%, 16% and 12% with
  thinking disabled.

#### 3.5 Outcomes of the predictions

| Prediction | Outcome |
|---|---|
| P1: for Qwen3 8B, correct-in-both-orders rises with the gap, and reversals are most frequent at 1 to 2 years | **Largely supported.** The share rises in every band (18% to 68%). Reversals are highest at 1 and 2 years (66%, 63%), but the intervals up to 25 years overlap; the only clear decline occurs beyond 25 years. |
| P2: Qwen3 14B outperforms Qwen3 8B in every gap band | **Supported** in all six bands; the intervals overlap at 1 year and marginally at 2 years. |
| P3: cycles among consistent judgments are rarer than chance | **Supported** for all three models (p ≤ 0.001; 0 of 1,000 reassignments as close to the observed count). |
| P4: with thinking disabled, the list-only share increases with length | **Supported** for Qwen3 8B (19% at 5 events to 31% at 20, non-overlapping intervals); **supported** for Qwen3 14B (35% [28 to 41] at 5 events to 47% [42 to 52] at 20, non-overlapping intervals; flat from 10 to 20 events); **not supported** for Llama 3.1 8B by the same interval criterion (16% [9 to 23] at 5 events, 18% [14 to 24] at 20; the intervals overlap, although the point estimate at 20 events is higher than at 5, which is all that clarification 1 in `PREREG.md` literally requires). |
| P5: incomplete lists become more frequent with length | **Supported** for every setup (valid share at 20 events: 25% to 55%). |
| P6: reasoning reduces list-only errors more than incorrect-on-pair errors | **Not established.** The direction matches P6 at every length, but the pre-registration set no test and the list-only change alone is not distinguishable from zero (section 3.4). |

### 4. Deviations from the pre-registration

All changes made after `PREREG.md` was committed are dated in its Deviations section. In summary:
1. **Llama 3.1 8B was added**, run on a Windows PC, to test whether the Qwen3 results, in particular the preference
   for the first option, generalize to a model from another developer. It was added after Qwen3 8B's results had been
   seen and before any Llama answers were analyzed. The decision is dated 20:07 UTC on October 12, 2026 in `PREREG.md`
   and preceded the first Llama answers (20:18 UTC, `data/raw/model_runs/main/console_pc.log`), but it was committed to
   the repository at 21:17 UTC (commit b096739).
2. **The Llama run was repeated.** The first attempt ran partly under non-default PC settings (a compressed memory
   cache and a different attention implementation) and partly under default settings. Those answers were set aside
   unused, and the run was repeated from the start under default settings. The repeated run stopped once, at 13,710
   of 14,280 pair questions, because of a Windows networking error, and was resumed under the same settings; no
   question was asked twice.
3. **gpt-oss 20B was not run.** It was designated optional, and no prediction depends on it.
4. **Scoring of replies that reached the length limit** (decided after initial list results were seen). `PREREG.md`
   section 3 states that a reply reaching the length limit is unreadable; section 5 states that a list that continues
   past N entries is scored on its first N entries. Jayden Ling chose the section 5 reading, which the analysis code
   already applied (that code was committed before any main data were examined), while aware that the choice affects
   the Qwen3 8B verdict. Both outcomes are reported.
5. **Analysis corrections that change no rule.** The cycle reassignment now iterates over gap bands in a fixed order,
   so the pre-registered seed reproduces the same result on every run (this changed only Qwen3 8B's expected count,
   from 3,278 to 3,281). P6 uses paired resampling because both setups answered the same lists (`src/p6.py`).
6. **Repeatability.** For both Qwen3 models, all 530 repeated questions received identical answers. For Llama 3.1 8B,
   all 500 repeated pair questions matched, but only 24 of 30 repeated lists did; all differing lists had 20 events.
   The cause is unknown. The analysis scores the first answer, as planned.
7. **A misattribution in `PREREG.md` section 1.** It states that "small AI models usually answer" the pair question
   correctly, citing Wongchamcharoen and Glasserman (2025). That paper evaluated large models (GPT-4.1, Claude 3.7
   Sonnet and GPT-5; arXiv abstract, accessed October 15, 2026), so "small" was misattributed to it. `PREREG.md` is
   unchanged.

### 5. Limitations

- **Scope.** Four setups, all small models, and 120 well-documented events from 1900 to 2019. Larger models may
  behave differently.
- **Hardware.** Llama 3.1 8B was run on a Windows PC and the Qwen3 models on a Mac, with the same Ollama version and
  default settings. Differences between Llama and Qwen3 may partly reflect hardware.
- **Sample size for long lists.** The 20-event results rest on 15 (Qwen3 8B), 30 (Qwen3 14B), 17 (Llama 3.1 8B) and 33
  (thinking enabled) valid lists, and list intervals may be too narrow because lists share events.
- **A verdict that depends on a post hoc scoring decision** (section 4, item 4) **and on random tie-breaking** in the
  prediction (section 3.3, exploratory caveat). It rests on 15 valid 20-event lists and should be treated as
  tentative.
- **The reasoning comparison changed more than reasoning.** The thinking-enabled run used temperature 0.6, a context
  size of 20,480 and a reply limit of 16,384 tokens, whereas the thinking-disabled runs used temperature 0, a context
  size of 4,096 and a 400-token reply limit for lists (`options` fields in the raw replies; the thinking-enabled
  settings are the model card's recommended ones). The 400-token limit is what cut off some thinking-disabled Qwen3 8B
  lists. The thinking-enabled run is a single sample at temperature 0.6 with no repeat check (`repeat_check` in
  `qwen3-8b-think.json` is empty), so its run-to-run variation is unknown. Differences between the two setups cannot
  be attributed to reasoning alone.
- **Event descriptions were written by an AI system** (Claude), with an automatic check for numbers and ordering words
  and a manual check of 10 dates.
- **Dependence of the list-only share on pair accuracy.** A model that answers more pairs correctly has more
  opportunities for list-only errors, so comparisons of this share across models require caution (section 6).

### 6. Exploratory observations

These analyses were not pre-registered and should be treated as hypotheses.
- **Llama 3.1 8B makes little use of its date knowledge in pair questions.** It gave the exact year for 97 of 120
  events, yet answered only 58% of single pair questions correctly for events more than 25 years apart
  (`per_question_accuracy` in `llama3.1-8b.json`), close to the 50% expected from guessing. One possible
  explanation, not tested here, is that its preference for the first option outweighs its knowledge of the dates.
- **The list-only share tracks pair accuracy across models.** Correct-in-both-orders on pairs 1 to 10 years apart,
  compared with the list-only share: Qwen3 8B 18% to 29% and 19% to 31%; Llama 3.1 8B 19% to 24% and 16% to 20%;
  Qwen3 14B 36% to 56% and 35% to 47%. A higher list-only share may therefore indicate a model that answers more pairs
  correctly rather than one that handles lists worse.

### 7. Exploratory analyses (not pre-registered)

These analyses were designed and carried out on October 12, 2026, after all pre-registered results above were final.
They use only the saved replies; no model was run. They do not alter any pre-registered result, rule or verdict,
which stand as reported in sections 3 and 4, and they should be treated as hypotheses. Code: `src/explore_debias.py`.
Results: `data/processed/results/exploratory_debias.json` and `data/processed/results/tables/exploratory_debias.csv`
(one row per value, with its interval); the field names cited below refer to these files. Intervals follow the
pre-registered procedures: 2,000 resamples of the 120 events for pair results (seed 41, the same resamples as
`src/analyze.py`) and 2,000 resamples of lists within each length and spacing group for list results.

#### 7.1 Pair judgments with the first-option preference removed

**Method.** Each pair reply records the model's probabilities for its first answer token. Both "A" and "B" appear
among them in all 42,840 thinking-disabled pair replies, and the letter given was always the more probable of the two.
For each order of presentation, the probabilities of "A" and "B" were rescaled to sum to one. The *debiased
probability* of a pair is the probability that the earlier event is judged earlier, averaged over the two orders.
Because each event appears once in each position, a fixed preference for the first position acts equally in both
directions. A pair is counted as judged correctly when its debiased probability exceeds 0.5. This holds exactly when
the log-odds favoring the correct order, summed over both orders, are positive, so the classification does not depend
on whether probabilities or log-odds are averaged.

Share of pairs judged correctly after removing the first-option preference (`debiased_correct_share`; 95% interval in
brackets), with the pre-registered share correct in both orders (section 3.1) in parentheses:

| Gap (years) | Qwen3 8B | Qwen3 14B | Llama 3.1 8B |
|---|---|---|---|
| 1 | 50% [38 to 65] (18%) | 50% [37 to 65] (36%) | 47% [34 to 60] (19%) |
| 2 | 60% [46 to 74] (23%) | 62% [49 to 75] (48%) | 55% [41 to 69] (19%) |
| 3 to 5 | 59% [50 to 67] (25%) | 64% [56 to 72] (53%) | 55% [46 to 63] (22%) |
| 6 to 10 | 62% [55 to 69] (29%) | 67% [60 to 75] (56%) | 57% [51 to 63] (24%) |
| 11 to 25 | 72% [67 to 78] (37%) | 78% [73 to 84] (68%) | 60% [55 to 65] (26%) |
| more than 25 | 90% [85 to 94] (68%) | 92% [87 to 96] (86%) | 64% [55 to 71] (29%) |

- **No model reaches a date resolution under this measure either.** No gap band reaches 95%
  (`debiased_date_resolution`). For events one year apart, all three models are at the level of guessing.
- **Reversals are almost entirely first-option answers.** In 99% of Qwen3 8B reversals, 82% of Qwen3 14B reversals
  and 99% of Llama 3.1 8B reversals, the model answered "A" in both orders (`flips_with_both_answers_A`, all gaps).
- **Most reversals nonetheless contain a judgment, and it reflects the model's knowledge of dates.** After the
  preference is removed, 69% of Qwen3 8B reversals, 66% of Qwen3 14B reversals and 59% of Llama 3.1 8B reversals are
  judged correctly (`flips_debiased_correct`). Among reversals whose two events the model's own year answers place in
  the correct order, 72% (Qwen3 8B), 67% (Qwen3 14B) and 60% (Llama 3.1 8B) are judged correctly, against 37%, 42% and
  34% where the year answers place them in the wrong order (`flips_by_own_year_answers`; the latter rest on 53 to 262
  reversals and have wide intervals).
- **How decisive these judgments are.** The threshold set for this analysis, a debiased probability more than 0.25
  from 0.5, cannot be met by any reversal when probabilities are averaged: in a reversal each order favors a different
  event, so the average lies between 0.25 and 0.75 by construction. Averaging log-odds instead, which removes a
  constant shift in log-odds exactly, 2,360 of 2,787 Qwen3 8B reversals (85%; 1,683 correct, 677 incorrect), 755 of
  919 Qwen3 14B reversals (82%; 526 correct, 229 incorrect) and 155 of 4,202 Llama 3.1 8B reversals (4%; 109 correct,
  46 incorrect) are clearly decided (`flips_clearly_correct_logodds_average`, `flips_clearly_wrong_logodds_average`).
  For the Qwen3 models, a reversal therefore usually combines a definite underlying judgment with a strong preference
  for the first position. For Llama 3.1 8B, most reversals reflect probabilities close to even.
- **Extreme probabilities.** In 52% of Qwen3 8B reversals and 38% of Qwen3 14B reversals, the letter given had a
  probability above 0.99 in both orders (`flips_both_orders_above_0.99`), so the debiased judgment rests on comparing
  small probabilities for the letters not given. The agreement with the year answers suggests these comparisons carry
  information, but they are not calibrated confidence (section 7.3).

#### 7.2 Origin of list errors without dependence on pair accuracy (Q2)

**Method.** The list-only share in section 3.3 depends on how many pairs a model answers correctly in both orders
(section 5), and it counts every reversal as an error already present at the pair level. Here, for every pair of
events in each valid list (all pairs, not only adjacent ones), the list's order was compared with the debiased pair
judgment. *Agreement* is the share of these pairs that the list places in the order the pair judgment favors. It
treats correct and incorrect pair judgments alike. It is compared with the agreement expected if list errors and pair
errors were unrelated, given the accuracy of each, using Cohen's kappa (0 means no more agreement than unrelated errors
would produce; 1 means complete agreement). Thinking-enabled lists are compared with the thinking-disabled pair
answers of Qwen3 8B, as in the pre-registered analysis.

| | Length | Pairs in correct order: list / debiased pair judgment | Agreement (expected if unrelated) | Kappa [interval] | Adjacent errors also judged incorrectly after debiasing [interval] | Pre-registered equivalent: B + U |
|---|---|---|---|---|---|---|
| Qwen3 8B | 5 | 58% / 63% | 66% (52%) | 0.29 [0.20 to 0.36] | 49% [42 to 56] | 81% |
| | 10 | 65% / 69% | 68% (56%) | 0.28 [0.23 to 0.33] | 40% [36 to 45] | 75% |
| | 20 | 66% / 69% | 65% (56%) | 0.21 [0.10 to 0.30] | 43% [37 to 48] | 69% |
| Qwen3 14B | 5 | 65% / 67% | 77% (55%) | 0.48 [0.41 to 0.55] | 53% [45 to 61] | 65% |
| | 10 | 70% / 73% | 75% (59%) | 0.38 [0.33 to 0.43] | 41% [36 to 45] | 53% |
| | 20 | 71% / 73% | 73% (60%) | 0.34 [0.29 to 0.39] | 41% [35 to 47] | 53% |
| Llama 3.1 8B | 5 | 64% / 53% | 57% (51%) | 0.13 [0.06 to 0.20] | 53% [45 to 61] | 84% |
| | 10 | 68% / 56% | 60% (52%) | 0.17 [0.12 to 0.22] | 53% [48 to 58] | 80% |
| | 20 | 67% / 59% | 61% (53%) | 0.16 [0.08 to 0.23] | 49% [42 to 56] | 82% |
| Qwen3 8B, thinking enabled | 5 | 90% / 63% | 65% (60%) | 0.11 [0.04 to 0.18] | 53% [39 to 67] | 82% |
| | 10 | 92% / 69% | 70% (65%) | 0.14 [0.09 to 0.18] | 49% [40 to 57] | 72% |
| | 20 | 93% / 70% | 70% (68%) | 0.09 [0.04 to 0.14] | 41% [34 to 49] | 76% |

Source: `lists_by_length` in the results files (`list_correct_share_all_pairs`,
`debiased_pair_correct_share_all_pairs`, `agreement_all_pairs`, `agreement_if_independent`, `kappa`,
`adjacent_errors_also_wrong_debiased`). The last column is one minus the pre-registered list-only share (section 3.3).

- **List order is related to the debiased pair judgments, but only partly.** Agreement exceeds what unrelated errors
  would produce in every case (all kappa intervals lie above zero). With thinking disabled, however, lists disagree
  with the model's own debiased pair judgment on 23% to 43% of pairs. For Qwen3 8B, lists and debiased pair judgments
  are about equally accurate, yet they differ on about a third of pairs. For Qwen3 14B, agreement beyond chance
  declines with length (kappa 0.48 at 5 events and 0.34 at 20; the intervals do not overlap).
- **About half of adjacent list errors coincide with an incorrect debiased pair judgment.** The share was 40% to 53%
  across setups and lengths, compared with 53% to 84% under the pre-registered labels, which count every reversal as
  a pair-level error. The remaining 47% to 60% of adjacent errors involve a pair the model judges correctly once the
  preference is removed. Across all pairs in the lists, 45% to 64% of the pairs that a thinking-disabled list placed
  in the wrong order were also judged incorrectly after debiasing (`list_errors_also_wrong_debiased`), against 27% to
  47% of all pairs in those lists (one minus the pair accuracy in the table).
- **By pre-registered label** (`agreement_stable_right_pairs`, `agreement_flip_pairs`,
  `agreement_stable_wrong_pairs`). With thinking disabled, lists placed 17% to 24% of stable-right pairs in the wrong
  order, with no clear change across lengths. They followed the debiased judgment on 54% to 61% of reversal pairs, and
  repeated the stable-wrong answer on 57% to 76% (Qwen3 models) and 46% to 49% (Llama 3.1 8B) of stable-wrong pairs.
  With thinking enabled, lists misordered 3% to 6% of stable-right pairs and repeated the thinking-disabled
  stable-wrong answer on only 17% to 24% of stable-wrong pairs.
- **Pair-based ordering with the preference removed.** Ordering each list by its events' summed debiased
  probabilities predicted 1.76, 3.95 and 8.87 adjacent errors per valid Qwen3 8B list (5, 10 and 20 events), against
  1.87, 4.10 and 8.60 for the pre-registered win counting and 1.87, 4.04 and 9.40 observed
  (`mean_debiased_predicted_errors`, `mean_prereg_predicted_errors`, `mean_adjacent_errors`). Relative to this
  prediction, the Qwen3 8B list penalty is +0.11 [-0.08 to +0.30], +0.09 [-0.20 to +0.38] and +0.53 [-0.29 to +1.29]
  (`mean_debiased_penalty`); the interval at 20 events includes zero, unlike the pre-registered penalty (+0.80, 0.33
  to 1.28). For Qwen3 14B it is -0.01 [-0.19 to +0.17], +0.46 [+0.17 to +0.77] and 0.00 [-0.81 to +0.81]. For Llama
  3.1 8B it is below zero at every length (-0.28, -0.42 and -1.12; all intervals below zero): its lists were ordered
  much better than its debiased pair judgments would order them (mean Kendall tau 0.27 to 0.36, against 0.04 to 0.15;
  `mean_tau`, `mean_debiased_predicted_tau`). This comparison is a sensitivity check and does not change the
  pre-registered verdicts.

#### 7.3 Further exploratory items listed in the pre-registration (`PREREG.md` section 6)

- **Probability of the given answer versus gap** (`mean_p_answer`, `mean_p_answer_when_correct`,
  `mean_p_answer_when_wrong`). The probability the models attached to their answers barely changed with the gap:
  0.95 to 0.97 in every band for Qwen3 8B, 0.96 to 0.99 for Qwen3 14B and 0.70 to 0.72 for Llama 3.1 8B. Incorrect
  answers received nearly as much probability as correct ones: for events more than 25 years apart, 0.93 against 0.98
  (Qwen3 8B), 0.95 against 0.99 (Qwen3 14B) and 0.70 against 0.73 (Llama 3.1 8B). For events one year apart, incorrect
  answers received no less probability than correct ones for either Qwen3 model. The probability of an answer is
  therefore a weak guide to its accuracy for these models.
- **First-option preference by gap** (`share_A_answers`). For Qwen3 8B, the share of "A" answers fell from 82% [73 to
  90] for events one year apart to 64% [61 to 68] for events more than 25 years apart: the preference is strongest
  where the model's judgments are weakest. For Qwen3 14B (54% to 56%) and Llama 3.1 8B (78% to 80%), it did not vary
  with the gap.
- **Era of the list** (`lists_by_era`). Lists were grouped by the middle year of their events, and each valid list's
  Kendall tau was compared with the mean for valid lists of the same length and spacing (`mean_tau_vs_cell_mean`), since
  the periods contain different mixes of list lengths. Lists centred before 1940 were ordered less well than
  comparable lists in all four setups: tau differences of -0.10 [-0.18 to -0.02] (Qwen3 8B), -0.07 [-0.16 to +0.02]
  (Qwen3 14B), -0.12 [-0.21 to -0.02] (Llama 3.1 8B) and -0.07 [-0.13 to +0.00] (thinking enabled); the intervals
  exclude zero for Qwen3 8B and Llama 3.1 8B only. No difference was established for lists centred in 1940 to 1979 or
  1980 to 2019. Debiased pair accuracy for events at most 10 years apart rose from the earliest to the latest period
  for both Qwen3 models (57%, 59% and 64%; 59%, 64% and 69%), with overlapping intervals, but not for Llama 3.1 8B
  (56%, 52% and 58%) (`pairs_by_era_gap_1_to_10`).
- **Year-question accuracy by decade** (`year_by_decade`). Exact years per decade (10 events each) ranged from 5 to
  10 for Qwen3 8B (lowest in the 1940s), from 7 to 10 for Qwen3 14B and from 7 to 10 for Llama 3.1 8B, with no
  consistent trend across the period.

#### 7.4 Bearing on the conclusions

- **Q1.** Removing the first-option preference raises the share of pairs judged correctly considerably (for events
  more than 25 years apart, from 68% to 90% for Qwen3 8B and from 29% to 64% for Llama 3.1 8B), but no model reaches
  95%, so the conclusion that no model reached a reliable date resolution holds under this measure as well. Most
  reversals by the Qwen3 models reflect the preference for the first option rather than an absence of judgment.
- **Q2.** The account that list errors are already present at the pair level (Summary and section 3.3) rests
  on counting every reversal as a pair-level error. Once the first-option preference is removed, about half of
  adjacent list errors (40% to 53%) coincide with an incorrect pair judgment, and the remainder occur on pairs that the
  model judges correctly. For the Qwen3 models, the number of list errors remains close to what the debiased pair
  judgments predict, so lists are not clearly worse than the pair judgments, with one exception: Qwen3 14B at 10 events
  has a debiased list penalty of +0.46 [+0.17 to +0.77] (section 7.2). List errors and pair errors overlap only in
  part. These results weaken the pair-level account of list errors described in the Summary and section 3.3. They are
  exploratory and do not change the pre-registered verdicts.
- **Limitations specific to these analyses.** The adjustment assumes that the preference for the first position acts
  equally in both orders. It relies on probabilities that the models compute but do not give as answers, and for the
  Qwen3 models these are extreme and poorly calibrated (section 7.3). The analyses were chosen after the pre-registered
  results were known.

### 8. Reproducibility

See `README.md`. All results can be regenerated from the saved raw replies without running any model:
`python3 src/analyze.py`, `python3 src/p6.py` and `python3 src/make_figures.py`. The exploratory analyses in section 7
are regenerated by `python3 src/explore_debias.py`, which reads the saved replies and the per-list files written by
`src/analyze.py`.

### 9. References

- Wongchamcharoen, P. K., and Glasserman, P. (2025). Do Large Language Models (LLMs) Understand Chronology?
  arXiv:2511.14214. https://arxiv.org/abs/2511.14214 (accessed October 12, 2026).
- English Wikipedia year pages, 1900 to 2019 (CC BY-SA 4.0), and Wikidata (CC0), retrieved October 12, 2026; revision
  identifiers are recorded in `data/raw/SOURCES.md`.
- Models: Qwen3 (Apache 2.0) and Llama 3.1 (Llama 3.1 Community License), run with Ollama 0.40.3. License texts
  consulted on October 12, 2026: https://huggingface.co/Qwen/Qwen3-8B (license field and LICENSE file) and
  https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE with its Acceptable Use Policy. This
  repository publishes model replies only, not model weights. The replies are AI-generated text.
