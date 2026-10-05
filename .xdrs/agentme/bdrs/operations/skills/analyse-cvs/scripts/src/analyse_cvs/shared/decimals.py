"""Exact decimal helpers for scores; no float anywhere in the chain (agentme-edr-105)."""

import re
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from math import floor

from analyse_cvs.shared.constants import SCALE_MAX, SCALE_MIN

_NUMBER = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
_ONE_DECIMAL = Decimal("0.1")
_TEN = 10
_HALF = Fraction(1, 2)
_SCALE_4 = 10_000
_FOUR_DECIMALS = Decimal("0.0001")


def parse_decimal(text: str) -> Decimal:
    """Parse plain decimal text ("7", "-0.5") and reject NaN, Infinity, exponents and commas."""
    value = text.strip()
    if not _NUMBER.match(value):
        msg = f"not a decimal number: {text!r}"
        raise ValueError(msg)
    return Decimal(value)


def decimal_places(value: Decimal) -> int:
    """Return how many decimal places the value is written with."""
    exponent = value.as_tuple().exponent
    return -exponent if isinstance(exponent, int) and exponent < 0 else 0


def has_one_decimal(value: Decimal) -> bool:
    """Return True when the value is written with exactly one decimal place."""
    return decimal_places(value) == 1


def round_one(value: Decimal) -> Decimal:
    """Round half up to one decimal place."""
    return value.quantize(_ONE_DECIMAL, rounding=ROUND_HALF_UP)


def clamp(value: Decimal, low: Decimal = SCALE_MIN, high: Decimal = SCALE_MAX) -> Decimal:
    """Limit the value to the closed interval [low, high]."""
    return min(max(value, low), high)


def round_one_fraction(value: Fraction) -> Decimal:
    """Round a positive exact fraction half up to one decimal place."""
    return round_one(Decimal(floor(value * _TEN + _HALF)) / _TEN)


def show_exact(value: Fraction) -> str:
    """Render an exact fraction with 4 decimals, rounded half up, for information only."""
    scaled = Decimal(floor(value * _SCALE_4 + _HALF)) / _SCALE_4
    return format(scaled.quantize(_FOUR_DECIMALS), "f")


def show(value: Decimal) -> str:
    """Render a one-decimal value without exponent notation."""
    return format(value, "f")
