# Independent check (recomputed from raw files, following PREREG sections 5 and 6)

Repeat-check records (`|repeat` keys) are excluded everywhere. Thinking-off setups: qwen3-8b-nothink (8B), qwen3-14b-nothink (14B), llama3.1-8b (Llama).

## 1. Pairs (shares are of readable pairs; stable-right = SR, flip = FL, stable-wrong = SW)

| Setup | Band | Pairs | Readable | SR | SR % | FL | FL % | SW | SW % |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-8b-nothink | 1 year | 119 | 119 | 22 | 18.5% | 79 | 66.4% | 18 | 15.1% |
| qwen3-8b-nothink | >25 | 4465 | 4465 | 3037 | 68.0% | 1295 | 29.0% | 133 | 3.0% |
| qwen3-14b-nothink | 1 year | 119 | 119 | 43 | 36.1% | 37 | 31.1% | 39 | 32.8% |
| qwen3-14b-nothink | >25 | 4465 | 4465 | 3821 | 85.6% | 405 | 9.1% | 239 | 5.4% |
| llama3.1-8b | 1 year | 119 | 119 | 23 | 19.3% | 72 | 60.5% | 24 | 20.2% |
| llama3.1-8b | >25 | 4465 | 4465 | 1278 | 28.6% | 2614 | 58.5% | 573 | 12.8% |

Position bias (share of readable pair replies that are "A", repeats excluded):

| Setup | Readable replies | Unreadable replies | "A" replies | Share "A" |
|---|---|---|---|---|
| qwen3-8b-nothink | 14280 | 0 | 9877 | 69.2% |
| qwen3-14b-nothink | 14280 | 0 | 7735 | 54.2% |
| llama3.1-8b | 14280 | 0 | 11226 | 78.6% |

All six gap bands (extra, for reference):

| Setup | 1 year (SR / FL) | 2 years (SR / FL) | 3 to 5 (SR / FL) | 6 to 10 (SR / FL) | 11 to 25 (SR / FL) | >25 (SR / FL) |
|---|---|---|---|---|---|---|
| qwen3-8b-nothink | 18.5% / 66.4% | 22.9% / 62.7% | 25.3% / 59.8% | 29.3% / 55.9% | 36.9% / 53.5% | 68.0% / 29.0% |
| qwen3-14b-nothink | 36.1% / 31.1% | 48.3% / 20.3% | 53.4% / 20.1% | 55.7% / 20.4% | 68.0% / 17.6% | 85.6% / 9.1% |
| llama3.1-8b | 19.3% / 60.5% | 18.6% / 61.9% | 21.8% / 58.9% | 24.3% / 60.0% | 25.7% / 59.0% | 28.6% / 58.5% |

## 2. Circular triples (triples whose three pairs are all stable)

| Setup | All-stable triples | Circular | Circular share |
|---|---|---|---|
| qwen3-8b-nothink | 66393 | 14 | 0.021% |
| qwen3-14b-nothink | 188198 | 140 | 0.074% |
| llama3.1-8b | 27761 | 30 | 0.108% |

(Shuffle baseline skipped, as asked. 120 events give 273,280 triples in total.)

## 3. Lists

Valid = first N numbered entries are N different codes from the list, none invented. Wrong neighbor pair = two consecutive entries, first one actually later. C = stable-right on the pair alone, U = flip, B = stable-wrong (X = unreadable pair). Labels for qwen3-8b-think come from qwen3-8b-nothink pair answers; others use their own.

| Setup | N | Lists | Valid | Valid % | Wrong neighbor pairs | C | C % | U | U % | B | B % | X | Exactly right (valid, 0 wrong) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-8b-nothink | 5 | 90 | 90 | 100.0% | 168 | 32 | 19.0% | 103 | 61.3% | 33 | 19.6% | 0 | 3 |
| qwen3-8b-nothink | 10 | 90 | 79 | 87.8% | 319 | 80 | 25.1% | 188 | 58.9% | 51 | 16.0% | 0 | 0 |
| qwen3-8b-nothink | 20 | 60 | 15 | 25.0% | 141 | 44 | 31.2% | 79 | 56.0% | 18 | 12.8% | 0 | 0 |
| qwen3-14b-nothink | 5 | 90 | 90 | 100.0% | 142 | 49 | 34.5% | 35 | 24.6% | 58 | 40.8% | 0 | 6 |
| qwen3-14b-nothink | 10 | 90 | 85 | 94.4% | 338 | 160 | 47.3% | 66 | 19.5% | 112 | 33.1% | 0 | 0 |
| qwen3-14b-nothink | 20 | 60 | 30 | 50.0% | 270 | 126 | 46.7% | 60 | 22.2% | 84 | 31.1% | 0 | 0 |
| llama3.1-8b | 5 | 90 | 90 | 100.0% | 151 | 24 | 15.9% | 98 | 64.9% | 29 | 19.2% | 0 | 3 |
| llama3.1-8b | 10 | 90 | 85 | 94.4% | 332 | 66 | 19.9% | 198 | 59.6% | 68 | 20.5% | 0 | 0 |
| llama3.1-8b | 20 | 60 | 17 | 28.3% | 147 | 27 | 18.4% | 94 | 63.9% | 26 | 17.7% | 0 | 0 |
| qwen3-8b-think | 5 | 90 | 90 | 100.0% | 45 | 8 | 17.8% | 23 | 51.1% | 14 | 31.1% | 0 | 51 |
| qwen3-8b-think | 10 | 90 | 85 | 94.4% | 105 | 29 | 27.6% | 50 | 47.6% | 26 | 24.8% | 0 | 23 |
| qwen3-8b-think | 20 | 60 | 33 | 55.0% | 99 | 24 | 24.2% | 58 | 58.6% | 17 | 17.2% | 0 | 0 |

