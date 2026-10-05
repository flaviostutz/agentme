"""Ground a normalized file against its source: every row's date and amount must appear in the source.

Matching is one-to-one (identical rows need identical source entries): first the same line, then a date up to
DATE_SLACK days later (booking after purchase) or an amount up to two lines below the date. Numeric dates such as
03-01-2026 are read in the day/month order of the source's unambiguous dates, or both ways when mixed. Also reports
source-only lines (date + amount but no row), the balance chain and the institution module check.
Image transcriptions (normalizer: llm-image) cannot be grounded: all rows are reported as unverified.
"""

import contextlib
import hashlib
import random
import re
from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from analyse_account_transactions.app import ledger
from analyse_account_transactions.app.jsonfile import write_json
from analyse_account_transactions.app.ports import InstitutionRegistry, LedgerStore, Sources
from analyse_account_transactions.app.textutil import parse_amount, parse_date
from analyse_account_transactions.shared.constants import CENT
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Doc, Ledger, Row
from analyse_account_transactions.shared.values import format_value, parse_value

DATE_SLACK = 4
LINE_WINDOW = 2
DEFAULT_SAMPLE = 20
MAX_MONTH = 12
MIN_VOTES = 3
VOTE_RATIO = 20
SEED_HEX_DIGITS = 12
SOURCE_LINE_CHARS = 300
DATES = [
    (re.compile(r"\b(\d{1,2})[-./](\d{1,2})[-./](\d{4})\b"), "dmy"),
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "ymd"),
    (re.compile(r"\b(\d{4})(\d{2})(\d{2})\b"), "ymd"),
    (re.compile(r"\b(\d{1,2}) ([A-Z][a-z]{2})[a-z]* (\d{4})\b"), "dMy"),
    (re.compile(r"\b([A-Z][a-z]{2})[a-z]* (\d{1,2}), (\d{4})\b"), "Mdy"),
]
AMOUNT = re.compile(r"(?<![\d.,])(?:\d{1,3}(?:[.,']\d{3})*|\d+)[.,]\d{2}(?!\d|[.,]\d)")
Entry = tuple[set[str], set[Decimal], str]


def numeric_order(texts: list[str]) -> str:
    """'dmy' or 'mdy' when the source's unambiguous numeric dates (day > 12) agree (95%+), else '' (read both)."""
    votes: Counter[str] = Counter()
    for text in texts:
        for a, b, _ in DATES[0][0].findall(text):
            if int(a) > MAX_MONTH >= int(b):
                votes["dmy"] += 1
            elif int(b) > MAX_MONTH >= int(a):
                votes["mdy"] += 1
    top, other = sorted(("dmy", "mdy"), key=lambda k: -votes[k])
    return top if votes[top] >= MIN_VOTES and votes[other] * VOTE_RATIO <= votes[top] else ""


def _numeric_candidates(numeric: str, a: str, b: str, c: str) -> list[tuple[str, str, str]]:
    """(year, month, day) readings of a numeric date a-b-c in the given day/month order."""
    if numeric == "dmy":
        return [(c, b, a)]
    if numeric == "mdy":
        return [(c, a, b)]
    return [(c, b, a), (c, a, b)]


def dates_in(text: str, numeric: str = "") -> set[str]:
    found: set[str] = set()
    for pattern, order in DATES:
        for m in pattern.finditer(text):
            a, b, c = m.groups()
            if order == "dmy":
                candidates = _numeric_candidates(numeric, a, b, c)
            elif order == "ymd":
                candidates = [(a, b, c)]
            else:
                raw = f"{a} {b} {c}" if order == "dMy" else f"{b} {a} {c}"
                with contextlib.suppress(LedgerError):
                    found.add(parse_date(raw, "%d %b %Y"))
                continue
            for y, mo, d in candidates:
                with contextlib.suppress(ValueError):
                    found.add(date(int(y), int(mo), int(d)).isoformat())
    return found


def amounts_in(text: str, cells: list[str] | None = None) -> set[Decimal]:
    found: set[Decimal] = set()
    for token in cells if cells is not None else [m.group(0) for m in AMOUNT.finditer(text)]:
        try:
            found.add(abs(parse_amount(token)).quantize(CENT))
        except (LedgerError, ArithmeticError):
            continue
    return found


def source_entries(doc: Doc) -> list[Entry]:
    """Per source line: (dates, amounts, text)."""
    texts = [" ".join(r) for r in doc.table] if doc.table else doc.lines()
    numeric = numeric_order(texts)
    if doc.table:
        return [(dates_in(t, numeric), amounts_in("", r), " | ".join(r)) for t, r in zip(texts, doc.table, strict=True)]
    return [(dates_in(line, numeric), amounts_in(line), line) for line in texts]


def shifted(day: str, days: int) -> str:
    return (date.fromisoformat(day) + timedelta(days=days)).isoformat()


