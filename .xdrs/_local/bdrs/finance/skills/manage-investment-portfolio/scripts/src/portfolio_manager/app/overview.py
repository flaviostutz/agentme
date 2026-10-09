"""Overview sections of the consolidated analysis: window, trend, risk, bridge, positions, contribution, income, benchmark."""

from decimal import Decimal

from portfolio_manager.app import benchmark as benchmark_mod
from portfolio_manager.app import bridge, contribution, income, positions, risk, trend
from portfolio_manager.shared.values import ZERO

WINDOW = "last 12 months"
FULL_WINDOW_DAYS = 365  # a shorter history only covers part of the 12 months


def _names(data: dict) -> dict:
    """Display name per security key from the statements and trades."""
    names = {}
    for s in data["snapshots"]:
        for p in s["positions"]:
            names[p["isin"] or p["symbol"]] = p["name"] or names.get(p["isin"] or p["symbol"], "")
    for e in data["events"]:
        if e["name"]:
            names[e["isin"] or e["symbol"]] = e["name"]
    return names


def _contribution(win: dict | None, valuers: dict, data: dict, rates) -> dict:
    """Per-security contribution inside the window, per account then merged; securities without a price are listed."""
    if win is None:
        return {"rows": [], "missing": []}
    names = _names(data)
    parts, missing = [], set()
    for acct, valuer in sorted(valuers.items()):
        d0, d1 = max(win["from"], valuer.first), min(win["to"], valuer.last)
        if d0 >= d1:
            continue
        if valuer.mode == "transactions":
            rows, miss = contribution.from_transactions(valuer, data["events"], d0, d1)
        elif valuer.mode == "snapshot":
            rows, miss = contribution.from_snapshots(valuer, valuer.snaps, d0, d1)
        else:
            continue
        parts.append((acct, rows, rates, d1))
        missing.update(names.get(k, k) for k in miss)
    merged = contribution.merge(parts, names)
    return {**merged, "missing": sorted(missing), "from": win["from"], "to": win["to"]}


def _positions_total(accounts: list) -> Decimal | None:
    known = [Decimal(a["positions_eur"]) for a in accounts if a["positions_eur"] is not None]
    return sum(known, ZERO) if known else None


def build(portfolio: dict, per_account: dict, valuers: dict, pf, data: dict, rates, hooks: tuple, bench: tuple) -> dict:
    """hooks: (metrics, month_ends) from the analysis module; bench: (ticker, saved series)."""
    metrics, month_ends = hooks
    win = next((p for p in portfolio["periods"] if p["label"].startswith(WINDOW)), None)
    rows = trend.cumulative(metrics, pf, win["from"], month_ends(win["from"], win["to"])) if win else []
    d0, d1 = (win["from"], win["to"]) if win else (portfolio["common_date"],) * 2
    pos = positions.aggregate(per_account)
    return {
        "window": None
        if win is None
        else {
            "label": win["label"],
            "from": win["from"],
            "to": win["to"],
            "days": win["window_days"],
            "full": win["window_days"] >= FULL_WINDOW_DAYS,
        },
        "trend": rows,
        "risk": risk.measures(portfolio["periods"]),
        "bridge": None if win is None else bridge.window_bridge(win, per_account),
        "positions": pos,
        "contribution": _contribution(win, valuers, data, rates),
        "income": income.summarize(per_account, d0, d1, _positions_total(portfolio["accounts"])),
        "benchmark": benchmark_mod.build(bench[0], bench[1], rows, win["from"] if win else None, rates),
    }
