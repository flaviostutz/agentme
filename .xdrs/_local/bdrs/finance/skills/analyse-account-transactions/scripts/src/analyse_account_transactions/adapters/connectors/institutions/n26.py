"""N26 (DE, BIC NTSBDEB1): monthly PDF account statements."""

import re
from decimal import Decimal
from typing import Any

from analyse_account_transactions.app.textutil import make_row, parse_amount, parse_date, title_from
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Doc, Institution, Ledger, ParseResult
from analyse_account_transactions.shared.values import format_value

NAME = "n26"
BANK = "N26"
COUNTRY = "DE"
ROW = re.compile(r"^(?P<desc>.+?) (?P<date>\d{2}\.\d{2}\.\d{4}) (?P<amount>[+-]?\d{1,3}(?:\.\d{3})*,\d{2})€$")
SKIP = re.compile(r"^Value Date \d{2}\.\d{2}\.\d{4}$")
TABLE_START = "Description Booking Date Amount"
MONEY = r"([+-]?[\d.]+,\d{2})€"
ISSUED_ON = "Issued on"


def detect(doc: Doc) -> bool:
    return doc.kind == "pdf" and bool(doc.texts) and "NTSBDEB1" in doc.texts[0]


def _collect(doc: Doc, meta: dict[str, str]) -> list[dict[str, Any]]:
    """Transaction entries {date, value, head, details} of all pages; fills the account holder in meta."""
    found: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for text in doc.texts:
        lines = text.splitlines()
        cut = next((i for i, line in enumerate(lines) if line.endswith(ISSUED_ON)), len(lines))
        if cut < len(lines):
            meta.setdefault("account-holder", lines[cut][: -len(ISSUED_ON)].strip())
        if lines and lines[0].startswith("Overview"):
            current = None
            continue
        in_table = False
        for line in lines[:cut]:
            if line.startswith(TABLE_START):
                in_table = True
                continue
            if not in_table or SKIP.match(line):
                continue
            m = ROW.match(line)
            if m:
                current = {
                    "date": parse_date(m["date"]),
                    "value": parse_amount(m["amount"]),
                    "head": m["desc"],
                    "details": [],
                }
                found.append(current)
            elif current is not None:
                current["details"].append(line)
    return found


def parse(doc: Doc, _opts: dict[str, Any]) -> ParseResult:
    """Return (meta, rows, notes)."""
    meta = {"bank": BANK, "account-type": "current", "currency": "EUR"}
    found = _collect(doc, meta)
    joined = "\n".join(doc.texts)
    # the account IBAN is in the page footer, right above the page number; other IBANs are counterparties
    m = re.search(r"IBAN: (\S+) • BIC: \S+(?: Nr\. \d{2}/\d{4})?\n\d+ / \d+$", "\n".join(doc.lines()), re.MULTILINE)
    if m:
        meta["iban"] = m.group(1)
    m = re.search(r"(\d{2}\.\d{2}\.\d{4}) until (\d{2}\.\d{2}\.\d{4})", joined)
    if m:
        meta["period"] = f"{parse_date(m.group(1))}..{parse_date(m.group(2))}"
    for key, label in (("opening-balance", "Previous balance"), ("closing-balance", "Your new balance")):
        m = re.search(f"{label} {MONEY}", joined)
        if m:
            meta[key] = format_value(parse_amount(m.group(1)))
    if not found:
        msg = "N26 statement without transaction rows"
        raise LedgerError(msg)
    rows = [
        make_row(
            r["date"],
            r["value"],
            " ".join([r["head"], *r["details"]]),
            title=title_from(r["head"], keep_digits=True),
        )
        for r in found
    ]
    return meta, rows, []


def check(doc: Doc, led: Ledger) -> list[dict[str, Any]]:
    """Compare the 'Outgoing/Incoming transactions' summary with the ledger sums."""
    joined = "\n".join(doc.texts)
    findings: list[dict[str, Any]] = []
    for name, label, values in (
        ("outgoing", "Outgoing transactions", [r.value for r in led.rows if r.value < 0]),
        ("incoming", "Incoming transactions", [r.value for r in led.rows if r.value >= 0]),
    ):
        m = re.search(f"{label} {MONEY}", joined)
        if not m:
            findings.append({"check": name, "ok": False, "message": f"'{label}' summary not found"})
            continue
        expected, found = parse_amount(m.group(1)), sum(values, Decimal(0))
        findings.append({"check": name, "ok": expected == found, "expected": str(expected), "found": str(found)})
    return findings


INSTITUTION = Institution(name=NAME, bank=BANK, country=COUNTRY, detect=detect, parse=parse, check=check)
