"""Risk and return measures from monthly time-weighted returns (flows cannot distort them)."""

from decimal import Decimal
from itertools import pairwise

from portfolio_manager.app import performance as perf
from portfolio_manager.app.records import dec
from portfolio_manager.shared.values import ZERO

PLACES = Decimal("0.000001")
MIN_MONTHS_FOR_VOLATILITY = 3
DAYS_PER_YEAR = 365
WINDOW_MONTHS = 12


def _s(value: Decimal | None) -> str | None:
    return None if value is None else dec(value.quantize(PLACES))


def _volatility(values: list) -> Decimal | None:
    """Sample standard deviation of monthly returns scaled to a year."""
    if len(values) < MIN_MONTHS_FOR_VOLATILITY:
        return None
    mean = sum(values, ZERO) / len(values)
    variance = sum(((v - mean) ** 2 for v in values), ZERO) / (len(values) - 1)
    return variance.sqrt() * Decimal(12).sqrt()


def _drawdown(months: list) -> list:
    """Month-end drawdown from the running peak of the chained monthly returns."""
    index, peak, out = Decimal(1), Decimal(1), []
    for m in months:
        index *= 1 + Decimal(m["twr"])
        peak = max(peak, index)
        out.append({"date": m["to"], "drawdown": _s(index / peak - 1)})
    return out


def _cagr(inception: dict | None) -> tuple:
    """Annualised TWR; only over 12 months or more of history."""
    if not inception or inception["twr"] is None:
        return None, "n/a (no TWR since inception)"
    days = perf.days_between(inception["from"], inception["to"])
    growth = 1 + Decimal(inception["twr"])
    if days < DAYS_PER_YEAR:
        return None, "n/a (history under 12 months)"
    if growth <= ZERO:
        return None, "n/a (total loss)"
    return growth ** (Decimal(DAYS_PER_YEAR) / Decimal(days)) - 1, ""


def _summary(months: list, cagr: Decimal | None, cagr_reason: str) -> dict:
    """Best and worst month, volatility, max drawdown and CAGR over the given complete-month rows."""
    values = [Decimal(m["twr"]) for m in months]
    dd = _drawdown(months)
    deepest = min(dd, key=lambda d: Decimal(d["drawdown"]), default=None)
    best = max(months, key=lambda m: Decimal(m["twr"]), default=None)
    worst = min(months, key=lambda m: Decimal(m["twr"]), default=None)
    vol = _volatility(values)
    return {
        "months": len(months),
        "best": None if best is None else {"label": best["label"], "twr": best["twr"], "status": best["twr_status"]},
        "worst": None
        if worst is None
        else {"label": worst["label"], "twr": worst["twr"], "status": worst["twr_status"]},
        "volatility": _s(vol),
        "volatility_reason": "" if vol is not None else f"n/a (needs {MIN_MONTHS_FOR_VOLATILITY}+ complete months)",
        "max_drawdown": deepest["drawdown"] if deepest else None,
        "max_drawdown_date": deepest["date"] if deepest else None,
        "cagr": _s(cagr),
        "cagr_reason": cagr_reason,
        "status": perf.worst(*(m["twr_status"] for m in months)),
        "drawdown": dd,
    }


def _is_calendar_month(p: dict) -> bool:
    return p["label"].startswith("month ") and not p["partial"]


def _window_gap(latest: list) -> str:
    """Why the rows are not 12 consecutive complete calendar months, empty when they are."""
    if len(latest) < WINDOW_MONTHS:
        return f"n/a (needs {WINDOW_MONTHS} complete months)"
    if any(not p["first_day"].endswith("-01") for p in latest) or any(
        a["to"] != b["from"] for a, b in pairwise(latest)
    ):
        return f"n/a (needs {WINDOW_MONTHS} consecutive complete months)"
    if any(p["twr"] is None for p in latest):
        return "n/a (a month has no TWR)"
    return ""


def last_12_months(periods: list) -> dict:
    """Measures over the latest 12 consecutive complete calendar months; a gap, a short history or a missing month gives n/a."""
    latest = [p for p in periods if _is_calendar_month(p)][-WINDOW_MONTHS:]
    reason = _window_gap(latest)
    if reason:
        return {"available": False, "reason": reason}
    growth = Decimal(1)
    for p in latest:
        growth *= 1 + Decimal(p["twr"])
    return {
        **_summary(latest, growth - 1, ""),
        "available": True,
        "reason": "",
        "from": latest[0]["first_day"],
        "to": latest[-1]["to"],
    }


def yearly_returns(periods: list) -> list:
    """TWR of every full calendar year that starts on the previous 31 December (the CAGR of a one-year span)."""
    out = []
    for p in periods:
        if not p["label"].startswith("year ") or p["partial"] or p["twr"] is None:
            continue
        year = int(p["label"][5:9])
        if p["from"] == f"{year - 1}-12-31":
            out.append({"year": str(year), "twr": p["twr"], "status": p["twr_status"]})
    return out


def measures(periods: list) -> dict:
    """Measures since inception from portfolio period rows (partial months are skipped), plus the latest 12 months and per-year returns."""
    months = [p for p in periods if _is_calendar_month(p) and p["twr"] is not None]
    cagr, cagr_reason = _cagr(next((p for p in periods if p["label"] == "inception"), None))
    return {
        **_summary(months, cagr, cagr_reason),
        "last_12m": last_12_months(periods),
        "yearly": yearly_returns(periods),
    }
