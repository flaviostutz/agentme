# Runtime: pytest; number, money and date parsing used by every adapter.
from datetime import date
from decimal import Decimal

import pytest

from sourcedoc import PmError
from util import fmt_decimal, is_money, iso, parse_date, parse_money, parse_number, parse_rate, quantize_cent


def test_parse_number_decimal_point_and_comma():
    assert parse_number("1,234.50") == Decimal("1234.50")
    assert parse_number("1.234,50", decimal=",") == Decimal("1234.50")


def test_parse_number_trailing_minus_is_negative():
    assert parse_number("1,306.68-") == Decimal("-1306.68")
    assert parse_number("-5") == Decimal(-5)


def test_parse_number_rejects_text():
    with pytest.raises(PmError):
        parse_number("abc")


@pytest.mark.parametrize(
    ("text", "expected"),
    [("-€2.21", ("EUR", Decimal("-2.21"))), ("US$0", ("USD", Decimal(0))), ("$1,064.91", ("USD", Decimal("1064.91"))),
     ("R$ -337,38", ("BRL", Decimal("-337.38"))), ("1,306.68-", ("", Decimal("-1306.68"))), ("12.5 EUR", ("EUR", Decimal("12.5")))],
)
def test_parse_money_variants(text, expected):
    decimal = "," if "," in text and "." not in text else "."
    assert parse_money(text, decimal=decimal) == expected


def test_parse_money_default_currency_and_errors():
    assert parse_money("10", default_currency="EUR") == ("EUR", Decimal(10))
    with pytest.raises(PmError):
        parse_money("hello")
    with pytest.raises(PmError):
        parse_money("10 XYZ")


def test_is_money_and_rate():
    assert is_money("€1.00")
    assert not is_money("n/a")
    assert parse_rate("1.0835") == Decimal("1.0835")


@pytest.mark.parametrize(
    ("text", "fmt"),
    [("31/12/2025", "dd/mm/yyyy"), ("31.12.2025", "dd.mm.yyyy"), ("2025-12-31", "yyyy-mm-dd"), ("31 Dec 2025", "dd Mon yyyy")],
)
def test_parse_date_formats(text, fmt):
    assert parse_date(text, fmt) == date(2025, 12, 31)


def test_parse_date_rejects_invalid():
    with pytest.raises(PmError):
        parse_date("32/13/2025", "dd/mm/yyyy")
    with pytest.raises(PmError):
        parse_date("2025-12-31", "dd/mm/yyyy")


def test_decimal_formatting():
    assert fmt_decimal(Decimal("10.500")) == "10.5"
    assert fmt_decimal(Decimal("0.000")) == "0"
    assert fmt_decimal(Decimal("1E+2")) == "100"
    assert quantize_cent(Decimal("1.005")) in (Decimal("1.00"), Decimal("1.01"))
    assert iso(date(2025, 1, 2)) == "2025-01-02"
