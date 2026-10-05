"""ABN AMRO (NL): PDF account statements and the tab-separated transaction export without header."""

import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from analyse_account_transactions.app import ledger
from analyse_account_transactions.app.textutil import group_lines, make_row, parse_amount, parse_date, title_from
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Doc, Institution, Ledger, ParseResult, Row
from analyse_account_transactions.shared.values import format_value

NAME = "abn_amro"
BANK = "ABN AMRO"
COUNTRY = "NL"
DATE_WORD = re.compile(r"^\d{2}-\d{2}-\d{4}$")
AMOUNT_WORD = re.compile(r"^-?\d{1,3}(?:[.,]\d{3})*[.,]\d{2}-?$")
PURCHASE_TIME = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{2})/(\d{2}):(\d{2})\b")
DEBIT_HEADERS = {"debited", "af", "debit", "debet", "afgeschreven"}
CREDIT_HEADERS = {"credited", "bij", "credit", "bijgeschreven"}
STOP_LINES = ("Number of debit", "Total amount debited", "Aantal af", "Totaal afgeschreven")
COLUMN_TOLERANCE = 4
DATE_COLUMN_SLACK = 10
EXPORT_COLUMNS = 8
TITLE_PATTERNS = [
    r"/N ?A ?M ?E ?/([^/]+)/",
    r"Naam: (.+?)(?=Omschrijving:|Machtiging:|Kenmerk:| IBAN:| BIC:|$)",
    r"^BEA, (?:Apple Pay |Google Pay |Betaalpas )?(.+?)(?:,PAS| NR:|$)",
]
COUNTS = re.compile(r"Number of debit Number of credit\s*\ntransactions transactions\s*\n(\d+) (\d+)")
TOTALS = re.compile(r"Total amount debited Total amount credited\s*\n(?:Balance \S+ )?(?:€ ?\S+ )?€ ?(\S+) € ?(\S+)")


def detect(doc: Doc) -> bool:
    if doc.kind == "pdf" and doc.texts:
        return ("ABNANL2A" in doc.texts[0] or "ABN AMRO" in doc.texts[0]) and "Date interval" in doc.texts[0]
    if doc.kind == "table" and doc.table:
        first = doc.table[0]
        return (
            len(first) >= EXPORT_COLUMNS
            and bool(re.fullmatch(r"\d{8}", first[2]))
            and bool(re.fullmatch(r"[A-Z]{3}", first[1]))
        )
    return False


def timestamp_for(day: str, description: str) -> str:
    m = PURCHASE_TIME.search(description)
    if not m:
        return day
    dd, mm, yy, hh, mi = m.groups()
    try:
        return datetime(2000 + int(yy), int(mm), int(dd), int(hh), int(mi), tzinfo=UTC).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return day


def title(description: str) -> str:
    if description.startswith("GEA,"):
        return "Cash withdrawal"
    match = next((m for m in (re.search(p, description) for p in TITLE_PATTERNS) if m), None)
    found = title_from(match.group(1) if match else description)
    if found == "Unnamed" and match:
        found = title_from(match.group(1), keep_digits=True)
    if found == "Unnamed":
        m = re.search(r"\d{2}:\d{2} (\S+)", description)
        found = m.group(1) if m else found
    return found


def row(day: str, value: Decimal, description: str) -> Row:
    desc = ledger.clip_description(description)
    return make_row(day, value, desc, title=title(desc), timestamp=timestamp_for(day, desc))


def find_columns(line: list[dict[str, Any]]) -> dict[str, float] | None:
    texts = {w["text"].lower(): w for w in line}
    desc = texts.get("description") or texts.get("omschrijving")
    debit = next((texts[t] for t in DEBIT_HEADERS if t in texts), None)
    credit = next((texts[t] for t in CREDIT_HEADERS if t in texts), None)
    if desc and debit and credit:
        return {"desc_x0": desc["x0"], "debit_x1": debit["x1"], "credit_x1": credit["x1"]}
    return None


