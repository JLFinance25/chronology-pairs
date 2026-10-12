"""Step 1c: pick one verified event per year (PLAN.md decision 2, tightened Oct 12, 2026).

For each year: start at its random month (data/processed/year_months.csv) and walk the bullets of
that month's events on the year's Wikipedia page, in page order. The first bullet that qualifies is
the year's event. If none qualifies, try the next month, wrapping around to January.

A bullet qualifies if:
  (a) it is dated to one specific day (no "c. January", no date ranges);
  (b) one of its linked articles has a Wikidata date (point in time, start time, inception,
      publication, opening, first flight, launch, first performance, dissolution or death) in the
      on exactly the same day (so also the same year);
  (c) that Wikidata item was not already used for an earlier year.

  (d) that Wikidata item has articles in at least MIN_SITELINKS language editions of Wikipedia
      (an objective notability floor, so most events are ones a model could know).

Changes from the plan (Oct 12, 2026, before any model was run; logged in WORKLOG.md):
  - The plan asked only for the same year. An exact-day match is required because a year-only (or
    one-day-off) match can "verify" an event through a different event on a linked article, such as
    a person's death the day before.
  - Rule (d) was added because many events picked without it were obscure.

Wikidata lookups are cached in data/raw/wikidata/ so re-running does not re-download.
"""

import csv
import re
from datetime import date

from common import PROCESSED, RAW, WIKIDATA_SPARQL, WIKIPEDIA_API, YEARS, polite_get, read_json, write_json

WIKI_DIR = RAW / "wikipedia"
CACHE_QIDS = RAW / "wikidata" / "title_to_qid.json"
CACHE_DATES = RAW / "wikidata" / "qid_dates.json"
CACHE_SITELINKS = RAW / "wikidata" / "qid_sitelinks.json"

# Notability floor for rule (d). Chosen Oct 12, 2026 from event metadata only, before any model run.
MIN_SITELINKS = 20

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTHS)}

DATE_PROPS = {
    "P585": "point in time", "P580": "start time", "P571": "inception", "P577": "publication date",
    "P1619": "date of official opening", "P606": "first flight", "P619": "launch date",
    "P1191": "first performance", "P576": "dissolved", "P570": "date of death",
}

LINK_RE = re.compile(r"\[\[([^\[\]|]+)(?:\|([^\[\]]*))?\]\]")
DATE_TEXT_RE = re.compile(r"^(%s)\s+(\d{1,2})$" % "|".join(MONTHS))
SEPARATOR_RE = re.compile(r"\s*(?:&ndash;|&mdash;|–|—|-|:)\s*")


# ---------- Wikitext helpers ----------

