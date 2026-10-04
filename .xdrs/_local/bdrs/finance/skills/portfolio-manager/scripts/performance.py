# Runtime: Python >=3.11 stdlib only; valuation timeline, time-weighted return chain and XIRR (Decimal). Statuses never hide approximations.
"""Performance maths. Status order: complete < interpolated < approximate < unavailable; n/a is never reported as 0."""

from datetime import date
from decimal import Decimal, getcontext

from util import ZERO

getcontext().prec = 40
STATUS_RANK = {"complete": 0, "interpolated": 1, "approximate": 2, "unavailable": 3}


def worst(*statuses: str) -> str:
    return max(statuses, key=lambda s: STATUS_RANK[s], default="complete")


def days_between(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def interpolate(points: list, day: str) -> tuple:
    """points: sorted [(iso date, Decimal)]. Returns (value, status): complete on a point, interpolated between, approximate flat
    outside the range, unavailable without points."""
    if not points:
        return None, "unavailable"
    for d, v in points:
        if d == day:
            return v, "complete"
    before = [p for p in points if p[0] < day]
    after = [p for p in points if p[0] > day]
    if before and after:
        (d0, v0), (d1, v1) = before[-1], after[0]
        span = days_between(d0, d1)
        return v0 + (v1 - v0) * Decimal(days_between(d0, day)) / Decimal(span), "interpolated"
    return (before[-1][1] if before else after[0][1]), "approximate"


def twr(value_at, flows: list, d0: str, d1: str) -> dict:
    """Chain sub-periods split at each external flow date.

    value_at(day) -> (Decimal value at end of that day or None, status); flows: [{date, amount}] where amount > 0 adds money to the
    account. Sub-periods that start at value <= 0 (first deposit, full sale, re-buy) are skipped; no usable sub-period gives unavailable.
    """
    in_period = sorted((f for f in flows if d0 < f["date"] <= d1), key=lambda f: f["date"])
    days = sorted({f["date"] for f in in_period} | {d1})
    start_v, status = value_at(d0)
    if start_v is None:
        return {"value": None, "status": "unavailable", "reason": f"no valuation at {d0}"}
    growth, used, prev_v = Decimal(1), 0, start_v
    for day in days:
        end_v, st = value_at(day)
        if end_v is None:
            return {"value": None, "status": "unavailable", "reason": f"no valuation at {day}"}
        flow_today = sum((Decimal(f["amount"]) for f in in_period if f["date"] == day), ZERO)
        before = end_v - flow_today
        status = worst(status, st)
        if prev_v > ZERO:
            growth *= before / prev_v
            used += 1
        prev_v = end_v
    if used == 0:
        return {"value": None, "status": "unavailable", "reason": "no sub-period with a positive starting value"}
    return {"value": growth - 1, "status": status, "reason": ""}


def xirr(flows: list, d0: str, d1: str, v0: Decimal, v1: Decimal) -> dict:
    """Money-weighted annual rate. flows: [{date, amount}] (amount > 0 = money added). Result {value, status, annualized, reason}."""
    cfs = [(d0, -v0)] if v0 > ZERO else []
    cfs += [(f["date"], -Decimal(f["amount"])) for f in flows if d0 < f["date"] <= d1]
    cfs.append((d1, v1))
    cfs = [c for c in cfs if c[1] != ZERO]
    annualized = days_between(d0, d1) < 365
    if len(cfs) < 2 or not (any(c[1] > ZERO for c in cfs) and any(c[1] < ZERO for c in cfs)):
        return {"value": None, "status": "unavailable", "annualized": annualized, "reason": "cash flows all have the same sign"}

    def npv(rate: Decimal) -> Decimal:
        return sum((amt / (Decimal(1) + rate) ** (Decimal(days_between(d0, d)) / Decimal(365)) for d, amt in cfs), ZERO)

    lo, hi = Decimal("-0.99"), Decimal(100)
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > ZERO:
        return {"value": None, "status": "unavailable", "annualized": annualized, "reason": "no rate solves the cash flows"}
    for _ in range(120):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if f_mid == ZERO:
            lo = hi = mid
            break
        if f_lo * f_mid < ZERO:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return {"value": (lo + hi) / 2, "status": "complete", "annualized": annualized, "reason": ""}


def period_return(v0: Decimal | None, v1: Decimal | None, flows: list, d0: str, d1: str) -> dict:
    """Modified Dietz period return (money-weighted over the period, not annualised)."""
    if v0 is None or v1 is None:
        return {"value": None, "status": "unavailable", "reason": "missing valuation"}
    span = max(days_between(d0, d1), 1)
    net = sum((Decimal(f["amount"]) for f in flows if d0 < f["date"] <= d1), ZERO)
    weighted = sum((Decimal(f["amount"]) * Decimal(days_between(f["date"], d1)) / Decimal(span) for f in flows if d0 < f["date"] <= d1), ZERO)
    base = v0 + weighted
    if base <= ZERO:
        return {"value": None, "status": "unavailable", "reason": "no invested base"}
    return {"value": (v1 - v0 - net) / base, "status": "approximate", "reason": ""}