def _collect(pages: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:  # noqa: C901 - one branch per layout element
    """Group the words of the pages into rows {date, desc, debit, credit}; amounts go to a column by right edge."""
    found: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for words in pages:
        cols = None
        stop = False
        for line in group_lines(words):
            text = " ".join(w["text"] for w in line)
            if text.startswith(STOP_LINES):
                stop = True
                break
            if cols is None:
                cols = find_columns(line)
                continue
            first = line[0]
            if DATE_WORD.match(first["text"]) and first["x0"] < cols["desc_x0"] - DATE_COLUMN_SLACK:
                current = {"date": parse_date(first["text"]), "desc": [], "debit": [], "credit": []}
                found.append(current)
                line = line[1:]  # noqa: PLW2901 - the date word is consumed
            if current is None:
                continue
            for w in line:
                if AMOUNT_WORD.match(w["text"]) and abs(w["x1"] - cols["debit_x1"]) <= COLUMN_TOLERANCE:
                    current["debit"].append(w["text"])
                elif AMOUNT_WORD.match(w["text"]) and abs(w["x1"] - cols["credit_x1"]) <= COLUMN_TOLERANCE:
                    current["credit"].append(w["text"])
                else:
                    current["desc"].append(w["text"])
        if stop:
            break
    return found


def rows_from_words(pages: list[list[dict[str, Any]]]) -> list[Row]:
    """pages: pdfplumber word lists; amounts go to the debit or credit column by their right edge."""
    result = []
    for n, r in enumerate(_collect(pages), 1):
        if len(r["debit"]) + len(r["credit"]) != 1:
            msg = f"row {n} ({r['date']}): expected one amount, found {r['debit'] + r['credit']}"
            raise LedgerError(msg)
        value = -parse_amount(r["debit"][0]) if r["debit"] else parse_amount(r["credit"][0])
        result.append(row(r["date"], value, " ".join(r["desc"])))
    return result


def meta_from_text(text: str) -> dict[str, str]:
    meta = {"bank": BANK}
    m = re.search(r"Account holder name (.+?)(?:\n(.+))?\n", text)
    if m:
        holder = m.group(1) + (" " + m.group(2) if m.group(1).endswith("and/or") and m.group(2) else "")
        meta["account-holder"] = holder.strip()
    m = re.search(r"^(Personal Account|Savings Account|Business Account|Betaalrekening) (\S+)", text, re.MULTILINE)
    if m:
        meta["account-type"] = "savings" if "Savings" in m.group(1) else "current"
        meta["iban"] = m.group(2)
    m = re.search(r"Date interval (\d{2}-\d{2}-\d{4}) until (\d{2}-\d{2}-\d{4})", text)
    if m:
        meta["period"] = f"{parse_date(m.group(1))}..{parse_date(m.group(2))}"
    balances = re.findall(r"Balance \d{2}-\d{2}-\d{4} €\s*(-?[\d.,]+-?)", text)
    if len(balances) >= 2:  # noqa: PLR2004 - opening and closing
        meta["opening-balance"] = format_value(parse_amount(balances[0]))
        meta["closing-balance"] = format_value(parse_amount(balances[1]))
    if "€" in text:
        meta["currency"] = "EUR"
    return meta


def parse(doc: Doc, _opts: dict[str, Any]) -> ParseResult:
    """Return (meta, rows, notes)."""
    if doc.kind == "pdf":
        return meta_from_text(doc.texts[0]), rows_from_words(doc.words), []
    table = doc.table
    rows = [row(parse_date(r[2]), parse_amount(r[6]), r[7]) for r in table]
    meta = {
        "bank": BANK,
        "iban": table[0][0],
        "currency": table[0][1],
        "account-type": "current",
        "opening-balance": format_value(parse_amount(table[0][3])),
        "closing-balance": format_value(parse_amount(table[-1][4])),
    }
    return meta, rows, []


def check(doc: Doc, led: Ledger) -> list[dict[str, Any]]:
    """Compare the statement summary (debit/credit counts and totals) with the ledger rows."""
    if doc.kind != "pdf":
        return []
    text = doc.texts[0]
    debits = [r.value for r in led.rows if r.value < 0]
    incoming = [r.value for r in led.rows if r.value >= 0]
    findings: list[dict[str, Any]] = []
    m = COUNTS.search(text)
    if not m:
        findings.append({"check": "counts", "ok": False, "message": "summary counts not found on page 1"})
    else:
        expected = (int(m.group(1)), int(m.group(2)))
        ok = expected == (len(debits), len(incoming))
        findings.append(
            {"check": "counts", "ok": ok, "expected": list(expected), "found": [len(debits), len(incoming)]}
        )
    m = TOTALS.search(text)
    if not m:
        findings.append({"check": "totals", "ok": False, "message": "summary totals not found on page 1"})
    else:
        expected_totals = (parse_amount(m.group(1)), parse_amount(m.group(2)))
        found = (-sum(debits, Decimal(0)), sum(incoming, Decimal(0)))
        findings.append(
            {
                "check": "totals",
                "ok": expected_totals == found,
                "expected": [str(v) for v in expected_totals],
                "found": [str(v) for v in found],
            },
        )
    return findings


INSTITUTION = Institution(name=NAME, bank=BANK, country=COUNTRY, detect=detect, parse=parse, check=check)
