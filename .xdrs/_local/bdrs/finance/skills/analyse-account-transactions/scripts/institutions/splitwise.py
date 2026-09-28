# Runtime: Python >=3.10; institution module imported by institutions/__init__.py.
"""Splitwise group CSV export as a shared-expenses pseudo-account.
Row value = the chosen person's balance change (positive = others owe them). Only the base currency is
kept; rows in other currencies are reported as notes so the analysis can mention them."""

from collections import Counter
from decimal import Decimal

import ledger
from ledger import LedgerError
from textutil import make_row, parse_amount, parse_date, title_from

NAME = "splitwise"
BANK = "Splitwise"
COUNTRY = ""
HEADER = ["Date", "Description", "Category", "Cost", "Currency"]
TOTAL = "Total balance"


def detect(doc) -> bool:
    return doc.kind == "table" and bool(doc.table) and [h.strip() for h in doc.table[0][:5]] == HEADER


def entries(table: list, col: int) -> list:
    """Data rows (not the total) with a non-zero share for the column."""
    result = []
    for r in table[1:]:
        if len(r) <= col or r[1].strip() == TOTAL or not r[0].strip():
            continue
        if r[col].strip() and parse_amount(r[col]) != 0:
            result.append(r)
    return result


def person_column(table: list, person: str, discover: bool = False) -> int:
    header = [h.strip() for h in table[0]]
    people = header[5:]
    if discover and person not in people and people:
        return 5
    if person not in people:
        raise LedgerError(f"Splitwise export: set account-holder to one of {people}")
    return header.index(person)


def parse(doc, opts: dict) -> tuple:
    """opts: account-holder (required, a member name), currency (base; default: most used),
    discover (use the first member when account-holder is missing; for period discovery only)."""
    table = doc.table
    col = person_column(table, opts.get("account-holder", ""), opts.get("discover", False))
    header = [h.strip() for h in table[0]]
    others = [(i, h) for i, h in enumerate(header) if i >= 5 and i != col]
    data = entries(table, col)
    currency = opts.get("currency") or (Counter(r[4].strip() for r in data).most_common(1) or [("EUR", 0)])[0][0]
    rows, total, skipped = [], None, Counter()
    for r in table[1:]:
        if len(r) <= col:
            continue
        if r[4].strip() != currency:
            if r in data:
                skipped[r[4].strip()] += 1
            continue
        if r[1].strip() == TOTAL:
            total = parse_amount(r[col])
            continue
        if r not in data:
            continue
        shares = "; ".join(f"{h} {r[i]}" for i, h in others)
        desc = f"Splitwise {r[1].strip()}; category {r[2].strip()}; cost {r[3]} {currency}; {shares}"
        rows.append(make_row(parse_date(r[0]), parse_amount(r[col]), desc, title=title_from(r[1], keep_digits=True)))
    moved = sum((r.value for r in rows), Decimal(0))
    # a date-range export omits older rows; the total balance line is authoritative for the closing balance
    closing = moved if total is None else total
    meta = {"bank": BANK, "account-type": "shared-expenses", "account-holder": header[col], "iban": "none",
            "currency": currency, "opening-balance": ledger.format_value(closing - moved),
            "closing-balance": ledger.format_value(closing)}
    notes = [f"skipped {n} row(s) in {cur} (not the base currency {currency})" for cur, n in sorted(skipped.items())]
    if opts.get("discover"):
        notes.append(f"members (set account-holder to one): {', '.join(header[5:])}")
    return meta, rows, notes


def check(doc, led) -> list:
    """Every non-zero base-currency row of the person inside the ledger period must be in the ledger."""
    col = person_column(doc.table, led.meta.get("account-holder", ""))
    start, _, end = led.meta.get("period", "..").partition("..")
    expected = 0
    for r in entries(doc.table, col):
        if r[4].strip() == led.meta.get("currency"):
            day = parse_date(r[0])
            expected += int((not start or day >= start) and (not end or day <= end))
    return [{"check": "row-count", "ok": expected == len(led.rows), "expected": expected, "found": len(led.rows)}]
