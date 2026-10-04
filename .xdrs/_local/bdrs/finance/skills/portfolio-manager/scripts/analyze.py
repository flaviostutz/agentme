# Runtime: Python >=3.11 stdlib only; builds the derived analysis (valuations, returns, bridge, assets) from the canonical ledger.
"""Analysis orchestrator: accounting -> reconciliation -> valuation timelines -> period metrics -> aggregation."""

import calendar
import unicodedata
from datetime import date
from decimal import Decimal
from itertools import pairwise

import accounting
import performance as perf
import reconcile
from institutions.common import dec
from util import ZERO


def norm(name: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", name.lower()) if unicodedata.category(c) != "Mn").strip()


def _opt(v) -> str | None:
    return None if v is None else dec(v.quantize(Decimal("0.000001")))


def month_ends(first: str, last: str) -> list:
    """Month-end dates from the month of first up to the month of last (the last entry is capped at last)."""
    d0, d1 = date.fromisoformat(first), date.fromisoformat(last)
    out, y, m = [], d0.year, d0.month
    while (y, m) <= (d1.year, d1.month):
        end = date(y, m, calendar.monthrange(y, m)[1])
        out.append(min(end, d1).isoformat())
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _supported_total(snap: dict) -> Decimal | None:
    supported = sum((Decimal(p["value"]) for p in snap["positions"] if not p.get("unsupported")), ZERO)
    if snap["total"] is None:
        return supported if snap["positions"] else None
    unsupported = sum((Decimal(p["value"]) for p in snap["positions"] if p.get("unsupported")), ZERO)
    return Decimal(snap["total"]) - unsupported


class Valuer:
    """Native-currency value of one account at any date plus its external flows."""

    def __init__(self, acct: dict, res: dict | None, opening: dict, snaps: list, events: list, refs: list):
        self.acct, self.res, self.opening = acct, res, opening
        self.checkpoints = sorted((s["date"], _supported_total(s)) for s in snaps if _supported_total(s) is not None)
        self.mode = acct["mode"]
        if self.mode == "transactions" and opening.get("date") and not opening.get("positions") and opening["date"] not in dict(self.checkpoints):
            self.checkpoints = sorted([*self.checkpoints, (opening["date"], Decimal(opening.get("cash", "0")))])  # empty account at opening
        self.flow_status = "complete"
        self.flows: list = []
        self.prices: dict = {}
        if self.mode == "transactions":
            self._init_transactions(snaps, events)
        else:
            self._init_snapshot_flows(snaps, refs)
        self.first = self.checkpoints[0][0] if self.checkpoints else None
        self.last = self.checkpoints[-1][0] if self.checkpoints else None

    def _init_transactions(self, snaps: list, events: list) -> None:
        obs: dict = {}
        for s in snaps:
            for p in s["positions"]:
                if p["price"] is not None:
                    obs.setdefault(p["isin"] or p["symbol"], {})[s["date"]] = Decimal(p["price"])
        for e in events:
            if e["account"] == self.acct["id"] and e["type"] in ("BUY", "SELL") and Decimal(e["quantity"]) > ZERO:
                obs.setdefault(e["isin"] or e["symbol"], {})[e["date"]] = abs(Decimal(e["cash"])) / Decimal(e["quantity"])
        self.prices = {k: sorted(v.items()) for k, v in obs.items()}
        self.flows = [{"date": f["date"], "amount": Decimal(f["amount"]), "status": "complete"} for f in (self.res or {}).get("flows", [])
                      if f["type"] in ("DEPOSIT", "WITHDRAWAL")]

    def _init_snapshot_flows(self, snaps: list, refs: list) -> None:
        acct = self.acct["id"]
        if self.mode == "snapshot":
            ordered = sorted((s for s in snaps if s["positions"]), key=lambda s: s["date"])
            for a, b in pairwise(ordered):
                qa = {p["isin"]: Decimal(p["quantity"]) for p in a["positions"]}
                amount = ZERO
                for p in b["positions"]:
                    amount += (Decimal(p["quantity"]) - qa.get(p["isin"], ZERO)) * Decimal(p["price"])
                for isin, q in qa.items():
                    if isin not in {p["isin"] for p in b["positions"]}:
                        amount -= q * Decimal(next(p["price"] for p in a["positions"] if p["isin"] == isin))
                mid = date.fromisoformat(a["date"]) + (date.fromisoformat(b["date"]) - date.fromisoformat(a["date"])) / 2
                self.flows.append({"date": mid.isoformat(), "amount": amount, "status": "approximate"})
            for r in (r for r in refs if r["kind"] == "tax-dividend" and r["account"] == acct):
                self.flows.append({"date": r["date"], "amount": -Decimal(r["income"]), "status": "complete"})
        else:
            for r in (r for r in refs if r["kind"] == "period-flows" and r["account"] == acct and not norm(r["asset"]).startswith("poupanca")):
                span = date.fromisoformat(r["to"]) - date.fromisoformat(r["from"])
                mid = (date.fromisoformat(r["from"]) + span / 2).isoformat()
                self.flows.append({"date": mid, "amount": Decimal(r["entries"]) - Decimal(r["exits"]), "status": "approximate"})
        if any(f["status"] != "complete" for f in self.flows):
            self.flow_status = "approximate"

    def holdings_at(self, day: str) -> tuple:
        states = (self.res or {}).get("states", [])
        best = None
        for s in states:
            if s["date"] <= day:
                best = s
        if best is not None:
            return Decimal(best["cash"]), {k: Decimal(v) for k, v in best["positions"].items()}
        return Decimal(self.opening.get("cash", "0")), {(p["isin"] or p["symbol"]): Decimal(p["quantity"]) for p in self.opening.get("positions", [])}

    def _between_statements(self, day: str) -> Decimal:
        """Value between two statements: known flows at their dates, the remaining gain spread linearly over time."""
        before = [c for c in self.checkpoints if c[0] < day][-1]
        after = next(c for c in self.checkpoints if c[0] > day)
        flow_to_day = sum((f["amount"] for f in self.flows if before[0] < f["date"] <= day), ZERO)
        flow_total = sum((f["amount"] for f in self.flows if before[0] < f["date"] <= after[0]), ZERO)
        frac = Decimal(perf.days_between(before[0], day)) / Decimal(perf.days_between(before[0], after[0]))
        return before[1] + flow_to_day + (after[1] - before[1] - flow_total) * frac

    def value(self, day: str) -> tuple:
        if self.first is None or day < self.first:
            return None, "unavailable"
        exact = dict(self.checkpoints)
        if day in exact:
            return exact[day], "complete"
        if self.mode != "transactions":
            if day > self.last:
                return None, "unavailable"
            return self._between_statements(day), "interpolated"
        cash, holdings = self.holdings_at(day)
        total, status = cash, "interpolated"
        for key, qty in holdings.items():
            price, st = perf.interpolate(self.prices.get(key, []), day)
            if price is None:
                return None, "unavailable"
            total += qty * price
            status = perf.worst(status, st if st != "complete" else "interpolated")
        return total, status


class Eur:
    """EUR view of a Valuer: values at the date's rate, flows at their own date's rate."""

    def __init__(self, valuer: Valuer, rates):
        self.v, self.rates, self.ccy = valuer, rates, valuer.acct["currency"]

    def value(self, day: str) -> tuple:
        native, st = self.v.value(day)
        if native is None:
            return None, "unavailable"
        eur, fx = self.rates.to_eur(native, self.ccy, day)
        if eur is None:
            return None, "unavailable"
        return eur, perf.worst(st, "approximate" if fx not in ("exact",) else "complete")

    def flows(self) -> list:
        out = []
        for f in self.v.flows:
            eur, fx = self.rates.to_eur(f["amount"], self.ccy, f["date"])
            if eur is not None:
                out.append({"date": f["date"], "amount": eur, "status": perf.worst(f["status"], "approximate" if fx != "exact" else "complete")})
        return out


class Portfolio:
    """Sum of EUR views; an account counts as 0 before its first valuation and makes the date unavailable after its last one."""

    def __init__(self, parts: list):
        self.parts = [p for p in parts if p.v.first is not None]
        self.first = min(p.v.first for p in self.parts)

    def value(self, day: str) -> tuple:
        total, status = ZERO, "complete"
        for p in self.parts:
            if day < p.v.first:
                continue
            v, st = p.value(day)
            if v is None:
                return None, "unavailable"
            total += v
            status = perf.worst(status, st)
        return total, status

    def flows(self) -> list:
        """Pooled flows; an account that starts being tracked later enters as an inflow of its first valuation."""
        out = [f for p in self.parts for f in p.flows()]
        for p in self.parts:
            if p.v.first > self.first:
                value, status = p.value(p.v.first)
                out.append({"date": p.v.first, "amount": value, "status": perf.worst(status, "approximate")})
        return sorted(out, key=lambda f: f["date"])


def fx_effect(view, d0: str, d1: str) -> Decimal | None:
    """EUR gain minus the native gain converted at the end rate, summed over non-EUR accounts (None when nothing to convert)."""
    parts = view.parts if isinstance(view, Portfolio) else [view]
    total, seen = ZERO, False
    for p in parts:
        if p.ccy == "EUR" or d1 < p.v.first:
            continue
        a, b = max(d0, p.v.first), min(d1, p.v.last)
        (n0, _), (n1, _), (e0, _), (e1, _) = p.v.value(a), p.v.value(b), p.value(a), p.value(b)
        if None in (n0, n1, e0, e1):
            continue
        fn = sum((f["amount"] for f in p.v.flows if a < f["date"] <= b), ZERO)
        fe = sum((f["amount"] for f in p.flows() if a < f["date"] <= b), ZERO)
        rate_end = p.rates.rate(p.ccy, b)["rate"]
        total += (e1 - e0 - fe) - (n1 - n0 - fn) / rate_end
        seen = True
    return total if seen else None


def metrics(view, d0: str, d1: str) -> dict:
    """Period metrics for an Eur view or Portfolio between two dates."""
    flows = view.flows()
    v0, s0 = view.value(d0)
    v1, s1 = view.value(d1)
    in_period = [f for f in flows if d0 < f["date"] <= d1]
    net = sum((f["amount"] for f in in_period), ZERO)
    flow_status = perf.worst(*(f["status"] for f in in_period)) if in_period else "complete"
    t = perf.twr(view.value, flows, d0, d1)
    if t["status"] != "unavailable":
        t["status"] = perf.worst(t["status"], flow_status)
    out = {"from": d0, "to": d1, "start_value": _opt(v0), "end_value": _opt(v1), "net_flows": dec(net),
           "start_status": s0, "end_status": s1, "twr": _opt(t["value"]), "twr_status": t["status"], "twr_reason": t["reason"]}
    if v0 is None or v1 is None:
        out.update(gain=None, period_return=None, period_return_status="unavailable", xirr=None, xirr_status="unavailable", xirr_reason="missing valuation")
        return out
    out["gain"] = dec(v1 - v0 - net)
    out["fx_effect"] = _opt(fx_effect(view, d0, d1))
    pr = perf.period_return(v0, v1, in_period, d0, d1)
    out.update(period_return=_opt(pr["value"]), period_return_status=pr["status"])
    x = perf.xirr(in_period, d0, d1, v0, v1)
    out.update(xirr=_opt(x["value"]), xirr_status=perf.worst(x["status"], flow_status) if x["status"] != "unavailable" else "unavailable",
               xirr_annualized=x["annualized"], xirr_reason=x["reason"])
    return out


def periods(first: str, last: str) -> list:
    """Calendar months and years inside [first, last], plus YTD and inception."""
    out = [{"label": "inception", "from": first, "to": last}]
    ends = month_ends(first, last)
    prev = first
    for e in ends:
        out.append({"label": f"month {e[:7]}", "from": prev, "to": e})
        prev = e
    years = sorted({e[:4] for e in ends})
    for y in years:
        start = max(first, f"{int(y) - 1}-12-31")
        end = min(last, f"{y}-12-31")
        if start < end:
            out.append({"label": f"year {y}", "from": start, "to": end})
    ly = last[:4]
    out.append({"label": f"ytd {ly}", "from": max(first, f"{int(ly) - 1}-12-31"), "to": last})
    return [p for p in out if p["from"] < p["to"]]


def assets_table(acct: dict, res: dict | None, snaps: list, rates) -> list:
    """Latest statement positions with lots-based cost and realized P&L when the account has transactions."""
    with_pos = [s for s in snaps if s["positions"]]
    if not with_pos:
        return []
    snap = max(with_pos, key=lambda s: s["date"])
    rows = []
    for p in snap["positions"]:
        key = p["isin"] or p["symbol"]
        row = {"account": acct["id"], "isin": p["isin"], "symbol": p["symbol"], "name": p["name"], "currency": p["currency"],
               "quantity": p["quantity"], "price": p["price"], "value": p["value"], "as_of": snap["date"], "unsupported": bool(p.get("unsupported")),
               "asset_class": p.get("asset_class"),
               "value_eur": _opt(rates.to_eur(Decimal(p["value"]), p["currency"], snap["date"])[0])}
        if res is not None:
            lots = [lot for lot in res["lots"] if lot["isin"] == key]
            realized = [r for r in res["realized"] if r["isin"] == key]
            costs = [lot["cost"] for lot in lots]
            row.update(lots=lots, cost=None if not lots or any(c is None for c in costs) else dec(sum((Decimal(c) for c in costs), ZERO)),
                       realized_pnl=dec(sum((Decimal(r["pnl"]) for r in realized if r["pnl"] is not None), ZERO)) if realized else None,
                       realized_status="complete" if realized and all(r["pnl"] is not None for r in realized) else ("partial" if realized else "none"))
        rows.append(row)
    return rows


def _flatten_checks(rows: list) -> dict:
    counts = {"ok": 0, "warn": 0, "fail": 0}
    for r in rows:
        counts[r["level"]] += 1
    return counts


def analyze(data: dict, rates) -> dict:
    """data: accounts, openings, events, snapshots, references. Returns the JSON-ready analysis."""
    accounts, openings = data["accounts"]["accounts"], data["accounts"]["openings"]
    events, snapshots, refs = data["events"], data["snapshots"], data["references"]
    for e in events:
        if e.get("fx_rate") and e["currency"] != "EUR":
            rates.add_statement(e["currency"], e["date"], Decimal(e["fx_rate"]))
    acct_res = accounting.run(accounts, openings, events, lambda amt, ccy, day: rates.to_eur(amt, ccy, day))
    checks = reconcile.reconcile(acct_res, events, snapshots, refs, openings)
    views, per_account, excluded = {}, {}, []
    for a in accounts:
        snaps = [s for s in snapshots if s["account"] == a["id"]]
        valuer = Valuer(a, acct_res.get(a["id"]), openings.get(a["id"], {}), snaps, events, refs)
        if valuer.first is None:
            continue
        view = Eur(valuer, rates)
        if rates.to_eur(Decimal(1), a["currency"], valuer.last)[0] is None:
            excluded.append({"account": a["id"], "reason": f"no {a['currency']} rate for {valuer.last}"})
            continue
        views[a["id"]] = view
        per_account[a["id"]] = {
            "account": a, "first": valuer.first, "last": valuer.last, "flows_status": valuer.flow_status,
            "latest_value": _opt(valuer.value(valuer.last)[0]), "latest_value_eur": _opt(view.value(valuer.last)[0]),
            "periods": [dict(p, **metrics(view, p["from"], p["to"])) for p in periods(valuer.first, valuer.last)],
            "accounting": acct_res.get(a["id"]), "assets": assets_table(a, acct_res.get(a["id"]), snaps, rates)}
    portfolio = {}
    if views:
        pf = Portfolio(list(views.values()))
        common = min(v.v.last for v in views.values())
        portfolio = {"first": pf.first, "common_date": common, "value_eur": _opt(pf.value(common)[0]), "value_status": pf.value(common)[1],
                     "periods": [dict(p, **metrics(pf, p["from"], p["to"])) for p in periods(pf.first, common)],
                     "accounts": [{"account": k, "last": v.v.last, "value": _opt(v.v.value(v.v.last)[0]), "currency": v.ccy,
                                   "value_eur": _opt(v.value(v.v.last)[0])} for k, v in sorted(views.items())]}
    return {"portfolio": portfolio, "accounts": per_account, "excluded": excluded, "checks": checks, "check_counts": _flatten_checks(checks),
            "cost_reports": [r for r in refs if r["kind"] == "cost-report"],
            "errors": [e for r in acct_res.values() for e in r["errors"]]}
