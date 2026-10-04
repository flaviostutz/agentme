# Runtime: Python >=3.11 stdlib only; FIFO lot accounting over canonical events (pure functions, JSON-ready output).
"""FIFO accounting: positions, cash, lots, realized P&L and income per account, transfers keep acquisition date and cost."""

from collections import defaultdict, deque
from decimal import Decimal

from institutions.common import dec
from util import ZERO

EPS = Decimal("0.000001")
PLACES = Decimal("0.0000000001")
FLOW_TYPES = {"DEPOSIT": 1, "WITHDRAWAL": 1, "TRANSFER_IN": 1, "TRANSFER_OUT": 1}


def _opt(value) -> str | None:
    return None if value is None else dec(value.quantize(PLACES))


class Account:
    """Mutable state of one account while events are replayed."""

    def __init__(self, acct: dict, opening: dict, to_eur):
        self.id, self.ccy, self.to_eur = acct["id"], acct["currency"], to_eur
        self.cash = Decimal(opening.get("cash", "0"))
        self.lots: dict = defaultdict(deque)
        self.realized, self.flows, self.errors, self.states = [], [], [], []
        self.income = {"dividends": ZERO, "interest": ZERO, "fees": ZERO, "taxes": ZERO, "withholding": ZERO}
        self.unreliable: set = set()
        self.negative_cash_days: set = set()
        self.opening_date = opening.get("date")
        for p in opening.get("positions", []):
            key = p["isin"] or p["symbol"]
            self.lots[key].append({"acquired": None, "quantity": Decimal(p["quantity"]), "cost": None, "cost_eur": None,
                                   "source": "opening", "symbol": p["symbol"], "name": p["name"]})

    def quantity(self, key: str) -> Decimal:
        return sum((lot["quantity"] for lot in self.lots[key]), ZERO)

    def snapshot_state(self, day: str) -> dict:
        qty = {k: dec(q) for k in sorted(self.lots) if (q := self.quantity(k)) > EPS}
        return {"date": day, "cash": dec(self.cash), "positions": qty}

    def buy(self, e: dict) -> None:
        qty, cost = Decimal(e["quantity"]), -Decimal(e["cash"])
        cost_eur, status = self.to_eur(cost, self.ccy, e["date"])
        self.lots[e["isin"] or e["symbol"]].append({"acquired": e["date"], "quantity": qty, "cost": cost, "cost_eur": cost_eur,
                                                    "source": "trade", "symbol": e["symbol"], "name": e["name"], "fx_status": status})

    def _consume(self, key: str, qty: Decimal) -> tuple:
        """Take qty FIFO; returns (consumed parts [(lot, taken)], shortfall)."""
        parts, left = [], qty
        lots = self.lots[key]
        while left > EPS and lots:
            lot = lots[0]
            take = min(lot["quantity"], left)
            parts.append((dict(lot), take))
            if take >= lot["quantity"] - EPS:
                lots.popleft()
            else:
                ratio = (lot["quantity"] - take) / lot["quantity"]
                lot["cost"] = None if lot["cost"] is None else lot["cost"] * ratio
                lot["cost_eur"] = None if lot["cost_eur"] is None else lot["cost_eur"] * ratio
                lot["quantity"] -= take
            left -= take
        return parts, max(left, ZERO)

    def sell(self, e: dict) -> None:
        key, qty, proceeds = e["isin"] or e["symbol"], Decimal(e["quantity"]), Decimal(e["cash"])
        parts, short = self._consume(key, qty)
        if short > EPS:
            self.errors.append(f"{self.id}: {e['date']} sold {dec(qty)} of {key} but only {dec(qty - short)} was held; position unreliable")
            self.unreliable.add(key)
        proceeds_eur, status = self.to_eur(proceeds, self.ccy, e["date"])
        for lot, take in parts:
            share = take / qty
            part_proceeds = proceeds * share
            cost = None if lot["cost"] is None else lot["cost"] * take / lot["quantity"]
            part_eur = None if proceeds_eur is None else proceeds_eur * share
            cost_eur = None if lot["cost_eur"] is None else lot["cost_eur"] * take / lot["quantity"]
            self.realized.append({
                "date": e["date"], "isin": key, "symbol": e["symbol"], "acquired": lot["acquired"], "quantity": dec(take),
                "proceeds": dec(part_proceeds), "cost": _opt(cost), "pnl": _opt(None if cost is None else part_proceeds - cost),
                "proceeds_eur": _opt(part_eur), "cost_eur": _opt(cost_eur),
                "pnl_eur": _opt(None if cost_eur is None or part_eur is None else part_eur - cost_eur),
                "cost_status": "complete" if cost is not None else "unavailable", "fx_status": status})

    def split(self, e: dict) -> None:
        key = e["isin"] or e["symbol"]
        total = self.quantity(key)
        if total <= EPS:
            self.errors.append(f"{self.id}: {e['date']} split on {key} with no position")
            return
        ratio = (total + Decimal(e["quantity"])) / total
        for lot in self.lots[key]:
            lot["quantity"] *= ratio

    def apply(self, e: dict) -> None:
        kind = e["type"]
        self.cash += Decimal(e["cash"])
        if self.cash < -EPS:
            self.negative_cash_days.add(e["date"])
        if kind == "BUY":
            self.buy(e)
        elif kind == "SELL":
            self.sell(e)
        elif kind == "SPLIT":
            self.split(e)
        elif kind == "DIVIDEND":
            self.income["dividends"] += Decimal(e["cash"])
            self.income["withholding"] += Decimal(e["tax"])
        elif kind == "INTEREST":
            self.income["interest"] += Decimal(e["cash"])
        elif kind == "FEE":
            self.income["fees"] += -Decimal(e["cash"])
        elif kind == "TAX":
            self.income["taxes"] += -Decimal(e["cash"])
        if kind in FLOW_TYPES:
            self.flows.append({"date": e["date"], "type": kind, "amount": dec(Decimal(e["cash"]))})

    def result(self) -> dict:
        open_lots = [{"isin": k, "symbol": lot["symbol"], "name": lot["name"], "acquired": lot["acquired"],
                      "quantity": dec(lot["quantity"]), "cost": _opt(lot["cost"]), "cost_eur": _opt(lot["cost_eur"]), "source": lot["source"]}
                     for k in sorted(self.lots) for lot in self.lots[k] if lot["quantity"] > EPS]
        known = [r for r in self.realized if r["pnl"] is not None]
        return {"account": self.id, "currency": self.ccy, "opening_date": self.opening_date, "cash": dec(self.cash), "lots": open_lots,
                "realized": self.realized, "realized_status": "complete" if len(known) == len(self.realized) else "partial",
                "income": {k: dec(v) for k, v in self.income.items()}, "flows": self.flows, "states": self.states,
                "errors": self.errors, "unreliable": sorted(self.unreliable), "negative_cash_days": sorted(self.negative_cash_days)}


