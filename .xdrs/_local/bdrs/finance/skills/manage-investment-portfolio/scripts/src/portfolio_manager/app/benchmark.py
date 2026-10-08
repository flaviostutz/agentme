"""Benchmark comparison: validate the ticker and Yahoo chart payload, express monthly closes in EUR, compare with the TWR."""

import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from portfolio_manager.app.records import dec
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.values import ZERO

TICKER = re.compile(r"^[A-Za-z0-9.^=\-]{1,20}$")
CURRENCIES = ("EUR", "USD", "GBP", "GBp", "CHF", "CAD", "BRL")
PLACES = Decimal("0.000001")
PENCE = Decimal(100)


def validate_ticker(ticker: str) -> str:
    """Tickers go into a URL: only the characters Yahoo symbols use are accepted."""
    if not TICKER.match(ticker or ""):
        msg = f"invalid benchmark ticker {ticker!r}: use 1-20 letters, digits, '.', '^', '=' or '-' (e.g. IWDA.AS)"
        raise PmError(msg)
    return ticker


def parse_chart(payload: dict) -> dict:
    """Yahoo chart JSON -> {symbol, currency, prices {YYYY-MM: close}}; anything unexpected is rejected."""
    try:
        res = payload["chart"]["result"][0]
        stamps = res["timestamp"]
        indicators = res["indicators"]
        closes = (indicators.get("adjclose") or [{}])[0].get("adjclose") or indicators["quote"][0]["close"]
        currency = res["meta"]["currency"]
        symbol = str(res["meta"]["symbol"])
        if currency not in CURRENCIES or len(stamps) != len(closes):
            msg = "unsupported currency or mismatched series"
            raise ValueError(msg)  # noqa: TRY301
        prices = {}
        for ts, close in zip(stamps, closes, strict=True):
            if close is not None:
                prices[datetime.fromtimestamp(int(ts), tz=UTC).strftime("%Y-%m")] = dec(Decimal(str(close)))
    except (KeyError, IndexError, TypeError, ValueError, InvalidOperation, OverflowError, OSError) as err:
        msg = f"benchmark data rejected: unexpected Yahoo response ({type(err).__name__})"
        raise PmError(msg) from err
    if not prices:
        msg = "benchmark data rejected: no prices in the response"
        raise PmError(msg)
    return {"symbol": symbol, "currency": currency, "prices": dict(sorted(prices.items()))}


def _eur(price: Decimal, currency: str, month: str, rates) -> Decimal | None:
    if currency == "EUR":
        return price
    last = f"{month}-28"  # month-end approximated by a late-month date; rates fall back up to 10 days
    ccy, amount = ("GBP", price / PENCE) if currency == "GBp" else (currency, price)
    return rates.to_eur(amount, ccy, last)[0]


def compare(series: dict, trend: list, start: str, rates) -> list:
    """Per trend date: portfolio TWR and the benchmark's return since `start`, both None when not computable.

    The benchmark uses the close of the month containing each date (the last month is the latest price).
    """
    base = series["prices"].get(start[:7])
    base = None if base is None else _eur(Decimal(base), series["currency"], start[:7], rates)
    rows = []
    for t in trend:
        raw = series["prices"].get(t["date"][:7])
        now = None if raw is None else _eur(Decimal(raw), series["currency"], t["date"][:7], rates)
        value = None if base is None or now is None or base <= ZERO else now / base - 1
        rows.append(
            {"date": t["date"], "twr": t["twr"], "benchmark": None if value is None else dec(value.quantize(PLACES))}
        )
    return rows


def build(ticker: str | None, series: dict | None, trend: list, start: str | None, rates) -> dict:
    """Analysis block: not-configured, no-data or ok with comparison rows."""
    if not ticker:
        return {"state": "not-configured", "ticker": None, "rows": []}
    if not series or series.get("ticker") != ticker or not start:
        return {"state": "no-data", "ticker": ticker, "rows": []}
    return {
        "state": "ok",
        "ticker": ticker,
        "currency": series["currency"],
        "rows": compare(series, trend, start, rates),
    }