def strip_noise(text):
    """Remove references, comments, templates and HTML tags."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    previous = None
    while previous != text:  # nested templates
        previous = text
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text


def to_plain(text):
    """Wikitext to readable plain text."""
    text = LINK_RE.sub(lambda m: m.group(2) if m.group(2) is not None else m.group(1), text)
    text = text.replace("'''", "").replace("''", "")
    text = text.replace("&ndash;", "–").replace("&mdash;", "—").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def is_date_title(title):
    return bool(DATE_TEXT_RE.match(title.strip())) or title.strip().isdigit()


def article_links(text):
    """Linked article titles in order, skipping files, categories, dates and years."""
    titles = []
    for m in LINK_RE.finditer(text):
        target = m.group(1).split("#")[0].strip()
        if not target or ":" in target.split(" ")[0] and target.split(":")[0] in ("File", "Image", "Category"):
            continue
        if target.startswith(("File:", "Image:", "Category:", ":")) or is_date_title(target):
            continue
        titles.append(target[0].upper() + target[1:])
    return titles


def parse_date_prefix(prefix):
    """Return (month, day) if the prefix names exactly one day, else None."""
    labels = []
    for m in LINK_RE.finditer(prefix):
        label = (m.group(2) if m.group(2) is not None else m.group(1)).strip()
        labels.append(label)
    plain = to_plain(prefix)
    days = DATE_TEXT_RE.findall(plain)
    if len(days) != 1:
        return None
    # A range such as "March 3–5" or "March 3 to 5" means more than one day.
    if re.search(r"\d\s*(?:–|-|&ndash;|to)\s*\d", plain):
        return None
    month, day = days[0]
    return MONTH_NUM[month], int(day)


def events_section(wikitext):
    m = re.search(r"^==\s*Events\s*==\s*$", wikitext, re.M)
    if not m:
        return ""
    rest = wikitext[m.end():]
    end = re.search(r"^==[^=].*?==\s*$", rest, re.M)
    return rest[: end.start()] if end else rest


def parse_bullets(year, wikitext):
    """All single-day bullets in the Events section, in page order, with sub-bullets inheriting dates."""
    bullets = []
    parent_date = None
    order = 0
    for raw_line in events_section(wikitext).splitlines():
        line = strip_noise(raw_line).rstrip()
        if not line.startswith("*"):
            continue
        depth = len(line) - len(line.lstrip("*"))
        body = line.lstrip("*").strip()
        if depth == 1:
            sep = SEPARATOR_RE.search(body)
            prefix, text = (body[: sep.start()], body[sep.end():]) if sep else (body, "")
            # A bullet that is only a date (with sub-bullets below) has no separator.
            parent_date = parse_date_prefix(prefix) if DATE_TEXT_RE.search(to_plain(prefix)) else None
            # The separator split a range ("April 24–30 – ..."): the text then starts with a day.
            # An optional bracketed note may sit in between: "21 (April 6–8 O.S.) – ...".
            if re.match(r"^(?:(?:%s)\s+)?\d{1,2}(?:\s*\([^)]*\))?\s*(?:–|-|&ndash;|—)" % "|".join(MONTHS), to_plain(text)):
                parent_date = None
            if parent_date is None or not to_plain(text) or to_plain(text).endswith(":"):
                continue
            links = article_links(prefix) + article_links(text)
        else:
            if parent_date is None:
                continue
            text = body
            links = article_links(text)
        order += 1
        bullets.append({
            "year": year, "order": order, "month": parent_date[0], "day": parent_date[1],
            "wikitext": raw_line.strip(), "text": to_plain(text), "links": links,
        })
    return bullets


# ---------- Wikidata lookups (cached) ----------

def load_cache(path):
    return read_json(path) if path.exists() else {}


def lookup_qids(titles, cache):
    todo = sorted({t for t in titles if t not in cache})
    for i in range(0, len(todo), 50):
        batch = todo[i : i + 50]
        data = polite_get(WIKIPEDIA_API, {
            "action": "query", "format": "json", "formatversion": "2", "prop": "pageprops",
            "ppprop": "wikibase_item", "redirects": "1", "titles": "|".join(batch), "maxlag": "5",
        })
        query = data.get("query", {})
        renamed = {}
        for step in query.get("normalized", []) + query.get("redirects", []):
            renamed[step["from"]] = step["to"]
        found = {p["title"]: p.get("pageprops", {}).get("wikibase_item") for p in query.get("pages", [])}
        for title in batch:
            final = title
            for _ in range(3):
                final = renamed.get(final, final)
            cache[title] = found.get(final)
    write_json(CACHE_QIDS, cache)
    return cache


def lookup_dates(qids, cache):
    todo = sorted({q for q in qids if q and q not in cache})
    props = " ".join(f"wd:{p}" for p in DATE_PROPS)
    for i in range(0, len(todo), 150):
        batch = todo[i : i + 150]
        values = " ".join(f"wd:{q}" for q in batch)
        query = f"""
        SELECT ?item ?prop ?time ?prec WHERE {{
          VALUES ?item {{ {values} }}
          VALUES ?prop {{ {props} }}
          ?prop wikibase:claim ?claim ; wikibase:statementValue ?value .
          ?item ?claim ?st . ?st ?value ?tv ; wikibase:rank ?rank .
          ?tv wikibase:timeValue ?time ; wikibase:timePrecision ?prec .
          FILTER(?rank != wikibase:DeprecatedRank)
        }}"""
        data = polite_get(WIKIDATA_SPARQL, {"query": query, "format": "json"})
        for q in batch:
            cache[q] = []
        for row in data["results"]["bindings"]:
            q = row["item"]["value"].rsplit("/", 1)[1]
            cache[q].append({
                "prop": row["prop"]["value"].rsplit("/", 1)[1],
                "time": row["time"]["value"],
                "precision": int(row["prec"]["value"]),
            })
    write_json(CACHE_DATES, cache)
    return cache


def lookup_sitelinks(qids, cache):
    """Number of Wikipedia (and sister-project) articles linked to each item, a notability count."""
    todo = sorted({q for q in qids if q and q not in cache})
    for i in range(0, len(todo), 200):
        batch = todo[i : i + 200]
        values = " ".join(f"wd:{q}" for q in batch)
        query = f"SELECT ?item ?n WHERE {{ VALUES ?item {{ {values} }} ?item wikibase:sitelinks ?n . }}"
        data = polite_get(WIKIDATA_SPARQL, {"query": query, "format": "json"})
        for q in batch:
            cache[q] = 0
        for row in data["results"]["bindings"]:
            cache[row["item"]["value"].rsplit("/", 1)[1]] = int(row["n"]["value"])
    write_json(CACHE_SITELINKS, cache)
    return cache


def day_match(bullet, wd_date):
    """True if a day-precision Wikidata date is exactly the bullet's day."""
    if wd_date["precision"] < 11:
        return False
    m = re.match(r"^\+?(-?\d+)-(\d\d)-(\d\d)", wd_date["time"])
    if not m:
        return False
    try:
        wd_day = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        wp_day = date(bullet["year"], bullet["month"], bullet["day"])
    except ValueError:
        return False
    return wd_day == wp_day


