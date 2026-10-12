"""Step 1b: download the English Wikipedia page for each year, 1900 to 2019.

Saves one JSON file per year in data/raw/wikipedia/ with the page text and its revision ID,
so the exact version used can always be fetched again. Already-downloaded years are skipped.
"""

from datetime import datetime, timezone

from common import RAW, WIKIPEDIA_API, YEARS, polite_get, write_json

OUT_DIR = RAW / "wikipedia"
BATCH = 10


def fetch_batch(years):
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "revisions",
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        "titles": "|".join(str(y) for y in years),
        "maxlag": "5",
    }
    data = polite_get(WIKIPEDIA_API, params)
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for page in data["query"]["pages"]:
        if page.get("missing"):
            print(f"  missing page: {page['title']}")
            continue
        rev = page["revisions"][0]
        record = {
            "title": page["title"],
            "pageid": page["pageid"],
            "revid": rev["revid"],
            "rev_timestamp": rev["timestamp"],
            "fetched_at": fetched_at,
            "source_url": f"https://en.wikipedia.org/w/index.php?oldid={rev['revid']}",
            "wikitext": rev["slots"]["main"]["content"],
        }
        write_json(OUT_DIR / f"{page['title']}.json", record)


def main():
    todo = [y for y in YEARS if not (OUT_DIR / f"{y}.json").exists()]
    print(f"{len(todo)} year pages to download")
    for i in range(0, len(todo), BATCH):
        batch = todo[i : i + BATCH]
        print(f"  {batch[0]} to {batch[-1]}")
        fetch_batch(batch)
    print("Done")


if __name__ == "__main__":
    main()
