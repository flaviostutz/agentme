# Runtime: pytest; benchmark ticker validation, Yahoo payload parsing, EUR conversion and the comparison rows.
from datetime import datetime
from decimal import Decimal

import pytest

from portfolio_manager.app import benchmark
from portfolio_manager.app.fx import Rates
from portfolio_manager.shared.errors import PmError


def chart(closes: dict, currency="EUR", symbol="IWDA.AS", adjusted=False) -> dict:
    stamps = [int(datetime.fromisoformat(f"{m}-01T00:00:00+00:00").timestamp()) for m in closes]
    values = list(closes.values())
    indicators = {"quote": [{"close": values}]}
    if adjusted:
        indicators["adjclose"] = [{"adjclose": values}]
    return {
        "chart": {
            "result": [
                {"meta": {"currency": currency, "symbol": symbol}, "timestamp": stamps, "indicators": indicators}
            ]
        }
    }


@pytest.mark.parametrize("ticker", ["IWDA.AS", "^GSPC", "EURUSD=X", "BRK-B"])
def test_valid_tickers_are_accepted(ticker):
    assert benchmark.validate_ticker(ticker) == ticker


@pytest.mark.parametrize("ticker", ["", "a b", "x/y", "a?b=1", "A" * 21, None])
def test_tickers_that_could_alter_the_url_are_rejected(ticker):
    with pytest.raises(PmError, match="invalid benchmark ticker"):
        benchmark.validate_ticker(ticker)


def test_parse_chart_prefers_adjusted_closes_and_keys_by_month():
    series = benchmark.parse_chart(chart({"2025-01": 100.5, "2025-02": None, "2025-03": 103}, adjusted=True))
    assert series == {"symbol": "IWDA.AS", "currency": "EUR", "prices": {"2025-01": "100.5", "2025-03": "103"}}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"chart": {"result": None}},
        chart({"2025-01": 1}, currency="XXX"),
        chart({"2025-01": None}),
    ],
)
def test_parse_chart_rejects_unexpected_payloads(payload):
    with pytest.raises(PmError, match="benchmark data rejected"):
        benchmark.parse_chart(payload)


def test_parse_chart_rejects_mismatched_series():
    payload = chart({"2025-01": 1, "2025-02": 2})
    payload["chart"]["result"][0]["timestamp"].pop()
    with pytest.raises(PmError, match="benchmark data rejected"):
        benchmark.parse_chart(payload)


def trend(*pairs):
    return [{"date": d, "twr": t} for d, t in pairs]


def test_compare_returns_the_benchmark_return_since_the_start_in_eur():
    series = benchmark.parse_chart(chart({"2025-01": 100, "2025-02": 110, "2025-03": 120}))
    rows = benchmark.compare(
        series, trend(("2025-01-31", "0"), ("2025-02-28", "0.05"), ("2025-04-30", "0.1")), "2025-01-15", None
    )
    assert [(r["date"], r["twr"], r["benchmark"]) for r in rows] == [
        ("2025-01-31", "0", "0"),
        ("2025-02-28", "0.05", "0.1"),
        ("2025-04-30", "0.1", None),
    ]


def test_compare_converts_foreign_prices_and_pence_with_the_rates():
    rates = Rates(
        {
            "USD": {"2025-01-28": Decimal(2), "2025-02-28": Decimal(4)},
            "GBP": {"2025-01-28": Decimal(1), "2025-02-28": Decimal(1)},
        }
    )
    usd = benchmark.parse_chart(chart({"2025-01": 100, "2025-02": 100}, currency="USD"))
    rows = benchmark.compare(usd, trend(("2025-02-28", "0")), "2025-01-31", rates)
    assert rows[0]["benchmark"] == "-0.5"
    pence = benchmark.parse_chart(chart({"2025-01": 1000, "2025-02": 1100}, currency="GBp"))
    rows = benchmark.compare(pence, trend(("2025-02-28", "0")), "2025-01-31", rates)
    assert rows[0]["benchmark"] == "0.1"


def test_compare_gives_none_when_the_start_month_has_no_price():
    series = benchmark.parse_chart(chart({"2025-02": 110}))
    assert benchmark.compare(series, trend(("2025-02-28", "0")), "2025-01-31", None)[0]["benchmark"] is None


def test_build_states():
    series = {"ticker": "IWDA.AS", **benchmark.parse_chart(chart({"2025-01": 100, "2025-02": 110}))}
    assert benchmark.build(None, None, [], None, None)["state"] == "not-configured"
    assert benchmark.build("IWDA.AS", None, [], "2025-01-01", None)["state"] == "no-data"
    assert benchmark.build("OTHER", series, [], "2025-01-01", None)["state"] == "no-data"
    assert benchmark.build("IWDA.AS", series, [], None, None)["state"] == "no-data"
    ok = benchmark.build("IWDA.AS", series, trend(("2025-02-28", "0.1")), "2025-01-31", None)
    assert ok["state"] == "ok" and ok["currency"] == "EUR" and ok["rows"][0]["benchmark"] == "0.1"
