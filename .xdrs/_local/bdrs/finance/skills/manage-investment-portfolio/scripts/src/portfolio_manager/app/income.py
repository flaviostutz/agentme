"""Income, fees and taxes per calendar year and per month, from the dated accounting events (EUR at the event date)."""

from decimal import Decimal

from portfolio_manager.app.records import dec
from portfolio_manager.shared.values import ZERO

PLACES = Decimal("0.000001")
KINDS = ("dividends", "interest", "fees", "taxes", "withholding")
TOP_PAYERS = 10


def _s(value: Decimal | None) -> str | None:
    return None if value is None else dec(value.quantize(PLACES))


def _months(d0: str, d1: str) -> list:
    y, m, out = int(d0[:4]), int(d0[5:7]), []
    while (y, m) <= (int(d1[:4]), int(d1[5:7])):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _events(accounts: dict) -> list:
    rows = [
        {**e, "account": acct}
        for acct in sorted(accounts)
        for e in ((accounts[acct]["accounting"] or {}).get("income_events", []))
    ]
    return sorted(rows, key=lambda e: (e["date"], e["account"], e["kind"], e["security"]))


def summarize(accounts: dict, d0: str, d1: str, positions_eur: Decimal | None) -> dict:
    """Per year, per month of the window (d0, d1], top payers and the trailing-12-month yield on open positions.

    Events whose EUR amount could not be converted are counted in `unconverted`, never treated as 0.
    """
    events = _events(accounts)
    years: dict = {}
    months = {m: {"dividends": ZERO, "interest": ZERO} for m in _months(d0, d1)}
    payers: dict = {}
    for e in events:
        if e["amount_eur"] is None:
            continue
        eur = Decimal(e["amount_eur"])
        row = years.setdefault(e["date"][:4], dict.fromkeys(KINDS, ZERO))
        row[e["kind"]] += eur
        if e["withholding_eur"] is not None:
            row["withholding"] += Decimal(e["withholding_eur"])
        if d0 < e["date"] <= d1 and e["kind"] in ("dividends", "interest"):
            months[e["date"][:7]][e["kind"]] += eur
            if e["kind"] == "dividends":
                payers[e["name"] or e["security"]] = payers.get(e["name"] or e["security"], ZERO) + eur
    trailing = sum((v["dividends"] + v["interest"] for v in months.values()), ZERO)
    top = sorted(payers.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_PAYERS]
    return {
        "years": {y: {k: _s(v) for k, v in row.items()} for y, row in sorted(years.items())},
        "months": {m: {k: _s(v) for k, v in row.items()} for m, row in months.items()},
        "payers": [{"name": n, "amount_eur": _s(v)} for n, v in top],
        "trailing_eur": _s(trailing),
        "yield": _s(trailing / positions_eur) if positions_eur and positions_eur > ZERO else None,
        "unconverted": sum(1 for e in events if e["amount_eur"] is None),
        "events": len(events),
    }
