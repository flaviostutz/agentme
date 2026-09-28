# Runtime: Python >=3.10, stdlib only; imported by normalize.py.
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
Rows with an empty date cell are skipped (footers); any other unreadable cell is an error."""

import csv
import io

import ledger
from ledger import LedgerError
from textutil import excel_serial, make_row, parse_amount, parse_date

KEYS = {"delimiter", "header-row", "date", "amount", "sign", "description", "title", "currency", "meta"}


def column(header: list, name: str, what: str) -> int:
    if name not in header:
        raise LedgerError(f"mapping {what}: column {name!r} not in header {header}")
    return header.index(name)


def amount_of(text: str, decimal: str):
    s = text.strip()
    if decimal == ",":
        s = s.replace(".", "").replace(",", ".")
    elif decimal == ".":
        s = s.replace(",", "")
    return parse_amount(s)


def table_for(doc, mapping: dict) -> list:
    if "delimiter" in mapping and doc.texts:
        reader = csv.reader(io.StringIO(doc.texts[0]), delimiter=mapping["delimiter"])
        return [[c.strip() for c in r] for r in reader if any(c.strip() for c in r)]
    return doc.table


def validate(mapping: dict) -> None:
    if not isinstance(mapping, dict):
        raise LedgerError("mapping must be a JSON object")
    unknown = set(mapping) - KEYS
    if unknown:
        raise LedgerError(f"mapping: unknown keys {sorted(unknown)}")
    for key in ("date", "amount", "description"):
        if key not in mapping:
            raise LedgerError(f"mapping: '{key}' is required")
    amount = mapping["amount"]
    if not ("column" in amount or {"debit", "credit"} <= set(amount)):
        raise LedgerError("mapping amount: needs 'column' or both 'debit' and 'credit'")
    meta = mapping.get("meta", {})
    bad = set(meta) - set(ledger.META_KEYS[1:])
    if bad:
        raise LedgerError(f"mapping meta: unknown keys {sorted(bad)}")


def apply(doc, mapping: dict) -> tuple:
    """Return (meta, rows, notes)."""
    validate(mapping)
    table = table_for(doc, mapping)
    start = int(mapping.get("header-row", 1))
    if not 1 <= start <= len(table):
        raise LedgerError(f"mapping header-row {start} outside the table (1..{len(table)})")
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
    rows, skipped, other = [], 0, {}
    for n, r in enumerate(table[start:], start + 1):
        def cell(i, r=r):
            return r[i].strip() if i is not None and i < len(r) else ""
        if not cell(date_col):
            skipped += 1
            continue
        try:
            day = excel_serial(cell(date_col)) if fmt == "excel" else parse_date(cell(date_col), fmt)
            if "column" in cols:
                value = amount_of(cell(cols["column"]), decimal)
            elif cell(cols["credit"]):
                value = abs(amount_of(cell(cols["credit"]), decimal))
            else:
                value = -abs(amount_of(cell(cols["debit"]), decimal))
        except (LedgerError, ValueError) as err:
            raise LedgerError(f"row {n}: {err}") from err
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
