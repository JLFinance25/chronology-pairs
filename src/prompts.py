"""Prompt wordings and reply parsers.

Two wordings per task are tried in the pilot. The one with fewer unreadable replies is fixed in
PREREG.md before the main runs.
"""

import re

PAIR = {
    "A": "Which of these two events happened first?\nA: {a}\nB: {b}\nAnswer with only the letter A or B.",
    "B": ("Here are two historical events.\nEvent A: {a}\nEvent B: {b}\n"
          "Which event occurred earlier? Reply with a single letter, A or B."),
}

YEAR = "In what year did this event happen?\n{event}\nAnswer with the year only."

LIST = {
    "A": ("Put these events in chronological order, from earliest to latest.\n\n{lines}\n\n"
          "Answer with only the codes, separated by commas, earliest first."),
    "B": ("Below are some historical events, each with a code.\n\n{lines}\n\n"
          "Sort them by when they happened, oldest first. Reply with the codes only, comma-separated."),
    # Added after the first pilot: codes-only answers gave near-random orders without thinking.
    "C": ("Put these events in chronological order, from earliest to latest.\n\n{lines}\n\n"
          "Rewrite every line exactly as given (code and event), one per line, earliest first. "
          "Write nothing else."),
    "D": ("Put these events in chronological order, from earliest to latest.\n\n{lines}\n\n"
          "Answer with a numbered list of the codes only, one per line, earliest first, "
          "like this:\n1. XX\n2. XX"),
}
LINE_FORMAT = {"C", "D"}  # answers with one event per line: read the code at the start of each line

# Two-letter list codes use only these letters: no vowels (so codes don't spell words) and no
# Roman-numeral letters (so codes don't suggest an order).
CODE_LETTERS = "BFGHJKNPQRSTWYZ"
CODE_RE = re.compile(r"\b([%s]{2})\b" % CODE_LETTERS)
# Codes that read like ordinary words or abbreviations are never used.
BLOCKED_CODES = {"BY", "PS", "ST", "NY", "PH", "SH", "HQ", "GB", "TH", "NB", "PT", "QT", "JK", "FB", "SF"}


def make_codes(rng, n):
    pool = [a + b for a in CODE_LETTERS for b in CODE_LETTERS if a != b and a + b not in BLOCKED_CODES]
    return rng.sample(pool, n)


def list_lines(codes, texts):
    return "\n".join(f"{c}: {t}" for c, t in zip(codes, texts))


def parse_pair(content):
    """'A', 'B', or None if the reply can't be read as one letter."""
    text = content.strip().strip("*_`\"' ").upper()
    m = re.match(r"^(?:ANSWER\s*[:\-]?\s*)?(?:EVENT\s+)?([AB])\b", text)
    if m:
        return m.group(1)
    letters = set(re.findall(r"\b([AB])\b", text))
    return letters.pop() if len(letters) == 1 else None


def parse_year(content):
    m = re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", content)
    return int(m.group(1)) if m else None


LINE_CODE_RE = re.compile(r"^\s*(?:\d+[.)]\s*)?\**([%s]{2})\b" % CODE_LETTERS, re.M)


def parse_list(content, codes, line_format=False):
    """Codes in the order given, plus integrity details."""
    continued_past_n = False
    if line_format:
        # Numbered answers: the first N entries are the answer. Writing more than N entries is
        # recorded as "continued_past_n" and does not count against integrity.
        found = LINE_CODE_RE.findall(content)  # the code at the start of each line
        continued_past_n = len(found) > len(codes)
        found = found[: len(codes)]
    else:
        found = CODE_RE.findall(content)  # case-sensitive, so "by" is never read as a code
    wanted = set(codes)
    order = [c for c in found if c in wanted]
    invented = [c for c in found if c not in wanted]
    duplicates = sorted({c for c in order if order.count(c) > 1})
    missing = sorted(wanted - set(order))
    valid = not invented and not duplicates and not missing
    return {"order": order, "valid": valid, "missing": missing, "duplicates": duplicates, "invented": invented,
            "continued_past_n": continued_past_n}
