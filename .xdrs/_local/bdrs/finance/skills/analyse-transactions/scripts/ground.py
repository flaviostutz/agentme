#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pdfplumber>=0.11", "openpyxl>=3.1"]
# ///
"""Ground a normalized file against its source: every row's date and amount must appear in the source.

  ground.py <normalized.md> [--sample N] [--json]
Matching is one-to-one (identical rows need identical source entries): first the same line, then a date up to
DATE_SLACK days later (booking after purchase) or an amount up to two lines below the date. Numeric dates such as
03-01-2026 are read in the day/month order of the source's unambiguous dates, or both ways when mixed. Also reports
source-only lines (date + amount but no row), the balance chain and the institution module check, and writes
<stem>.grounding.json. Exit codes: 0 grounded, 1 unmatched rows or failed checks, 2 invalid input.
Image transcriptions (normalizer: llm-image) cannot be grounded: all rows are reported as unverified, exit 0.
"""

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import institutions
import ledger
import sourcedoc
from ledger import LedgerError
from textutil import parse_amount, parse_date

DATE_SLACK = 4
LINE_WINDOW = 2
DEFAULT_SAMPLE = 20
DATES = [
    (re.compile(r"\b(\d{1,2})[-./](\d{1,2})[-./](\d{4})\b"), "dmy"),
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "ymd"),
    (re.compile(r"\b(\d{4})(\d{2})(\d{2})\b"), "ymd"),
    (re.compile(r"\b(\d{1,2}) ([A-Z][a-z]{2})[a-z]* (\d{4})\b"), "dMy"),
    (re.compile(r"\b([A-Z][a-z]{2})[a-z]* (\d{1,2}), (\d{4})\b"), "Mdy"),
]
AMOUNT = re.compile(r"(?<![\d.,])(?:\d{1,3}(?:[.,']\d{3})*|\d+)[.,]\d{2}(?!\d|[.,]\d)")


def numeric_order(texts: list) -> str:
    """'dmy' or 'mdy' when the source's unambiguous numeric dates (day > 12) agree (95%+), else '' (read both)."""
    votes = Counter()
    for text in texts:
        for a, b, _ in DATES[0][0].findall(text):
            if int(a) > 12 >= int(b):
                votes["dmy"] += 1
            elif int(b) > 12 >= int(a):
                votes["mdy"] += 1
    top, other = sorted(("dmy", "mdy"), key=lambda k: -votes[k])
    return top if votes[top] >= 3 and votes[other] * 20 <= votes[top] else ""


def dates_in(text: str, numeric: str = "") -> set:
    found = set()
    both = {"": lambda a, b, c: [(c, b, a), (c, a, b)], "dmy": lambda a, b, c: [(c, b, a)],
            "mdy": lambda a, b, c: [(c, a, b)]}[numeric]
    for pattern, order in DATES:
        for m in pattern.finditer(text):
            a, b, c = m.groups()
            candidates = {"dmy": both(a, b, c), "ymd": [(a, b, c)]}.get(order)
            if candidates is None:
                raw = f"{a} {b} {c}" if order == "dMy" else f"{b} {a} {c}"
                try:
                    found.add(parse_date(raw, "%d %b %Y"))
                except LedgerError:
                    pass
                continue
            for y, mo, d in candidates:
                try:
                    found.add(date(int(y), int(mo), int(d)).isoformat())
                except ValueError:
                    pass
    return found


def amounts_in(text: str, cells: list | None = None) -> set:
    found = set()
    for token in cells if cells is not None else [m.group(0) for m in AMOUNT.finditer(text)]:
        try:
            found.add(abs(parse_amount(token)).quantize(ledger.CENT))
        except (LedgerError, ArithmeticError):
            continue
    return found


def source_entries(doc) -> list:
    """Per source line: (dates, amounts, text)."""
    texts = [" ".join(r) for r in doc.table] if doc.table else doc.lines()
    numeric = numeric_order(texts)
    if doc.table:
        return [(dates_in(t, numeric), amounts_in("", r), " | ".join(r)) for t, r in zip(texts, doc.table, strict=True)]
    return [(dates_in(line, numeric), amounts_in(line), line) for line in texts]


def shifted(day: str, days: int) -> str:
    return (date.fromisoformat(day) + timedelta(days=days)).isoformat()


