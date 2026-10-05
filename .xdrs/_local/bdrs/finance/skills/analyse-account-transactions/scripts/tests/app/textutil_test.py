# Tests for textutil.py: amounts, dates, titles and period helpers.
from datetime import date
from decimal import Decimal

import pytest

from analyse_account_transactions.app import textutil
from analyse_account_transactions.shared.errors import LedgerError


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1.234,56", "1234.56"),
        ("1,234.56", "1234.56"),
        ("-12,34", "-12.34"),
        ("+1.500,00€", "1500.00"),
        ("12,50-", "-12.50"),
        ("(12.50)", "-12.50"),
        ("\u22123.00", "-3.00"),
        ("EUR 1.234", "1234"),
        ("€ 7", "7"),
        ("1 000,5", "1000.5"),
    ],
)
def test_parse_amount(text, expected):
    assert textutil.parse_amount(text) == Decimal(expected)


@pytest.mark.parametrize("text", ["abc", "", "1.2.3,4,5"])
def test_parse_amount_rejects(text):
    with pytest.raises(LedgerError, match="not an amount"):
        textutil.parse_amount(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("02-01-2026", "2026-01-02"),
        ("2026-01-02", "2026-01-02"),
        ("02/01/2026", "2026-01-02"),
        ("20260102", "2026-01-02"),
        ("02.01.2026", "2026-01-02"),
        ("Jan 2, 2026", "2026-01-02"),
        ("2 January 2026", "2026-01-02"),
    ],
)
def test_parse_date(text, expected):
    assert textutil.parse_date(text) == expected


def test_parse_date_format_and_errors():
    assert textutil.parse_date("01/02/2026", "%m/%d/%Y") == "2026-01-02"
    with pytest.raises(LedgerError, match=r"\(format %m/%d/%Y\)"):
        textutil.parse_date("31/01/2026", "%m/%d/%Y")
    with pytest.raises(LedgerError, match="unrecognised date"):
        textutil.parse_date("yesterday")


def test_excel_serial():
    assert textutil.excel_serial("46024") == "2026-01-02"
    assert textutil.excel_serial(46024.5) == "2026-01-02"


def test_group_lines():
    words = [{"text": "b", "x0": 20, "top": 10.5}, {"text": "a", "x0": 5, "top": 10}, {"text": "c", "x0": 1, "top": 30}]
    assert [[w["text"] for w in line] for line in textutil.group_lines(words)] == [["a", "b"], ["c"]]


@pytest.mark.parametrize(
    ("text", "keep", "expected"),
    [
        ("CCV*Coffee Bar 1234", False, "Coffee Bar"),
        ("SumUp *Cafe Rose", False, "Cafe Rose"),
        ("ACME B.V. Amsterdam", False, "ACME Amsterdam"),
        ("Coffeeshop*ORDER123 Main", False, "Coffeeshop Main"),
        ("2026StoreName", False, "StoreName"),
        ("One Two Three Four Five", False, "One Two Three Four"),
        ("Route 66 Diner", True, "Route 66 Diner"),
        ("12345", False, "Unnamed"),
    ],
)
def test_title_from(text, keep, expected):
    assert textutil.title_from(text, keep_digits=keep) == expected


def test_make_row_clips_and_titles():
    r = textutil.make_row("2026-01-02", Decimal("-1.00"), "  Coffee   Bar  " + "y " * 250)
    assert r.timestamp == "2026-01-02"
    assert len(r.description) == 399 and r.description.endswith("...")
    assert r.title == "Coffee Bar y y"
    r = textutil.make_row("2026-01-02", Decimal(1), "d", title="A B C D E", timestamp="2026-01-02 10:00")
    assert (r.title, r.timestamp) == ("A B C D", "2026-01-02 10:00")


def test_slug_and_months():
    assert textutil.slug("My File (1)") == "my-file-1"
    assert textutil.slug("...") == "file"
    assert textutil.month_end(date(2024, 2, 10)) == date(2024, 2, 29)
    assert textutil.months("2025-11-15..2026-02-01") == {"2025-11", "2025-12", "2026-01", "2026-02"}