def match(rows: list[Row], entries: list[Entry]) -> tuple[dict[int, tuple[int, str]], set[int]]:  # noqa: C901 - ordered matching passes
    """Return (matches {row index: (line, how)}, used lines)."""
    pairs: dict[tuple[str, Decimal], list[int]] = {}
    for n, (ds, amts, _) in enumerate(entries):
        for d in ds:
            for a in amts:
                pairs.setdefault((d, a), []).append(n)
    used: set[int] = set()
    uses: Counter[tuple[tuple[str, Decimal], int]] = Counter()
    matches: dict[int, tuple[int, str]] = {}

    def take(key: tuple[str, Decimal], i: int, how: str) -> bool:
        for n in pairs.get(key, []):
            if uses[(key, n)] < 1:
                uses[(key, n)] += 1
                used.add(n)
                matches[i] = (n, how)
                return True
        return False

    wanted = [(i, r.date, abs(r.value).quantize(CENT)) for i, r in enumerate(rows, 1)]
    for i, d, a in wanted:
        take((d, a), i, "line")
    for i, d, a in wanted:
        if i not in matches:
            any(take((shifted(d, k), a), i, f"date+{k}") for k in range(1, DATE_SLACK + 1))
    for i, d, a in wanted:
        if i in matches:
            continue
        for n, (ds, _, _) in enumerate(entries):
            window = range(n, min(n + LINE_WINDOW + 1, len(entries)))
            if d in ds and n not in used and any(a in entries[k][1] for k in window):
                used.add(n)
                matches[i] = (n, "window")
                break
    return matches, used


def _balance_chain(led: Ledger, total: Decimal) -> dict[str, Any]:
    opening, closing = led.meta.get("opening-balance", "none"), led.meta.get("closing-balance", "none")
    if "none" in (opening, closing):
        return {"ok": None, "message": "no balances in the source"}
    expected = parse_value(opening) + total
    return {
        "ok": expected == parse_value(closing),
        "opening": opening,
        "sum": format_value(total),
        "closing": closing,
    }


def _spot_check(
    led: Ledger,
    entries: list[Entry],
    matches: dict[int, tuple[int, str]],
    seed: int,
    sample: int,
) -> list[dict[str, Any]]:
    picked = sorted(random.Random(seed).sample(sorted(matches), min(sample, len(matches))))  # noqa: S311 - deterministic spot check, not security
    return [
        {
            "row": i,
            "title": led.rows[i - 1].title,
            "value": format_value(led.rows[i - 1].value),
            "description": led.rows[i - 1].description,
            "source-line": entries[matches[i][0]][2][:SOURCE_LINE_CHARS],
        }
        for i in picked
    ]


def ground(
    store: LedgerStore,
    sources: Sources,
    registry: InstitutionRegistry,
    path: Path,
    sample: int,
) -> dict[str, Any]:
    led = ledger.read(store, path)
    normalizer = led.meta.get("normalizer", "")
    result: dict[str, Any] = {"file": path.name, "normalizer": normalizer, "rows": len(led.rows)}
    if normalizer == "llm-image":
        return {
            **result,
            "unverified": len(led.rows),
            "exit": 0,
            "warning": "image transcription: values cannot be grounded; report every row as unverified",
        }
    src = store.resolve_tmp(led.meta.get("source", ""))
    doc = sources.load(src)
    if not doc.has_text:
        msg = f"source {src.name} has no text to ground against"
        raise LedgerError(msg)
    entries = source_entries(doc)
    matches, used = match(led.rows, entries)
    unmatched = [
        {
            "row": i,
            "date": r.date,
            "value": format_value(r.value),
            "reason": "date and amount not found together in the source",
        }
        for i, r in enumerate(led.rows, 1)
        if i not in matches
    ]
    source_only = [
        {"line": n + 1, "dates": sorted(ds), "amounts": [str(a) for a in sorted(amts)]}
        for n, (ds, amts, _) in enumerate(entries)
        if ds and n not in used and any(a != 0 for a in amts)
    ]
    chain = _balance_chain(led, sum((r.value for r in led.rows), Decimal(0)))
    module_check: list[dict[str, Any]] = []
    if normalizer.startswith("module:"):
        module_check = registry.by_name(normalizer.split(":", 1)[1]).check(doc, led)
    seed = int(hashlib.sha256(store.read_bytes(src)).hexdigest()[:SEED_HEX_DIGITS], 16)
    ok = not unmatched and chain["ok"] is not False and all(f.get("ok") for f in module_check)
    how = Counter(h for _, h in matches.values())
    return {
        **result,
        "matched": len(matches),
        "matched-by": dict(how),
        "unmatched": unmatched,
        "source-only": source_only,
        "balance-chain": chain,
        "module-check": module_check,
        "sample": _spot_check(led, entries, matches, seed, sample),
        "exit": 0 if ok else 1,
    }


def grounding_path(path: Path) -> Path:
    return path.with_name(path.stem + ".grounding.json")


def write_grounding(store: LedgerStore, path: Path, result: dict[str, Any]) -> Path:
    out = grounding_path(path)
    write_json(store, out, result)
    return out