def match(rows: list, entries: list) -> tuple:
    """Return (matches {row index: (line, how)}, used lines)."""
    pairs = {}
    for n, (ds, amts, _) in enumerate(entries):
        for d in ds:
            for a in amts:
                pairs.setdefault((d, a), []).append(n)
    used, uses, matches = set(), Counter(), {}

    def take(key, i, how):
        for n in pairs.get(key, []):
            if uses[(key, n)] < 1:
                uses[(key, n)] += 1
                used.add(n)
                matches[i] = (n, how)
                return True
        return False

    wanted = [(i, r.date, abs(r.value).quantize(ledger.CENT)) for i, r in enumerate(rows, 1)]
    for i, d, a in wanted:
        take((d, a), i, "line")
    for i, d, a in wanted:
        if i not in matches:
            any(take((shifted(d, k), a), i, f"date+{k}") for k in range(1, DATE_SLACK + 1))
    for i, d, a in wanted:
        if i in matches:
            continue
        for n, (ds, _, _) in enumerate(entries):
            if d in ds and n not in used and any(a in entries[k][1] for k in range(n, min(n + LINE_WINDOW + 1,
                                                                                            len(entries)))):
                used.add(n)
                matches[i] = (n, "window")
                break
    return matches, used


def ground(path: Path, cwd: Path, sample: int) -> dict:
    led = ledger.read(path)
    normalizer = led.meta.get("normalizer", "")
    result = {"file": path.name, "normalizer": normalizer, "rows": len(led.rows)}
    if normalizer == "llm-image":
        return {**result, "unverified": len(led.rows), "exit": 0,
                "warning": "image transcription: values cannot be grounded; report every row as unverified"}
    src = ledger.resolve_tmp(led.meta.get("source", ""), cwd)
    doc = sourcedoc.load(src)
    if not doc.has_text:
        raise LedgerError(f"source {src.name} has no text to ground against")
    entries = source_entries(doc)
    matches, used = match(led.rows, entries)
    unmatched = [{"row": i, "date": r.date, "value": ledger.format_value(r.value),
                  "reason": "date and amount not found together in the source"}
                 for i, r in enumerate(led.rows, 1) if i not in matches]
    source_only = [{"line": n + 1, "dates": sorted(ds), "amounts": [str(a) for a in sorted(amts)]}
                   for n, (ds, amts, _) in enumerate(entries)
                   if ds and n not in used and any(a != 0 for a in amts)]
    total = sum((r.value for r in led.rows), Decimal(0))
    opening, closing = led.meta.get("opening-balance", "none"), led.meta.get("closing-balance", "none")
    if "none" in (opening, closing):
        chain = {"ok": None, "message": "no balances in the source"}
    else:
        expected = ledger.parse_value(opening) + total
        chain = {"ok": expected == ledger.parse_value(closing), "opening": opening,
                 "sum": ledger.format_value(total), "closing": closing}
    module_check = []
    if normalizer.startswith("module:"):
        module_check = institutions.by_name(normalizer.split(":", 1)[1]).check(doc, led)
    seed = int(hashlib.sha256(src.read_bytes()).hexdigest()[:12], 16)
    picked = sorted(random.Random(seed).sample(sorted(matches), min(sample, len(matches))))
    spot = [{"row": i, "title": led.rows[i - 1].title, "value": ledger.format_value(led.rows[i - 1].value),
             "description": led.rows[i - 1].description, "source-line": entries[matches[i][0]][2][:300]}
            for i in picked]
    ok = not unmatched and chain["ok"] is not False and all(f.get("ok") for f in module_check)
    how = Counter(h for _, h in matches.values())
    return {**result, "matched": len(matches), "matched-by": dict(how), "unmatched": unmatched,
            "source-only": source_only, "balance-chain": chain, "module-check": module_check,
            "sample": spot, "exit": 0 if ok else 1}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", help="normalized file inside .tmp/")
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE, help="matched rows to spot-check")
    parser.add_argument("--json", action="store_true", help="print the full JSON result")
    args = parser.parse_args(argv)
    cwd = Path.cwd()
    try:
        path = ledger.resolve_tmp(args.file, cwd)
        result = ground(path, cwd, max(0, args.sample))
    except (LedgerError, OSError, KeyError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    except Exception as err:  # noqa: BLE001 - third-party parsers raise many types for corrupt files
        print(f"error: cannot read the source of {args.file}: {type(err).__name__}: {err}", file=sys.stderr)
        return 2
    out = path.with_name(path.stem + ".grounding.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(f"{result['file']}: {result.get('matched', 0)}/{result['rows']} rows grounded"
              f", {len(result.get('unmatched', []))} unmatched, {len(result.get('source-only', []))} source-only"
              f" lines, balance {result.get('balance-chain', {}).get('ok')}"
              f", module check {[f['check'] for f in result.get('module-check', []) if not f.get('ok')] or 'ok'}"
              f" -> {out.name}" + (f"; {result['warning']}" if "warning" in result else ""))
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
