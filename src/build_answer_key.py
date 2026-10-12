"""Step 1d: build the answer key and check the wording for leaks (PLAN.md decision 3).

Joins the selected events (data/processed/events_selected.csv) with the rewritten descriptions
(data/manual/event_wording.csv) and writes data/processed/events.csv.

The leak check fails the build if any description contains a digit, a Roman numeral, a number
word, or a word that reveals order or era, unless the wording file's note explains why the word is
allowed (for example, "Modern" in the film title Modern Times). Descriptions over 12 words are
listed as warnings. Also prints a fingerprint of the answer key for the pre-registration.
"""

import csv
import hashlib
import re
import sys

from common import MANUAL, PROCESSED, YEARS

ROMAN = re.compile(r"^(?=[MDCLXVI]+$)M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
NUMBER_WORDS = {
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
    "twenty", "thirty", "forty", "fifty", "hundred", "hundreds", "thousand", "thousands", "million",
    "millions", "dozen", "dozens", "half",
}
ORDER_WORDS = {
    "first", "second", "third", "fourth", "fifth", "last", "final", "new", "newest", "former", "later",
    "latest", "earlier", "early", "late", "next", "previous", "modern", "postwar", "post-war", "prewar",
    "pre-war", "inaugural", "again", "recent", "current", "today", "now", "century", "decade", "era",
    "millennium", "ancient", "old", "oldest", "wwi", "wwii",
}
# Only these may appear inside a name. Ordinals never get this pass ("Second Sudanese Civil War").
NAME_SAFE = {"new", "modern", "old"}
MAX_WORDS = 12


def leak_flags(text):
    flags = []
    if re.search(r"\d", text):
        flags.append("digit")
    for m in re.finditer(r"[A-Za-z][A-Za-z'\-]*", text):
        raw = m.group(0)
        word = raw.lower().strip("'")
        after = text[m.end():]
        is_initial = len(raw) == 1 and after.startswith(".")  # "James M. Cox"
        # A capitalized word followed by another capitalized word is part of a name
        # ("New York", "New Horizons", "Modern Times"), not an order word.
        in_name = raw[0].isupper() and re.match(r"^\s+[A-Z]", after) is not None
        if ROMAN.match(raw) and not is_initial:
            flags.append(f"roman numeral '{raw}'")
        if word in NUMBER_WORDS:
            flags.append(f"number word '{raw}'")
        if word in ORDER_WORDS and not (in_name and word in NAME_SAFE):
            flags.append(f"order or era word '{raw}'")
    return flags


def main():
    selected = {int(r["year"]): r for r in csv.DictReader((PROCESSED / "events_selected.csv").open(encoding="utf-8"))}
    wording = {int(r["year"]): r for r in csv.DictReader((MANUAL / "event_wording.csv").open(encoding="utf-8"))}

    problems, warnings, rows = [], [], []
    if sorted(selected) != YEARS or sorted(wording) != YEARS:
        problems.append("the selected events and the wording file must both cover every year 1900 to 2019")
    texts = [w["event_text"] for w in wording.values()]
    if len(set(texts)) != len(texts):
        problems.append("two years have the same description")

    for year in YEARS:
        s, w = selected[year], wording[year]
        text = w["event_text"].strip()
        flags = leak_flags(text)
        if flags and not w["note"].strip():
            problems.append(f"{year}: {', '.join(flags)} in: {text}")
        elif flags:
            warnings.append(f"{year}: allowed by note ({w['note']}): {', '.join(flags)}")
        n_words = len(text.split())
        if n_words > MAX_WORDS:
            warnings.append(f"{year}: {n_words} words: {text}")
        rows.append({
            "year": year, "month": s["month"], "day": s["day"], "event_text": text,
            "wording_source": w["wording_source"], "wording_note": w["note"],
            "wikipedia_text": s["wikipedia_text"], "matched_article": s["matched_article"],
            "wikidata_qid": s["wikidata_qid"], "wikidata_property": s["wikidata_property"],
            "wikidata_date": s["wikidata_date"], "sitelinks": s["sitelinks"],
            "wikipedia_revid": s["wikipedia_revid"], "wikipedia_source": s["wikipedia_source"],
            "wikidata_source": s["wikidata_source"],
        })

    for w in warnings:
        print("WARNING", w)
    if problems:
        for p in problems:
            print("PROBLEM", p)
        sys.exit("Answer key NOT written: fix the problems above.")

    out = PROCESSED / "events.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    fingerprint = hashlib.sha256(
        "\n".join(f"{r['year']}\t{r['event_text']}" for r in rows).encode("utf-8")
    ).hexdigest()
    print(f"Wrote {out}: {len(rows)} events, no unexplained leaks.")
    print(f"Answer key fingerprint (sha256 of year + text): {fingerprint}")


if __name__ == "__main__":
    main()
