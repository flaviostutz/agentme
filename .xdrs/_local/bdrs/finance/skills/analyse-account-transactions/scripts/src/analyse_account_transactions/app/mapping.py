"""Apply an LLM-written column mapping (mapping.json) to a table from an unknown CSV/TXT/XLSX export.

{
  "delimiter": ";",                  optional, re-reads the text with this delimiter (CSV/TXT only)
  "header-row": 1,                   optional, 1-based row holding the column names (default 1)
  "date": {"column": "Boekdatum", "format": "%d-%m-%Y"},      format "excel" for serial day numbers
  "amount": {"column": "Bedrag", "decimal": ","}              or {"debit": "Paid out", "credit": "Paid in"}
  "sign": {"column": "Af Bij", "debit": ["Af"]},              optional, when amounts are unsigned
  "description": ["Naam", "Omschrijving"],                    joined with ' '
  "title": "Naam",                                            optional, short counterparty column
  "currency": {"column": "Munt"},                             optional, rows in other currencies are skipped
  "meta": {"bank": "...", "iban": "...", "currency": "EUR", "account-holder": "..."}
}
Rows with an empty date cell are skipped (footers); any other unreadable cell is an error.
"""

import csv
import io
from collections.abc import Callable
from decimal import Decimal
from typing import Any

from analyse_account_transactions.app.textutil import excel_serial, make_row, parse_amount, parse_date
from analyse_account_transactions.shared.constants import META_KEYS
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Doc, ParseResult, Row

KEYS = {"delimiter", "header-row", "date", "amount", "sign", "description", "title", "currency", "meta"}


def column(header: list[str], name: str, what: str) -> int:
    if name not in header:
        msg = f"mapping {what}: column {name!r} not in header {header}"
        raise LedgerError(msg)
    return header.index(name)


def amount_of(text: str, decimal: str) -> Decimal:
    s = text.strip()
    if decimal == ",":
        s = s.replace(".", "").replace(",", ".")
    elif decimal == ".":
        s = s.replace(",", "")
    return parse_amount(s)


def table_for(doc: Doc, mapping: dict[str, Any]) -> list[list[str]]:
    if "delimiter" in mapping and doc.texts:
        reader = csv.reader(io.StringIO(doc.texts[0]), delimiter=mapping["delimiter"])
        return [[c.strip() for c in r] for r in reader if any(c.strip() for c in r)]
    return doc.table


def validate(mapping: dict[str, Any]) -> None:
    if not isinstance(mapping, dict):
        msg = "mapping must be a JSON object"
        raise LedgerError(msg)
    unknown = set(mapping) - KEYS
    if unknown:
        msg = f"mapping: unknown keys {sorted(unknown)}"
        raise LedgerError(msg)
    for key in ("date", "amount", "description"):
        if key not in mapping:
            msg = f"mapping: '{key}' is required"
            raise LedgerError(msg)
    amount = mapping["amount"]
    if not ("column" in amount or {"debit", "credit"} <= set(amount)):
        msg = "mapping amount: needs 'column' or both 'debit' and 'credit'"
        raise LedgerError(msg)
    bad = set(mapping.get("meta", {})) - set(META_KEYS[1:])
    if bad:
        msg = f"mapping meta: unknown keys {sorted(bad)}"
        raise LedgerError(msg)


def _amount(get: Callable[[int | None], str], cols: dict[str, int], decimal: str) -> Decimal:
    """The amount of one row from a single column or from separate debit/credit columns."""
    if "column" in cols:
        return amount_of(get(cols["column"]), decimal)
    if get(cols["credit"]):
        return abs(amount_of(get(cols["credit"]), decimal))
    return -abs(amount_of(get(cols["debit"]), decimal))


def apply(doc: Doc, mapping: dict[str, Any]) -> ParseResult:
    """Return (meta, rows, notes)."""
    validate(mapping)
    table = table_for(doc, mapping)
    start = int(mapping.get("header-row", 1))
    if not 1 <= start <= len(table):
        msg = f"mapping header-row {start} outside the table (1..{len(table)})"
        raise LedgerError(msg)
    header = table[start - 1]
    date_col = column(header, mapping["date"]["column"], "date")
    fmt = mapping["date"].get("format", "")
    amount = mapping["amount"]
    decimal = amount.get("decimal", "")
    cols = {k: column(header, amount[k], f"amount {k}") for k in ("column", "debit", "credit") if k in amount}
    desc_cols = [column(header, c, "description") for c in mapping["description"]]
    title_col = column(header, mapping["title"], "title") if "title" in mapping else None
    sign = mapping.get("sign")
    sign_col = column(header, sign["column"], "sign") if sign else None
    debit_words = {w.lower() for w in (sign or {}).get("debit", [])}
    meta = dict(mapping.get("meta", {}))
    cur = mapping.get("currency")
    cur_col = column(header, cur["column"], "currency") if cur else None
    rows: list[Row] = []
    skipped = 0
    other: dict[str, int] = {}
    for n, r in enumerate(table[start:], start + 1):

        def cell(i: int | None, r: list[str] = r) -> str:
            return r[i].strip() if i is not None and i < len(r) else ""

        if not cell(date_col):
            skipped += 1
            continue
        try:
            day = excel_serial(cell(date_col)) if fmt == "excel" else parse_date(cell(date_col), fmt)
            value = _amount(cell, cols, decimal)
        except (LedgerError, ValueError) as err:
            msg = f"row {n}: {err}"
            raise LedgerError(msg) from err
        if sign_col is not None:
            value = -abs(value) if cell(sign_col).lower() in debit_words else abs(value)
        if cur_col is not None:
            meta.setdefault("currency", cell(cur_col))
            if cell(cur_col) != meta["currency"]:
                other[cell(cur_col)] = other.get(cell(cur_col), 0) + 1
                continue
        desc = " ".join(cell(i) for i in desc_cols if cell(i))
        rows.append(make_row(day, value, desc, title=cell(title_col)))
    notes = [f"skipped {skipped} row(s) without a date"] if skipped else []
    notes += [f"skipped {k} row(s) in {c} (not {meta['currency']})" for c, k in sorted(other.items())]
    return meta, rows, notes
