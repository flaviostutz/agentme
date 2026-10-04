# Runtime: Python >=3.10; shared helpers imported by adapters, ingest and reports. Pure functions, no I/O.
"""Parsing of money, numbers and dates as printed on broker statements."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation

from sourcedoc import PmError

MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
CURRENCY_MARKS = (("US$", "USD"), ("R$", "BRL"), ("€", "EUR"), ("$", "USD"), ("£", "GBP"))
CURRENCY_CODES = ("EUR", "USD", "BRL", "GBP", "CHF", "CAD")
_MONEY = re.compile(r"^(?P<s1>[-+])?\s*(?P<mark>US\$|R\$|€|\$|£)?\s*(?P<s2>[-+])?\s*(?P<num>\d[\d.,]*)\s*(?P<code>[A-Z]{3})?\s*(?P<s3>-)?$")
ZERO = Decimal(0)
CENT = Decimal("0.01")


def parse_number(text: str, decimal: str = ".") -> Decimal:
    """Parse '1,234.50' (decimal='.') or '1.234,50' (decimal=','); a trailing '-' means negative."""
    s = text.strip()
    negative = s.endswith("-") or s.startswith("-")
    s = s.strip("-+ ")
    if decimal == ",":
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        value = Decimal(s)
    except InvalidOperation as err:
        raise PmError(f"not a number: {text!r}") from err
    return -value if negative else value


def parse_money(text: str, decimal: str = ".", default_currency: str = "") -> tuple:
    """Return (currency, Decimal) from '-€2.21', 'US$0', '$1,064.91', 'R$ -337,38', '1.243,23 EUR' or '1,306.68-'."""
    m = _MONEY.match(text.strip())
    if not m:
        raise PmError(f"not a money amount: {text!r}")
    mark, code = m.group("mark"), m.group("code")
    currency = default_currency
    if mark:
        currency = dict(CURRENCY_MARKS)[mark]
    elif code in CURRENCY_CODES:
        currency = code
    elif code:
        raise PmError(f"unknown currency code in {text!r}")
    negative = "-" in (m.group("s1") or "") + (m.group("s2") or "") + (m.group("s3") or "")
    value = parse_number(m.group("num"), decimal)
    return currency, -value if negative else value


def is_money(text: str, decimal: str = ".") -> bool:
    try:
        parse_money(text, decimal)
    except PmError:
        return False
    return True


def parse_rate(text: str) -> Decimal:
    return parse_number(text)


def iso(day: date) -> str:
    return day.isoformat()


def parse_date(text: str, fmt: str) -> date:
    """fmt: 'dd/mm/yyyy', 'dd.mm.yyyy', 'yyyy-mm-dd' or 'dd Mon yyyy'."""
    s = text.strip()
    try:
        if fmt == "dd Mon yyyy":
            d, mon, y = s.split()
            return date(int(y), MONTHS[mon.lower()[:3]], int(d))
        if fmt == "yyyy-mm-dd":
            return date.fromisoformat(s)
        sep = {"dd/mm/yyyy": "/", "dd.mm.yyyy": "."}[fmt]
        d, m, y = s.split(sep)
        return date(int(y), int(m), int(d))
    except (ValueError, KeyError) as err:
        raise PmError(f"not a {fmt} date: {text!r}") from err


def fmt_decimal(value: Decimal) -> str:
    """Canonical string for a Decimal: no exponent, no trailing zeros, '0' for zero."""
    if value == 0:
        return "0"
    text = format(value.normalize(), "f")
    return text


def quantize_cent(value: Decimal) -> Decimal:
    return value.quantize(CENT)
