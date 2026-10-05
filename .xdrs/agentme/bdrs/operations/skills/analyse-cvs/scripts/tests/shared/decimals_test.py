# Python 3.11+ pytest suite; run with: make test
from decimal import Decimal
from fractions import Fraction

import pytest

from analyse_cvs.shared.decimals import (
    clamp,
    decimal_places,
    has_one_decimal,
    parse_decimal,
    round_one,
    round_one_fraction,
    show,
    show_exact,
)


@pytest.mark.parametrize("text", ["1e3", "NaN", "Infinity", "7,5", "", "abc", "1.2.3"])
def test_parse_decimal_rejects(text):
    with pytest.raises(ValueError, match="not a decimal"):
        parse_decimal(text)


def test_parse_decimal_accepts_signed_text():
    assert parse_decimal(" -0.5 ") == Decimal("-0.5")
    assert parse_decimal("+1") == Decimal(1)


def test_decimal_places_and_one_decimal():
    assert decimal_places(Decimal(7)) == 0
    assert decimal_places(Decimal("7.25")) == 2
    assert has_one_decimal(Decimal("7.0"))
    assert not has_one_decimal(Decimal(7))


def test_rounding_is_half_up_and_exact():
    assert round_one(Decimal("7.25")) == Decimal("7.3")
    assert round_one_fraction(Fraction(51, 10) + Fraction(1, 100)) == Decimal("5.1")
    assert round_one_fraction(Fraction(5, 1) + Fraction(1, 45)) == Decimal("5.0")
    assert round_one_fraction(Fraction(1, 2) + Fraction(1, 20)) == Decimal("0.6")


def test_clamp_and_show():
    assert clamp(Decimal(12)) == Decimal("10.0")
    assert clamp(Decimal("0.2")) == Decimal("1.0")
    assert show(Decimal("1E+1")) == "10"
    assert show_exact(Fraction(22, 3)) == "7.3333"