def _scaled(lot: dict, take: Decimal) -> dict:
    """A part of a lot keeps its acquisition date and the proportional cost."""
    ratio = take / lot["quantity"]
    return dict(lot, quantity=take, cost=None if lot["cost"] is None else lot["cost"] * ratio,
                cost_eur=None if lot["cost_eur"] is None else lot["cost_eur"] * ratio)


def run(accounts: list, openings: dict, events: list, to_eur) -> dict:
    """Replay all events (already sorted) per transaction account; TRANSFER_OUT lots move into the matching TRANSFER_IN."""
    engines = {a["id"]: Account(a, openings.get(a["id"], {}), to_eur) for a in accounts if a["mode"] == "transactions"}
    in_flight: dict = {}
    last_day: dict = {}
    for e in events:
        eng = engines.get(e["account"])
        if eng is None:
            continue
        if last_day.get(eng.id) not in (None, e["date"]):
            eng.states.append(eng.snapshot_state(last_day[eng.id]))
        last_day[eng.id] = e["date"]
        if e["type"] == "TRANSFER_OUT":
            key = e["isin"] or e["symbol"]
            parts, short = eng._consume(key, Decimal(e["quantity"]))
            in_flight[(key, e["date"], e["quantity"])] = [_scaled(lot, take) for lot, take in parts]
            if short > EPS:
                eng.errors.append(f"{eng.id}: {e['date']} transfer out of {key} exceeds the held quantity")
        elif e["type"] == "TRANSFER_IN":
            key = e["isin"] or e["symbol"]
            moved = in_flight.pop((key, e["date"], e["quantity"]), None)
            if moved is None:
                eng.lots[key].append({"acquired": None, "quantity": Decimal(e["quantity"]), "cost": None, "cost_eur": None,
                                      "source": "transfer", "symbol": e["symbol"], "name": e["name"]})
            else:
                eng.lots[key].extend(moved)
        eng.apply(e)
    for acct_id, day in last_day.items():
        engines[acct_id].states.append(engines[acct_id].snapshot_state(day))
    return {k: engines[k].result() for k in sorted(engines)}
