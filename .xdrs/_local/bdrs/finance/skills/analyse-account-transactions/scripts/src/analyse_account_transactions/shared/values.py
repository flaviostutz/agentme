"""Signed decimal values as written in the normalized files."""

import re
from decimal import Decimal, InvalidOperation

from analyse_account_transactions.shared.constants import CENT
from analyse_account_transactions.shared.errors import LedgerError


def format_value(value: Decimal) -> str:
    q = value.quantize(CENT)
    return f"+{q}" if q >= 0 else str(q)


def parse_value(text: str) -> Decimal:
    if not re.fullmatch(r"[+-]\d+\.\d{2}", text):
        msg = f"value must be signed with 2 decimals (e.g. -12.34): {text!r}"
        raise LedgerError(msg)
    return Decimal(text)


def parse_decimal(text: str) -> Decimal:
    try:
        return Decimal(text)
    except InvalidOperation as err:
        msg = f"not a number: {text!r}"
        raise LedgerError(msg) from err
