"""Watch the laws behind app/customs/tax_rates.json and report when their text changes.

Rates are NEVER updated automatically: a changed law needs a human to read it and edit the JSON.
This script only detects that something changed, so nobody has to re-read the codes by hand.

Usage (from backend/):
    python scripts/check_law_updates.py            # check; exit 1 if any watched clause changed
    python scripts/check_law_updates.py --update   # after reviewing: store current fingerprints

Exit codes: 0 = no changes, 1 = a clause changed (review needed), 2 = could not check (network,
or the clause markers were not found — the article was probably renumbered/rewritten).
Run it on a schedule (GitHub Actions cron or AWS EventBridge) and alert the team on exit != 0.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

import httpx

RATES_FILE = Path(__file__).resolve().parents[1] / "app" / "customs" / "tax_rates.json"


def normalize(page_html: str) -> str:
    """HTML -> plain text with collapsed whitespace (stable across cosmetic markup changes)."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", page_html))
    return re.sub(r"\s+", " ", text).strip()


def extract_clause(text: str, start: str, end: str) -> str | None:
    i = text.find(start)
    if i < 0:
        return None
    j = text.find(end, i + len(start))
    return text[i:j].strip() if j >= 0 else None


def fingerprint(clause: str) -> str:
    return hashlib.sha256(clause.encode("utf-8")).hexdigest()[:16]


def revision_of(text: str) -> str | None:
    m = re.search(r"Редакція від (\d{2}\.\d{2}\.\d{4})", text)
    return m.group(1) if m else None


def check(update: bool = False, fetch=None) -> int:
    fetch = fetch or (lambda url: httpx.get(url, timeout=60, follow_redirects=True,
                                            headers={"User-Agent": "Mozilla/5.0"}).text)
    data = json.loads(RATES_FILE.read_text(encoding="utf-8"))
    pages: dict[str, str] = {}
    status = 0
    for key, src in data["sources"].items():
        if not src.get("start"):
            print(f"[manual ] {key}: no machine-checkable clause; re-check by hand ({src['url']})")
            continue
        try:
            if src["url"] not in pages:
                pages[src["url"]] = normalize(fetch(src["url"]))
        except Exception as exc:  # network / HTTP error
            print(f"[ERROR  ] {key}: cannot fetch {src['url']}: {exc}")
            status = max(status, 2)
            continue
        text = pages[src["url"]]
        clause = extract_clause(text, src["start"], src["end"])
        if clause is None:
            print(f"[MISSING] {key}: clause markers not found — the article was likely changed. REVIEW.")
            status = max(status, 2)
            continue
        fp, rev = fingerprint(clause), revision_of(text)
        if update:
            src["fingerprint"] = fp
            if rev:
                src["revision_checked"] = rev
            print(f"[stored ] {key}: {fp} (revision {rev})")
        elif src.get("fingerprint") != fp:
            print(f"[CHANGED] {key}: {src.get('fingerprint')} -> {fp} (revision {rev}). REVIEW {src['title']}")
            status = max(status, 1)
        else:
            print(f"[ok     ] {key} (revision {rev})")
    if update:
        data["sources_checked_at"] = date.today().isoformat()
        RATES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--update", action="store_true", help="store current fingerprints after review")
    sys.exit(check(update=parser.parse_args().update))
