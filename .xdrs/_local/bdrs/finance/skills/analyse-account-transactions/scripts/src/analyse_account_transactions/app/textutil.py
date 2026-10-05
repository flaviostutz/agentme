"""Generic value, date and title helpers shared by the normalizer and the institution modules."""

import re
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from analyse_account_transactions.app.ledger import clip_description
from analyse_account_transactions.shared.constants import MAX_TITLE_WORDS
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Row

MINUS_SIGNS = "\u2212\u2012\u2013"
DATE_FORMATS = (
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%Y%m%d",
    "%d.%m.%Y",
    "%d-%m-%y",
    "%d/%m/%y",
    "%b %d, %Y",
    "%B %d, %Y",
    "%d %b %Y",
    "%d %B %Y",
)
# payment-processor prefixes seen on card rows of many banks (e.g. 'CCV*SHOP', 'SumUp *Cafe', 'SQ *BAR')
PROCESSOR_PREFIX = re.compile(r"^(?:[A-Za-z]{2,4} ?\*|SumUp \*|Zettle_\*|PAYPAL \*)\s*", re.IGNORECASE)
LEGAL_SUFFIX = re.compile(r"(?i)^(?:b\.?v\.?|n\.?v\.?|ltd\.?|gmbh|inc\.?|llc|sarl|sca|ag|s\.?a\.?|plc)$")
EXCEL_EPOCH = date(1899, 12, 30)
LINE_TOLERANCE = 2


def parse_amount(text: str) -> Decimal:
    """Parse '1.234,56', '1,234.56', '-12,34', '+1.500,00€', '12,50-', '(12.50)', '<minus sign>3.00' or 'EUR 1.234'."""
    s = str(text).strip()
    for ch in MINUS_SIGNS:
        s = s.replace(ch, "-")
    s = re.sub(r"[A-Za-z€$£¥\s\u00a0']", "", s)
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg, s = True, s[1:-1]
    if s.startswith("-") or s.endswith("-"):
        neg = True
    s = s.strip("+-")
    if re.search(r",\d{1,2}$", s):
        s = s.replace(".", "").replace(",", ".")
    elif re.search(r"\.\d{1,2}$", s):
        s = s.replace(",", "")
    else:
        s = s.replace(",", "").replace(".", "")
    if not re.fullmatch(r"\d+(?:\.\d+)?", s):
        msg = f"not an amount: {text!r}"
        raise LedgerError(msg)
    value = Decimal(s)
    return -value if neg else value


def parse_date(text: str, fmt: str = "") -> str:
    """Return YYYY-MM-DD; fmt forces one strptime format, otherwise day-first formats are tried in order."""
    raw = str(text).strip()
    for f in (fmt,) if fmt else DATE_FORMATS:
        try:
            return datetime.strptime(raw, f).replace(tzinfo=UTC).strftime("%Y-%m-%d")
        except ValueError:
            continue
    msg = f"unrecognised date: {text!r}" + (f" (format {fmt})" if fmt else "")
    raise LedgerError(msg)


def excel_serial(value: str | float) -> str:
    """Excel serial day number (e.g. 45901) to YYYY-MM-DD."""
    return (EXCEL_EPOCH + timedelta(days=int(float(value)))).isoformat()


def group_lines(words: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Group pdfplumber words (dicts with text, x0, x1, top) into lines sorted left to right."""
    lines: list[list[dict[str, Any]]] = []
    for w in sorted(words, key=lambda w: (round(w["top"]), w["x0"])):
        if lines and abs(lines[-1][0]["top"] - w["top"]) <= LINE_TOLERANCE:
            lines[-1].append(w)
        else:
            lines.append([w])
    return [sorted(line, key=lambda w: w["x0"]) for line in lines]


def title_from(text: str, *, keep_digits: bool = False) -> str:
    """Short counterparty title: drops processor prefixes and '*order' references.

    Unless keep_digits, also drops digit-only words and legal suffixes (use keep_digits for layouts where the title
    is clean).
    """
    text = PROCESSOR_PREFIX.sub("", text.strip())
    words = []
    for w in text.replace(",", " ").split():
        w = re.sub(r"\*.*$", "", w)  # noqa: PLW2901 - the word is cleaned in place
        if not keep_digits and re.search(r"\d", w):
            m = re.search(r"[A-Z][a-z][^\d]*$", w)
            w = m.group(0) if m else ""  # noqa: PLW2901
        if w and (keep_digits or not LEGAL_SUFFIX.match(w)):
            words.append(w)
    return " ".join(words[:MAX_TITLE_WORDS]).strip(" .*,") or "Unnamed"


def make_row(day: str, value: Decimal, description: str, title: str = "", timestamp: str = "") -> Row:
    desc = clip_description(description)
    short = " ".join((title or title_from(desc)).split()[:MAX_TITLE_WORDS]) or "Unnamed"
    return Row(timestamp or day, short, value, desc)


def slug(text: str) -> str:
    """Safe file-name part: letters, digits, '.', '_', '-'."""
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-.")
    return s.lower() or "file"


def month_end(day: date) -> date:
    return (day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)


def months(period: str) -> set[str]:
    """'YYYY-MM-DD..YYYY-MM-DD' to the set of 'YYYY-MM' it touches."""
    start, _, end = period.partition("..")
    cur, last, result = date.fromisoformat(start).replace(day=1), date.fromisoformat(end), set()
    while cur <= last:
        result.add(cur.strftime("%Y-%m"))
        cur = month_end(cur) + timedelta(days=1)
    return result
