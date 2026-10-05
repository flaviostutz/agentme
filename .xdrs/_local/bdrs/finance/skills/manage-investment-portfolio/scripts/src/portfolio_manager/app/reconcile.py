"""Reconciliation: the ledger wins on conflict, every difference is reported as a check row."""

from decimal import Decimal
from itertools import pairwise

from portfolio_manager.app.records import check, rounding_tolerance
from portfolio_manager.shared.values import ZERO


def state_at(states: list, day: str, opening_cash: str = "0") -> dict:
    """Last replayed state on or before day (cash and quantities)."""
    best = {"date": None, "cash": opening_cash, "positions": {}}
    for s in states:
        if s["date"] <= day:
            best = s
    return best


def _row(scope: str, account: str, c: dict) -> dict:
    return {**c, "scope": scope, "account": account}


def positions_and_cash(accounts_res: dict, snapshots: list, openings: dict) -> list:
    """Ledger quantities and cash against the latest statement with positions (and its cash) per ledger account."""
    out = []
    for acct, res in accounts_res.items():
        snaps = [s for s in snapshots if s["account"] == acct and s["positions"]]
        if not snaps:
            continue
        snap = max(snaps, key=lambda s: s["date"])
        st = state_at(res["states"], snap["date"], openings.get(acct, {}).get("cash", "0"))
        tol = Decimal("0.000001")
        statement = {
            (p["isin"] or p["symbol"]): Decimal(p["quantity"]) for p in snap["positions"] if p["quantity"] is not None
        }
        for key in sorted(set(statement) | set(st["positions"])):
            out.append(
                _row(
                    "positions",
                    acct,
                    check(
                        f"quantity {key} on {snap['date']}",
                        statement.get(key, ZERO),
                        Decimal(st["positions"].get(key, "0")),
                        tol,
                    ),
                )
            )
        if snap.get("cash") is not None:
            out.append(
                _row(
                    "cash",
                    acct,
                    check(
                        f"cash on {snap['date']}",
                        Decimal(snap["cash"]),
                        Decimal(st["cash"]),
                        rounding_tolerance(len(res["states"])),
                        max(Decimal(1), Decimal(snap["total"] or 0) * Decimal("0.005")),
                    ),
                )
            )
    return out


def pnl_reports(events: list, references: list) -> list:
    """Ledger sells and dividends against the broker P&L statement for the same account and period."""
    out = []
    for ref in (r for r in references if r["kind"] == "pnl-summary"):
        sells = [
            e
            for e in events
            if e["account"] == ref["account"] and e["type"] == "SELL" and ref["from"] <= e["date"] <= ref["to"]
        ]
        divs = [
            e
            for e in events
            if e["account"] == ref["account"] and e["type"] == "DIVIDEND" and ref["from"] <= e["date"] <= ref["to"]
        ]
        gross = sum((Decimal(e["cash"]) + Decimal(e["fee"]) for e in sells), ZERO)
        out.append(
            _row(
                "pnl-report",
                ref["account"],
                check(
                    f"sell proceeds {ref['from']}..{ref['to']}",
                    Decimal(ref["gross_proceeds"]),
                    gross,
                    rounding_tolerance(len(sells), "0.05"),
                ),
            )
        )
        out.append(
            _row(
                "pnl-report",
                ref["account"],
                check(
                    f"dividends/other income {ref['from']}..{ref['to']}",
                    Decimal(ref["net_other_income"]),
                    sum((Decimal(e["cash"]) for e in divs), ZERO),
                    rounding_tolerance(len(divs), "0.05"),
                ),
            )
        )
    return out


def tax_statements(snapshots: list, references: list) -> list:
    """Upvest annual tax transactions against quantity changes between consecutive statements of the same year."""
    out = []
    by_acct: dict = {}
    for s in sorted(snapshots, key=lambda s: s["date"]):
        by_acct.setdefault(s["account"], []).append(s)
    for acct, snaps in by_acct.items():
        txs = [r for r in references if r["kind"] == "tax-transaction" and r["account"] == acct]
        if not txs:
            continue
        for a, b in pairwise(snaps):
            if a["date"][:4] != b["date"][:4] or not txs or not any(a["date"] < t["date"] <= b["date"] for t in txs):
                continue
            qa = {p["isin"]: Decimal(p["quantity"]) for p in a["positions"]}
            qb = {p["isin"]: Decimal(p["quantity"]) for p in b["positions"]}
            net: dict = {}
            for t in txs:
                if a["date"] < t["date"] <= b["date"]:
                    net[t["isin"]] = net.get(t["isin"], ZERO) + (
                        Decimal(t["units"]) if t["side"] == "BUY" else -Decimal(t["units"])
                    )
            for isin in sorted(set(qa) | set(qb) | set(net)):
                out.append(
                    _row(
                        "tax-statement",
                        acct,
                        check(
                            f"quantity change {isin} {a['date']}..{b['date']}",
                            qb.get(isin, ZERO) - qa.get(isin, ZERO),
                            net.get(isin, ZERO),
                            Decimal("0.01"),
                            Decimal("0.05"),
                        ),
                    )
                )
    return out


def reconcile(accounts_res: dict, events: list, snapshots: list, references: list, openings: dict) -> list:
    return (
        positions_and_cash(accounts_res, snapshots, openings)
        + pnl_reports(events, references)
        + tax_statements(snapshots, references)
    )
