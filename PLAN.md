# Plan: Chronology Pairs

Written Oct 12, 2026, at the end of the planning session. Status: **waiting for Jayden's OK.** Nothing has been run or downloaded.

**Who does what.** Study directed by Jayden Ling. Code, analysis and write-up by Claude Code (an AI agent), checked by Jayden. Jayden chose this split on Oct 12, 2026. Every public mention of the project uses that credit line.

**Labels used below.** *Known* = checked on a source or this computer. *Think* = reasoning, not yet checked. *Guess* = an estimate the pilot will replace. **UNVERIFIED** = not checked against a source yet.

---

## 1. The question

AI language models usually answer "which came first?" correctly for two events, yet they rarely put a long list of events in exactly the right order (Wongchamcharoen and Glasserman, "Do LLMs Understand Chronology?", 2025, https://arxiv.org/abs/2511.14214; re-open before citing). That paper says it does not know why.

This study asks two things about small AI models that run on a home computer:

1. **Date resolution.** How many years apart do two events need to be before a model answers "which came first?" correctly *and* consistently? Consistent means it gives the same answer when the two events are swapped, and it never goes in circles (A before B, B before C, but C before A).
2. **Where list mistakes come from.** When a model sorts a list, what share of its mistakes would it also make on those same two events alone, and what share appear only in the list?

**Why neighbor pairs are the right thing to count.** A list is exactly right if and only if every pair of side-by-side events is in the right order. One wrong neighbor pair breaks the list. If every neighbor pair is right, then #1 is before #2, #2 is before #3, and so on, so by chaining, every event is before every later one. That lets each list mistake be traced back to a single pair, and checked against the model's answer on that pair alone.

**Who would use the answer.**
- People who use AI to put things in time order (news timelines, history questions) get a "date resolution" per model: below it, don't trust the order.
- People who test AI forecasters with "use only information from before year Y" prompts. Those prompts assume the model knows what came before what.
- A practical choice: is it more reliable to sort events with many two-event questions, or to ask for the whole list at once? This study answers that for these models with no extra model calls.

## 2. Decisions and why

| # | Decision | Choice | Why | Decided by |
|---|---|---|---|---|
| 1 | Answer key | Our own list of 120 events, one per year, 1900 to 2019, each year checked on Wikipedia and Wikidata; events where the two disagree are replaced | One per year gives many close pairs (119 pairs 1 year apart, 466 pairs 2 to 5 years apart), where models should struggle. The era is well documented and well before the models' training cutoffs. Our own list avoids a rerun of the earlier paper. | Jayden |
| 2 | How each year's event is picked | A random month per year (saved seed), then the first event in that month on the year's Wikipedia page that (a) happened on one specific day, (b) has a Wikidata date in the same year, (c) is not a duplicate. If none qualifies, the next month. | A fixed rule anyone can rerun, so no one can say the events were hand-picked to get a result. The random month avoids a January-heavy list. | Jayden |
| 3 | Event wording | Rewritten as short descriptions with no numbers, no order words (first, second, last, new, former), pointing to exactly one event, under about 12 words. Wikipedia's original title kept in a separate column. | Names like "1906 San Francisco earthquake" or "World War II" give away the answer. | Jayden |
| 4 | Who writes what | Claude writes the code, analysis, pre-registration and write-up. Jayden approves each run and download, spot-checks 10 event dates, and reads the final result until he can explain it. | Jayden's choice, for speed. | Jayden |
| 5 | Public credit | "Study directed by Jayden Ling. Code, analysis and write-up by Claude Code (an AI agent), checked by Jayden." | Honest, and required for anything public. | Jayden |
| 6 | Where it runs | This Mac (Apple M5 Pro, 24 GB memory), with Ollama, which is already installed | *Known* (checked Oct 12): Ollama 0.40.3 is installed with qwen3:8b, qwen3:14b and gpt-oss:20b already downloaded. No downloads needed to start. | Claude |
| 7 | Models | Main: Qwen3 8B, thinking off. Size check: Qwen3 14B, thinking off. Thinking comparison: Qwen3 8B, thinking on (lists only). Stretch: gpt-oss 20B, a reasoning model from a different company. | Same model with thinking on and off isolates what thinking changes. 14B shows whether size helps. All three are already on disk. | Claude |
| 8 | Pair table | All 7,140 pairs of the 120 events, asked in both orders: 14,280 questions per model. Temperature 0 (the model always picks its most likely answer). | Cycles can only be counted with every pair. The computer time is cheap (*guess*: 1 to 4 hours per model). | Claude |
| 9 | Year check | Each model is asked "In what year did this happen?" for all 120 events. Used to label mistakes, not to drop events. | Keeps the same events for every model, while still separating "doesn't know the date" from other mistakes. | Claude |
| 10 | Lists | Lengths 5, 10 and 20, crossed with the gap between neighboring events: tight (1 to 2 years), medium (3 to 5), wide (6 to 10). Length 20 with wide gaps is dropped because it needs at least 114 of the 119 available years. 8 cells, 30 lists each, the same lists for every model. | Holds spacing in a band while length changes, at the close gaps where pair mistakes should live. | Claude |
| 11 | List answer format | Each event gets a random two-letter code. The model returns the codes in order. | Exact, automatic scoring. *Think*: it may cause fewer dropped or invented items than writing out names, which the write-up will say. | Claude |
| 12 | Error ranges | Pair results: 2,000 redraws of the events (bootstrap over events). List results: 2,000 redraws of lists within each cell, flagged as possibly too narrow because lists share events. | Events, not questions, are the real sample. | Claude |
| 13 | Publishing | GitHub repo with a short report, only with Jayden's OK. arXiv only with honest authorship and an endorser who is comfortable with it. Not for student journals or science fairs, which require the student to do the research. | Matches decision 4. | Claude, from Jayden's goals |

## 3. How the questions are asked

- **Pair question:** "Which happened first? A: [event] B: [event] Answer with only the letter A or B." Each pair is asked twice, with the two events swapped.
- **Year question:** "In what year did this happen? [event] Answer with the year only." The first four-digit number counts as the answer.
- **List question:** the shuffled events with their codes, and "List the codes from earliest to latest, separated by commas. Output only the codes."
- Replies that can't be read count as **invalid**, not wrong, and are reported.
- Exact wording is fixed in `PREREG.md` after the pilot.

## 4. Scoring

**Each pair** gets one label from its two answers:
- **stable-right:** right both ways.
- **stable-wrong:** wrong both ways.
- **flip:** the answer changes when the order is swapped.
- **invalid.**

**Date resolution** (per model): pair results are grouped by year gap (1, 2, 3 to 5, 6 to 10, 11 to 25, more than 25). Date resolution is the smallest gap band where that band and every wider band have at least 95% stable-right and at most 5% flips. The full curve is always reported, even if no band qualifies.

**Circular triples:**
- Only triples where all three pairs are stable count. With 120 events there are 280,840 triples.
- Compare the real count with 1,000 shuffles that move the same number of wrong answers randomly within each gap band.
- Fewer cycles than the shuffles means the mistakes fit a consistent but blurry timeline. About the same means the mistakes look random. More means worse than random.

**Each list** is scored in two parts:
1. **Integrity.** Every code appears exactly once and none is invented. Lists that fail are counted and described (dropped, duplicated, invented), and don't get part 2.
2. **Wrong neighbor pairs** in the valid lists. Each one gets a type:
   - **A, doesn't know the date:** the model's own year answers put the two events in this wrong order, or tie them.
   - **B, wrong on the pair alone:** the pair is stable-wrong in the pair table (and not A).
   - **U, unsure on the pair:** the pair is a flip in the pair table.
   - **C, list-only:** the pair is stable-right alone, but wrong in the list.

**Headline number:** the share of type C mistakes, by list length, gap band and model.

**Pair-based prediction:**
- For each list, the same events are also sorted using only the model's saved pair answers, ranked by how many pairs each event wins. This is "win counting," with a flip counting as half a win.
- Its wrong neighbor pairs are the prediction. The observed count minus the predicted count is the list penalty.
- This also answers the practical question: sorting by many pair questions vs. asking for the whole list.

**For comparison with the earlier paper**, also report exact match (share of lists perfectly right) and Kendall tau (a score from -1 to 1 for how close two orderings are).

## 5. What would prove the pair explanation wrong

These thresholds are fixed now, before any data:
- **The collapse is "mostly in the pairs"** if type C is at most 20% of wrong neighbor pairs at every list length, and the list penalty's 95% range includes zero.
- **There is "a real long-list penalty"** if type C rises with length and is at least 50% at length 20, or if the list penalty's 95% range is above zero at length 20.
- **Dropped or invented items** are reported separately, so they can't hide inside either answer.
- **Thinking mode:** if thinking on cuts type C much more than types A and B, thinking fixes list handling, not date knowledge.
- **Every outcome gets reported**, including "in between."

## 6. Step-by-step plan with dates

Each step needs Jayden's OK before it starts. Dates are *guesses* until the pilot.

| Step | Dates | What happens | Jayden's part |
|---|---|---|---|
| 0 | Oct 12 to 13 | OK this plan. Claude makes a local git repo (no upload). | Read and OK (~15 min) |
| 1 | Oct 13 to 15 | **Events.** Claude downloads the 120 Wikipedia year pages and the matching Wikidata entries through their official APIs, logs them in `data/raw/SOURCES.md` with license and terms, builds `data/processed/events.csv` with code, and runs an automatic check for numbers and order words. | OK the download; spot-check 10 dates (~15 min) |
| 2 | Oct 15 to 16 | **Pilot** on this Mac with the first 25 events: 600 pair questions, 16 lists, 4 thinking-on lists, two prompt wordings. Measures speed, unreadable replies, repeatability at temperature 0, and whether outputs follow the code letters instead of the dates. Claude reads the Qwen3 and gpt-oss model pages for thinking settings and licenses. | OK running the models |
| 3 | Oct 16 to 17 | **Pre-registration.** Claude writes `PREREG.md` (hypotheses, final prompts, thresholds, analysis, and a fingerprint of the event list) and commits it before any main run. Pilot data is kept out. | Read and OK; decide whether to upload it to a private GitHub repo as a dated record |
| 4 | Oct 17 to 21 | **Main runs:** year check and pair table for Qwen3 8B and 14B; lists with thinking off and on. A rerun of 500 pairs and 30 lists checks repeatability. | OK each run |
| 5 | Oct 21 to 24 | **Stretch:** gpt-oss 20B, while the analysis starts | OK |
| 6 | Oct 21 to 28 | **Analysis and charts:** date resolution curves, the A/B/U/C split by length, observed vs predicted list mistakes, cycles vs shuffles | None |
| 7 | Oct 28 to Nov 3 | **Report and README** | Can wait until after a busy week |
| 8 | Nov 3 to 6 | Jayden reads the one-page result until he can explain it. Then, with his OK: public release. | Read, ask questions, OK each public step |

**Stop and change rules (fixed now):**
- If more than 5% of pilot replies can't be read after one prompt fix, change the prompt or parser and write a dated note before the main runs.
- If one model's pair table would take more than 12 hours, ask every pair up to 25 years apart (2,675 pairs) plus 1,000 random wider pairs.
- If Qwen3 8B gets 90% or more of 20-event lists exactly right in the pilot, there is no collapse to explain. Then add 40-event tight lists, or a smaller model, which needs a download and Jayden's OK.
- (Added Oct 12, before any model run.) If the pilot's year question shows Qwen3 8B dates fewer than half of the events exactly right, raise the notability floor from 20 to 40 language editions and rebuild the event list before the main runs.

**Postponed, no new model calls needed:** other sorting algorithms (insertion, merge, quicksort) run on the saved pair tables; repeats at a higher temperature to separate stuck mistakes from random ones; more models.

## 7. Open risks

- **Speed** on this Mac is UNVERIFIED. The pilot replaces every time estimate above.
- **Settings:** whether Ollama 0.40.3 can turn Qwen3 thinking on and off, and set gpt-oss's reasoning level, is UNVERIFIED. *Think*: Qwen3's own guidance may advise against temperature 0 with thinking on; check the model page before `PREREG.md`.
- **The random-month rule may pick little-known events.** Then most mistakes would be type A (doesn't know the date). That is still a finding, but the "knows both dates" subset could be small. Its size gets reported.
- **Automatic event picking may misread some Wikipedia pages.** Every manual fix is logged.
- **The rewordings are written by an AI** (Claude). The automatic leak check plus Jayden's spot-check are the safeguards. This is disclosed.
- **Nothing to explain:** small models could be near perfect on pairs, or near perfect on short lists. The stop rules above cover this.
- **Code labels** may tempt the model to sort by letter. The pilot checks for it.
- **Licenses and terms:** Wikipedia (CC BY-SA 4.0) and Wikidata (CC0) were checked and logged on Oct 12. Qwen3 and gpt-oss are UNVERIFIED until read before the pilot.
- **It must not read as a rerun of the 2025 chronology paper.** What's new here: pairs asked both ways, flips and cycles, the A/B/U/C split, the pair-based prediction, and small local models. Prior work must be re-opened before it is cited.
- **Impact** is the weakest part. The write-up must say plainly who would use the date-resolution number and the pair-vs-list sorting result.
- **Authorship:** the work is AI-built. The credit line in decision 5 goes on everything public.

## 8. Changes after approval

All of these were made before any model was run.

- **Oct 12, event picking, decision 2.**
  - **Change:** a Wikidata date now has to match the event's exact day, not just its year.
  - **Why:** a year-only match (or a match one day off) can "verify" an event through a different event on a linked article. Example: "Malenkov succeeds Stalin" (Mar 6, 1953) matched Stalin's death (Mar 5). Multi-day date ranges are also now skipped, as the "one specific day" rule intended.
- **Oct 12, event picking, decision 2.**
  - **Change:** added a notability floor. The event's Wikidata item must have articles in at least 20 language editions of Wikipedia.
  - **Why:** without it, many picks were obscure (median 18 language editions). With it, the median is 40, and 96 of 120 years still use their random month.
  - **How the 20 was chosen:** from event information only, not model results. A fallback rule for the pilot is in section 6.
- **Oct 12, event wording, decision 3.**
  - **Change:** ten events needed one fact from the matched article's opening paragraph to be described uniquely without numbers (for example, the 1953 Academy Awards). Those paragraphs were downloaded and logged.
  - **Note:** six descriptions are 13 words, slightly over "about 12."
- **Oct 12, pilot, list answer format.**
  - **Change:** lists are answered as a numbered list of codes (format D in `src/prompts.py`), and only the first N entries are scored.
  - **Why:** the planned comma-separated codes gave near-random orders with thinking off, even for 5 events, and endless repetition on 20-event lists. Details are in PREREG.md section 9.
  - **Related:** pair wording A was kept (0 unreadable replies in the pilot).
