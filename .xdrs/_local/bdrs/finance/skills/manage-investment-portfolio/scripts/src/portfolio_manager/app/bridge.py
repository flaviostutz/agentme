"""Wealth bridge of a window: start value, money added, income, fees and taxes, FX, market and other effects, end value."""

from decimal import Decimal

from portfolio_manager.app.records import dec
from portfolio_manager.shared.values import ZERO

PLACES = Decimal("0.000001")


def _s(value: Decimal) -> str:
    return dec(value.quantize(PLACES))


def _sum_in_window(accounts: dict, kinds: tuple, d0: str, d1: str) -> tuple:
    total, skipped = ZERO, 0
    for acct in accounts.values():
        for e in (acct["accounting"] or {}).get("income_events", []):
            if e["kind"] in kinds and d0 < e["date"] <= d1:
                if e["amount_eur"] is None:
                    skipped += 1
                else:
                    total += Decimal(e["amount_eur"])
    return total, skipped


def window_bridge(row: dict, accounts: dict) -> dict | None:
    """Steps start -> end for a portfolio period row; None without a start and end valuation.

    Income, fees and taxes come from transaction accounts only; the market and other effect is the remainder.
    """
    if row["start_value"] is None or row["end_value"] is None or row["gain"] is None:
        return None
    start, end, flows = Decimal(row["start_value"]), Decimal(row["end_value"]), Decimal(row["net_flows"])
    income, skip_in = _sum_in_window(accounts, ("dividends", "interest"), row["from"], row["to"])
    costs, skip_costs = _sum_in_window(accounts, ("fees", "taxes"), row["from"], row["to"])
    fx = Decimal(row["fx_effect"]) if row["fx_effect"] is not None else ZERO
    other = Decimal(row["gain"]) - income + costs - fx
    steps = [
        ("Start", start, "total"),
        ("Money added", flows, "delta"),
        ("Income", income, "delta"),
        ("Fees and taxes", -costs, "delta"),
        ("FX effect", fx, "delta"),
        ("Market and other", other, "delta"),
        ("End", end, "total"),
    ]
    return {
        "from": row["from"],
        "to": row["to"],
        "steps": [{"label": label, "amount": _s(v), "kind": kind} for label, v, kind in steps],
        "unconverted": skip_in + skip_costs,
        "status": row["period_return_status"],
    }