Why lists were invalid (a list can have several problems; counts are of lists):

| Setup | N | Invalid lists | Fewer than N numbered entries | With a missing code | With a repeated code | With an invented/unreadable entry |
|---|---|---|---|---|---|---|
| qwen3-8b-nothink | 5 | 0 | 0 | 0 | 0 | 0 |
| qwen3-8b-nothink | 10 | 11 | 2 | 11 | 9 | 0 |
| qwen3-8b-nothink | 20 | 45 | 2 | 45 | 40 | 6 |
| qwen3-14b-nothink | 5 | 0 | 0 | 0 | 0 | 0 |
| qwen3-14b-nothink | 10 | 5 | 4 | 5 | 1 | 0 |
| qwen3-14b-nothink | 20 | 30 | 21 | 30 | 6 | 4 |
| llama3.1-8b | 5 | 0 | 0 | 0 | 0 | 0 |
| llama3.1-8b | 10 | 5 | 4 | 5 | 1 | 1 |
| llama3.1-8b | 20 | 43 | 42 | 43 | 5 | 2 |
| qwen3-8b-think | 5 | 0 | 0 | 0 | 0 | 0 |
| qwen3-8b-think | 10 | 5 | 5 | 5 | 0 | 0 |
| qwen3-8b-think | 20 | 27 | 27 | 27 | 0 | 0 |

Valid lists whose reply hit the 400-token limit after the N entries (scored on the first N entries, per the PREREG section 5 reading and the Oct 12 22:30 deviation):

| Setup | N=5 | N=10 | N=20 |
|---|---|---|---|
| qwen3-8b-nothink | 1 | 6 | 9 |
| qwen3-14b-nothink | 0 | 0 | 0 |
| llama3.1-8b | 0 | 0 | 0 |
| qwen3-8b-think | 0 | 0 | 0 |

## Judgment calls

- Pair replies: readable = the whole reply is the single letter A or B (spaces, quotes, markdown stars and a final period would be tolerated). In all three files every non-repeat pair reply is exactly 'A' or 'B', so unreadable = 0 and the rule changes nothing. All pair replies ended with done_reason 'stop'.
- Pair label: right/wrong is judged from the year fields (year_a, year_b) of each record, not from the prompt text. A flip = one order right and the other wrong (this includes always answering 'A' or always 'B'). Gap = difference in true years; band counts came out at exactly 119/118/348/560/1530/4465 for every setup.
- Position bias: counted over all 14,280 non-repeat pair replies (each ordered pair once), not over pairs.
- Circular triples: triple taken in true year order x<y<z over all 120 events; circular = labels (xy,yz,xz) right,right,wrong or wrong,wrong,right, where right/wrong mean stable-right/stable-wrong. A triple with any flip or unreadable pair is skipped (not counted in the all-stable total). No shuffle baseline.
- List parsing (written from PREREG section 5): a 'numbered entry' is a line starting with a number followed by '.' or ')' (leading spaces, stars, underscores, backticks, '>' or '-' tolerated). The entry's code is the first letters/digits token after the number. Lines without a number (e.g. Llama's 'Here is the list...' preamble, or notes) are ignored. Only the first N numbered entries are read; anything after is ignored (so Qwen3 8B's repetition loops and Qwen3 14B's second 'corrected' list after the first N entries do not count against it).
- List validity: valid only if there are exactly N numbered entries read, all different, all codes from that list. A reply with fewer than N numbered entries (e.g. 9 of 10, 19 of 20) is invalid (a code is missing). A repeated code or an entry that is not one of the list's codes also makes the list invalid. Codes are matched case-sensitively (no entry matched only after upper-casing).
- Cut-off replies: lists whose reply hit the 400-token limit are still scored on their first N entries if those are valid (PREREG section 5 reading, as instructed). This affects only qwen3-8b-nothink (16 of its 184 valid lists; see table). Under the stricter section 3 reading ('cut off counts as unreadable') those lists would be invalid.
- Wrong neighbor pairs: only in valid lists; consecutive entries where the first event's true year is later. Labeled C/U/B/X from the pair label of that unordered pair for the same setup (Qwen3 8B-think uses qwen3-8b-nothink labels). The 'misdated' flag (year answers), win counting, list penalty, Kendall tau and error ranges were not computed. 'Exactly right' counts valid lists with zero wrong neighbor pairs (extra).
- qwen3-8b-think: the file already had all 240 non-repeat list records when I started (no waiting needed). Every reply ended with done_reason 'stop'; I used the `content` field (the final answer) and not `thinking`. List ids, codes and true years are identical across all four files.

## Run notes

- qwen3-8b-think: 240 non-repeat list records read (0 repeat lines ignored, 0 malformed lines skipped, waited 0 min)
- qwen3-8b-nothink: 14640 non-repeat records (530 repeat lines ignored, 0 malformed skipped)
- qwen3-14b-nothink: 14640 non-repeat records (530 repeat lines ignored, 0 malformed skipped)
- llama3.1-8b: 14640 non-repeat records (530 repeat lines ignored, 0 malformed skipped)
- List sets identical (ids, codes, years) for qwen3-8b-think vs qwen3-8b-nothink: True
- List sets identical (ids, codes, years) for qwen3-14b-nothink vs qwen3-8b-nothink: True
- List sets identical (ids, codes, years) for llama3.1-8b vs qwen3-8b-nothink: True

