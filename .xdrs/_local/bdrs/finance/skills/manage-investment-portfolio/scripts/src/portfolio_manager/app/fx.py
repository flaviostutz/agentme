"""FX rates (pure lookup): units of currency per 1 EUR from the ECB history CSV; every conversion reports its rate date and status."""

import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from portfolio_manager.shared.values import ZERO

MAX_GAP_DAYS = 10


def parse_ecb_csv(text: str) -> dict:
    """ECB CSV (Date,USD,...; newest first; 'N/A' for missing) -> {ccy: {iso date: Decimal per EUR}}."""
    rates: dict = {}
    for row in csv.DictReader(io.StringIO(text)):
        day = (row.get("Date") or "").strip()
        for ccy, raw in row.items():
            if ccy and ccy != "Date" and raw and raw.strip() not in ("", "N/A"):
                rates.setdefault(ccy.strip(), {})[day] = Decimal(raw.strip())
    return rates


class Rates:
    """Lookup of EUR conversion rates with provenance."""

    def __init__(self, ecb: dict | None = None, statement: dict | None = None) -> None:
        self.ecb = ecb or {}
        self.statement = statement or {}  # {(ccy, iso date): Decimal per EUR} observed on statements

    def add_statement(self, ccy: str, day: str, per_eur: Decimal) -> None:
        self.statement[(ccy, day)] = per_eur

    def rate(self, ccy: str, day: str) -> dict:
        """{rate (ccy per EUR), rate_date, status: exact|prior-day rate|statement|unavailable}."""
        if ccy == "EUR":
            return {"rate": Decimal(1), "rate_date": day, "status": "exact"}
        series = self.ecb.get(ccy, {})
        if day in series:
            return {"rate": series[day], "rate_date": day, "status": "exact"}
        d = date.fromisoformat(day)
        for back in range(1, MAX_GAP_DAYS + 1):
            prior = (d - timedelta(days=back)).isoformat()
            if prior in series:
                return {"rate": series[prior], "rate_date": prior, "status": "prior-day rate"}
        if (ccy, day) in self.statement:
            return {"rate": self.statement[(ccy, day)], "rate_date": day, "status": "statement"}
        return {"rate": None, "rate_date": None, "status": "unavailable"}

    def to_eur(self, amount: Decimal, ccy: str, day: str) -> tuple:
        """Return (Decimal EUR amount or None, status)."""
        info = self.rate(ccy, day)
        if info["rate"] is None or info["rate"] == ZERO:
            return None, "unavailable"
        return amount / info["rate"], info["status"]
