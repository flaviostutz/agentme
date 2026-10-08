"""Open securities across all investment accounts: one row per ISIN (or per account and name when there is no ISIN)."""

from decimal import Decimal

from portfolio_manager.app.records import dec
from portfolio_manager.shared.values import ZERO

PLACES = Decimal("0.000001")


def _s(value: Decimal | None) -> str | None:
    return None if value is None else dec(value.quantize(PLACES))


def _key(row: dict) -> tuple:
    if row["isin"]:
        return (row["isin"], False)
    label = " ".join((row["name"] or row["symbol"]).lower().split())
    return (f"{row['account']}|{label}", True)


def aggregate(accounts: dict) -> dict:
    """Merge the securities tables of all accounts, sorted by EUR value (largest first).

    Rows without a price or EUR value, and unsupported products, are listed in `excluded`, never counted as 0.
    """
    groups: dict = {}
    excluded: list = []
    for acct in sorted(accounts):
        for row in accounts[acct]["securities"]:
            if row["unsupported"] or row["value_eur"] is None:
                excluded.append(row["name"] or row["symbol"] or row["isin"])
                continue
            key, no_isin = _key(row)
            g = groups.setdefault(
                key,
                {"key": key, "isin": row["isin"], "name": row["name"] or row["symbol"], "no_isin": no_isin}
                | {"value": ZERO, "cost": ZERO, "cost_known": True, "as_of": "", "accounts": set()},
            )
            g["value"] += Decimal(row["value_eur"])
            g["as_of"] = max(g["as_of"], row["as_of"])
            g["accounts"].add(acct)
            if row.get("cost_eur") is None:
                g["cost_known"] = False
            else:
                g["cost"] += Decimal(row["cost_eur"])
    total = sum((g["value"] for g in groups.values()), ZERO)
    rows = []
    for g in sorted(groups.values(), key=lambda g: (-g["value"], g["key"])):
        pnl = (g["value"] - g["cost"]) / g["cost"] if g["cost_known"] and g["cost"] > ZERO else None
        rows.append(
            {
                "key": g["key"],
                "isin": g["isin"],
                "name": g["name"],
                "no_isin": g["no_isin"],
                "accounts": sorted(g["accounts"]),
                "value_eur": _s(g["value"]),
                "weight": _s(g["value"] / total) if total > ZERO else None,
                "as_of": g["as_of"],
                "pnl_pct": _s(pnl),
            }
        )
    return {"rows": rows, "total_eur": _s(total), "excluded": sorted(set(excluded))}
