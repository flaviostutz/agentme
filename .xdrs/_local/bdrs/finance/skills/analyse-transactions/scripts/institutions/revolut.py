# Runtime: Python >=3.10; institution module imported by institutions/__init__.py.
"""Revolut Bank UAB: PDF account statements (current account table with Money out / Money in / Balance)."""

import re
from decimal import Decimal

import ledger
from ledger import LedgerError
from textutil import group_lines, make_row, parse_amount, parse_date, title_from

NAME = "revolut"
BANK = "Revolut"
COUNTRY = "LT"
DATE = re.compile(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$")
AMOUNT = re.compile(r"^[€$£]\d{1,3}(?:,\d{3})*\.\d{2}$")
STOP = ("Report lost or stolen card", "Pending from")
PREFIX = re.compile(r"^(?:Payment from|Refund from|Transfer from|Transfer to|To)\s+")
SUMMARY = re.compile(r"^Account \(Current Account\) (\S+) (\S+) (\S+) (\S+)$", re.MULTILINE)


def detect(doc) -> bool:
    return doc.kind == "pdf" and bool(doc.texts) and "Revolut Bank" in doc.texts[0]


def columns(line: list):
    texts = [w["text"] for w in line]
    if texts[:2] != ["Date", "Description"] or "Balance" not in texts:
        return None
    outs = [w for i, w in enumerate(line) if w["text"] == "out" and i and line[i - 1]["text"] == "Money"]
    ins = [w for i, w in enumerate(line) if w["text"] == "in" and i and line[i - 1]["text"] == "Money"]
    if not outs or not ins:
        return None
    return {"out": outs[0]["x1"], "in": ins[0]["x1"], "balance": line[-1]["x1"]}


def meta_from_text(text: str) -> dict:
    meta = {"bank": BANK, "account-type": "current"}
    m = re.search(r"^([A-Z]{3}) Statement", text, re.MULTILINE)
    if m:
        meta["currency"] = m.group(1)
    m = re.search(r"IBAN (\S+)", text)
    if m:
        meta["iban"] = m.group(1)
    m = re.search(r"^Revolut Bank UAB.*\n(.+)", text, re.MULTILINE)
    if m:
        meta["account-holder"] = m.group(1).strip()
    m = re.search(r"from ([A-Z][a-z]+ \d{1,2}, \d{4}) to ([A-Z][a-z]+ \d{1,2}, \d{4})", text)
    if m:
        meta["period"] = f"{parse_date(m.group(1))}..{parse_date(m.group(2))}"
    m = SUMMARY.search(text)
    if m:
        meta["opening-balance"] = ledger.format_value(parse_amount(m.group(1)))
        meta["closing-balance"] = ledger.format_value(parse_amount(m.group(4)))
    return meta


def parse(doc, opts: dict) -> tuple:
    """Return (meta, rows, notes)."""
    found, current, stop = [], None, False
    for words in doc.words:
        cols = None
        for line in group_lines(words):
            text = " ".join(w["text"] for w in line)
            if text.startswith(STOP):
                stop = True
                break
            if cols is None:
                cols = columns(line)
                continue
            head = " ".join(w["text"] for w in line[:3])
            if DATE.match(head):
                current = {"date": parse_date(head), "head": [], "details": [], "out": [], "in": []}
                found.append(current)
                for w in line[3:]:
                    if AMOUNT.match(w["text"]):
                        near = min(cols, key=lambda k: abs(cols[k] - w["x1"]))
                        if near != "balance":
                            current[near].append(w["text"])
                    else:
                        current["head"].append(w["text"])
            elif current is not None:
                current["details"].append(text)
        if stop:
            break
    rows = []
    for r in found:
        if len(r["out"]) + len(r["in"]) != 1:
            raise LedgerError(f"Revolut row {r['date']}: expected one amount, found {r['out'] + r['in']}")
        value = -parse_amount(r["out"][0]) if r["out"] else parse_amount(r["in"][0])
        head = " ".join(r["head"])
        rows.append(make_row(r["date"], value, " ".join([head] + r["details"]),
                             title=title_from(PREFIX.sub("", head), keep_digits=True)))
    return meta_from_text(doc.texts[0]), rows, []


def check(doc, led) -> list:
    """Compare the 'Account (Current Account)' summary (opening, out, in, closing) with the ledger sums."""
    m = SUMMARY.search(doc.texts[0])
    if not m:
        return [{"check": "summary", "ok": False, "message": "'Account (Current Account)' summary not found"}]
    out, inc = parse_amount(m.group(2)), parse_amount(m.group(3))
    found_out = -sum((r.value for r in led.rows if r.value < 0), Decimal(0))
    found_in = sum((r.value for r in led.rows if r.value >= 0), Decimal(0))
    return [{"check": "money-out", "ok": out == found_out, "expected": str(out), "found": str(found_out)},
            {"check": "money-in", "ok": inc == found_in, "expected": str(inc), "found": str(found_in)}]