# ---------- Selection ----------

def month_order(start):
    return [((start - 1 + k) % 12) + 1 for k in range(12)]


def select(min_sitelinks, quiet=False):
    months = {int(r["year"]): int(r["month"]) for r in csv.DictReader((PROCESSED / "year_months.csv").open())}
    pages = {y: read_json(WIKI_DIR / f"{y}.json") for y in YEARS}
    bullets = {y: parse_bullets(y, pages[y]["wikitext"]) for y in YEARS}
    qid_cache, date_cache = load_cache(CACHE_QIDS), load_cache(CACHE_DATES)
    link_cache = load_cache(CACHE_SITELINKS)

    chosen, used_qids, log_rows = {}, set(), []
    for step in range(12):
        # Look up Wikidata for this round's months in one batch, then decide year by year.
        round_bullets = {
            y: [b for b in bullets[y] if b["month"] == month_order(months[y])[step]]
            for y in YEARS if y not in chosen
        }
        titles = [t for bs in round_bullets.values() for b in bs for t in b["links"]]
        if not titles:
            continue
        qid_cache = lookup_qids(titles, qid_cache)
        date_cache = lookup_dates([qid_cache.get(t) for t in titles], date_cache)
        day_matched = [
            qid_cache.get(t) for y, bs in round_bullets.items() for b in bs for t in b["links"]
            if any(day_match(b, d) for d in date_cache.get(qid_cache.get(t) or "", []))
        ]
        link_cache = lookup_sitelinks(day_matched, link_cache)
        for y in YEARS:
            if y in chosen:
                continue
            for b in round_bullets.get(y, []):
                match, reason = None, "no linked article with a same-day Wikidata date"
                for title in b["links"]:
                    qid = qid_cache.get(title)
                    if not qid:
                        continue
                    for d in date_cache.get(qid, []):
                        if d["time"].lstrip("+")[:4] == str(y) and day_match(b, d):
                            if qid in used_qids:
                                reason = f"duplicate of an earlier year ({qid})"
                                continue
                            if link_cache.get(qid, 0) < min_sitelinks:
                                reason = f"below notability floor ({link_cache.get(qid, 0)} sitelinks)"
                                continue
                            match = (title, qid, d)
                            break
                    if match:
                        break
                log_rows.append({
                    "year": y, "month": b["month"], "day": b["day"], "page_order": b["order"],
                    "qualifies": bool(match), "reason": "" if match else reason, "text": b["text"],
                })
                if match:
                    title, qid, d = match
                    used_qids.add(qid)
                    chosen[y] = {
                        "year": y, "random_month": months[y], "month": b["month"], "day": b["day"],
                        "wikipedia_text": b["text"], "matched_article": title, "wikidata_qid": qid,
                        "wikidata_property": f"{d['prop']} ({DATE_PROPS[d['prop']]})",
                        "wikidata_date": d["time"][:11].lstrip("+"),
                        "sitelinks": link_cache.get(qid, 0),
                        "wikipedia_revid": pages[y]["revid"], "wikipedia_source": pages[y]["source_url"],
                        "wikidata_source": f"https://www.wikidata.org/wiki/{qid}",
                        "wikitext": b["wikitext"],
                    }
                    break
        if not quiet:
            print(f"after month step {step + 1}: {len(chosen)} of {len(YEARS)} years have an event")
        if len(chosen) == len(YEARS):
            break
    return chosen, log_rows


def main():
    chosen, log_rows = select(MIN_SITELINKS)
    out = PROCESSED / "events_selected.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(next(iter(chosen.values())).keys()))
        writer.writeheader()
        for y in YEARS:
            if y in chosen:
                writer.writerow(chosen[y])
    log = PROCESSED / "event_selection_log.csv"
    with log.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()))
        writer.writeheader()
        writer.writerows(log_rows)
    missing = [y for y in YEARS if y not in chosen]
    print(f"Wrote {out} ({len(chosen)} events) and {log}")
    if missing:
        print("Years with no qualifying event:", missing)


if __name__ == "__main__":
    main()
