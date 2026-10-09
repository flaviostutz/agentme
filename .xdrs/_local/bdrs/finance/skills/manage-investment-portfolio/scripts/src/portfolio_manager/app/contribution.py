"""Contribution of each security to the result of a window: value change minus money put in, plus income."""

from decimal import Decimal

from portfolio_manager.app import performance as perf
from portfolio_manager.app.records import dec
from portfolio_manager.shared.values import ZERO

PLACES = Decimal("0.000001")


def _s(value: Decimal | None) -> str | None:
    return None if value is None else dec(value.quantize(PLACES))


def _price(prices: list, day: str) -> tuple:
    return perf.interpolate(prices, day)


def _value(qty: Decimal, prices: list, day: str) -> tuple:
    """(value, status) of a holding; a missing price makes it unavailable, an empty holding is exactly 0."""
    if qty <= ZERO:
        return ZERO, "complete"
    price, status = _price(prices, day)
    return (None, "unavailable") if price is None else (qty * price, status)


def _trade_flows(events: list, acct: str, d0: str, d1: str, prices: dict) -> tuple:
    """Money put into each security (+) or taken out (-) and income received, inside (d0, d1]."""
    put_in: dict = {}
    income: dict = {}
    for e in events:
        if e["account"] != acct or not (d0 < e["date"] <= d1):
            continue
        key = e["isin"] or e["symbol"]
        if e["type"] in ("BUY", "SELL"):
            put_in[key] = put_in.get(key, ZERO) - Decimal(e["cash"])
        elif e["type"] == "DIVIDEND":
            income[key] = income.get(key, ZERO) + Decimal(e["cash"])
        elif e["type"] in ("TRANSFER_IN", "TRANSFER_OUT"):
            price, _ = _price(prices.get(key, []), e["date"])
            if price is not None:
                sign = 1 if e["type"] == "TRANSFER_IN" else -1
                put_in[key] = put_in.get(key, ZERO) + sign * Decimal(e["quantity"]) * price
    return put_in, income


def from_transactions(valuer, events: list, d0: str, d1: str) -> tuple:
    """Rows per security for a transactions account: (rows [{key, native, currency, status}], keys without a price)."""
    acct = valuer.acct["id"]
    _, h0 = valuer.holdings_at(d0)
    _, h1 = valuer.holdings_at(d1)
    put_in, income = _trade_flows(events, acct, d0, d1, valuer.prices)
    rows, missing = [], []
    for key in sorted(set(h0) | set(h1) | set(put_in) | set(income)):
        prices = valuer.prices.get(key, [])
        (v0, s0), (v1, s1) = _value(h0.get(key, ZERO), prices, d0), _value(h1.get(key, ZERO), prices, d1)
        if v0 is None or v1 is None:
            missing.append(key)
            continue
        native = v1 - v0 - put_in.get(key, ZERO) + income.get(key, ZERO)
        status = "complete" if s0 == s1 == "complete" else "interpolated"
        rows.append({"key": key, "native": native, "currency": valuer.acct["currency"], "status": status})
    return rows, missing


def _position_values(snap: dict) -> dict:
    out = {}
    for p in snap["positions"]:
        qty = Decimal(p["quantity"])
        if p.get("unsupported") or qty == ZERO:
            continue
        out[p["isin"] or p["symbol"]] = (qty, Decimal(p["value"]) / qty)
    return out


def from_snapshots(valuer, snaps: list, d0: str, d1: str) -> tuple:
    """Rows for a snapshot account: price effect on the opening quantity between two statements (always approximate)."""
    dated = sorted((s for s in snaps if s["positions"] and s["date"] <= d1), key=lambda s: s["date"])
    if not dated:
        return [], []
    end = dated[-1]
    start = next((s for s in reversed(dated) if s["date"] <= d0), dated[0])
    if start["date"] >= end["date"]:
        return [], []
    p0, p1 = _position_values(start), _position_values(end)
    rows = []
    for key in sorted(set(p0) & set(p1)):
        q0, price0 = p0[key]
        _, price1 = p1[key]
        rows.append(
            {"key": key, "native": q0 * (price1 - price0), "currency": valuer.acct["currency"], "status": "approximate"}
        )
    return rows, []


def merge(per_account: list, names: dict) -> dict:
    """Combine accounts by security key into EUR rows sorted by contribution (best first).

    per_account: [(account id, rows, rates, window end)]; non-EUR amounts are converted at the window end (approximate).
    """
    total: dict = {}
    for _acct, rows, rates, d1 in per_account:
        for r in rows:
            eur, _fx = rates.to_eur(r["native"], r["currency"], d1)
            if eur is None:
                continue
            status = perf.worst(r["status"], "complete" if r["currency"] == "EUR" else "approximate")
            t = total.setdefault(r["key"], {"eur": ZERO, "status": "complete"})
            t["eur"] += eur
            t["status"] = perf.worst(t["status"], status)
    ordered = sorted(total.items(), key=lambda kv: (-kv[1]["eur"], kv[0]))
    out = [
        {"key": k, "name": names.get(k, k), "contribution_eur": _s(v["eur"]), "status": v["status"]} for k, v in ordered
    ]
    return {"rows": out}
