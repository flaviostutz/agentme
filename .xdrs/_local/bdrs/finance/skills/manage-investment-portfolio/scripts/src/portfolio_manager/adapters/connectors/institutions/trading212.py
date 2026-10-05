"""Parse a Trading 212 Activity statement: overview totals, executed trades, open positions, cash, transactions, dividends."""

import re
from datetime import timedelta
from decimal import Decimal

from portfolio_manager.app.records import (
    ISIN_RE,
    account_id,
    check,
    dec,
    event,
    position,
    result,
    rounding_tolerance,
    snapshot,
    unresolved,
)
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import ZERO, iso, parse_date, parse_money, parse_number, sha256_file

NAME = "trading212"
KIND = "ledger"
TS = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})$")
PAGE_NO = re.compile(r"^\d+/\d+$")
FOOTERS = ("Trading 212 EU GmbH receives", "Your cash is safeguarded")
OVERVIEW = (
    "Deposits",
    "Withdrawals",
    "Realised return",
    "Open return",
    "Open return change",
    "Dividends",
    "Interest on cash",
    "FX fee",
    "Third-party fees",
    "Account value",
)
COVER = re.compile(r"covering from (\d{2}\.\d{2}\.\d{4}) (\d{2}):\d{2} \(UTC\) to (\d{2}\.\d{2}\.\d{4}) (\d{2}):\d{2}")


def detect(doc: Doc) -> bool:
    text = doc.text()
    return "Trading 212" in text and "Activity statement" in text


def _lines(doc: Doc) -> list:
    out = []
    for page in doc.pages:
        rows = page[4:] if page[:1] == ["CUSTOMER ID"] else page
        out += [s for s in rows if not PAGE_NO.match(s) and not s.startswith(FOOTERS)]
    return out


def _index(lines: list, label: str, start: int = 0) -> int:
    for i in range(start, len(lines)):
        if lines[i] == label:
            return i
    msg = f"trading212: missing section {label!r}"
    raise PmError(msg)


def _money(token: str, default: str = "") -> Decimal:
    return ZERO if token == "-" else parse_money(token, default_currency=default)[1]  # noqa: S105


def _trade(acct: str, ccy: str, day: str, time: str, t: list, ref: str):
    if len(t) < 15 or not ISIN_RE.match(t[1]) or t[3] not in ("Buy", "Sell"):
        return None
    side = t[3]
    pccy, price = parse_money(t[5], default_currency=ccy)
    value = parse_money(t[6])[1]
    fx_rate = parse_number(t[10]) if t[10] != "-" else None
    fees = _money(t[11]) + _money(t[12])
    eur = parse_money(t[14])[1]
    cash = -(eur + fees) if side == "Buy" else eur - fees
    return event(
        acct,
        side.upper(),
        day,
        ref,
        time=time,
        isin=t[1],
        symbol=t[0],
        quantity=parse_number(t[4]),
        price=price,
        currency=pccy,
        gross=value,
        fx_rate=fx_rate,
        cash=cash,
        fee=fees,
        raw_type=f"order {t[2]}",
    )


def _overview(lines: list) -> dict:
    out = {}
    for i, s in enumerate(lines[:60]):
        if s in OVERVIEW and i + 1 < len(lines):
            try:
                out[s] = parse_money(lines[i + 1])[1]
            except ValueError:
                continue
    return out


def parse(doc: Doc, answers: dict) -> list:
    sha = sha256_file(doc.path)
    lines = _lines(doc)
    text = " ".join(lines[:40])
    m = COVER.search(text)
    num = re.search(r"Account ID: (\w+)", text)
    if not m or not num:
        msg = "trading212: missing period or account id in the first page"
        raise PmError(msg)
    start = parse_date(m.group(1), "dd.mm.yyyy") + (timedelta(days=1) if int(m.group(2)) >= 12 else timedelta(0))
    end = parse_date(m.group(3), "dd.mm.yyyy")
    ov = _overview(lines)
    ccy = parse_money(lines[lines.index("Deposits") + 1])[0] or "EUR"
    acct = account_id("trading212", num.group(1))
    res = result(
        NAME,
        KIND,
        {"id": acct, "institution": "trading212", "currency": ccy, "mode": "transactions"},
        {"start": iso(start), "end": iso(end)},
    )

    def unres(kind, text, where) -> None:
        res["unresolved"].append(
            unresolved(sha, kind, text, "How should this record be read, or skip it?", f"{doc.path.name} {where}")
        )

    t0, t1 = _index(lines, "Invest account - executed trades"), _index(lines, "Invest account - open positions summary")
    for i in range(t0, t1):
        mt = TS.match(lines[i])
        if mt:
            ev = _trade(acct, ccy, mt.group(1), mt.group(2), lines[i + 1 : i + 16], f"{sha[:8]}:trade{i}")
            if ev is None:
                unres("unknown-trade", " | ".join(lines[i : i + 16]), f"line {i}")
            else:
                res["events"].append(ev)

    c0 = _index(lines, "Invest account - cash breakdown")
    positions = []
    for i in range(t1, c0):
        if ISIN_RE.match(lines[i]) and i > t1 and i + 9 <= c0:
            r = lines[i - 1 : i + 9]
            pccy, price = parse_money(r[4], default_currency=ccy)
            positions.append(position(r[1], r[0], "", parse_number(r[2]), price, parse_money(r[9])[1], ccy))
            positions[-1]["price_currency"] = pccy
    cash = parse_money(lines[_index(lines, "EUR cash", c0) + 1])[1]

    x0 = _index(lines, "Invest account - transactions and dividends")
    d0 = _index(lines, "Dividends", x0 + 2)
    for i in range(x0, d0):
        mt = TS.match(lines[i])
        if not mt or i + 2 >= d0:
            continue
        kind, amount = lines[i + 1], parse_money(lines[i + 2])[1]
        low = kind.lower()
        etype = (
            "INTEREST" if "interest" in low else "FEE" if "fee" in low else "DEPOSIT" if amount > 0 else "WITHDRAWAL"
        )
        if not re.search(r"deposit|transfer|ideal|sepa|card|withdraw|interest|fee|bank|adyen|payment", low):
            unres("unknown-transaction", f"{mt.group(1)} {kind} {amount}", f"line {i}")
            continue
        res["events"].append(
            event(
                acct,
                etype,
                mt.group(1),
                f"{sha[:8]}:cash{i}",
                time=mt.group(2),
                currency=ccy,
                cash=amount,
                raw_type=kind,
            )
        )
    for i in range(d0, len(lines)):
        if not ISIN_RE.match(lines[i]) or i + 10 > len(lines):
            continue
        r = lines[i - 1 : i + 10]
        try:
            pay = parse_date(r[4].split()[0], "dd.mm.yyyy")
            dccy, total = parse_money(r[6])
            rate = parse_number(r[9])
            net = parse_money(r[10])[1]
            wht = parse_money(r[8])[1] * rate
        except ValueError:
            continue
        res["events"].append(
            event(
                acct,
                "DIVIDEND",
                iso(pay),
                f"{sha[:8]}:div{i}",
                time=r[4].split()[1],
                isin=r[1],
                symbol=r[0],
                quantity=parse_number(r[3]),
                currency=dccy or ccy,
                gross=total,
                cash=net,
                tax=wht,
            )
        )

    res["snapshots"] = [
        snapshot(
            acct,
            iso(end),
            positions,
            cash=cash,
            positions_value=sum((Decimal(p["value"]) for p in positions), ZERO),
            total=ov.get("Account value"),
            currency=ccy,
            ref=f"{sha[:8]}:end",
        )
    ]
    ev = res["events"]

    def by(t):
        return sum((Decimal(e["cash"]) for e in ev if e["type"] == t), ZERO)

    flows = sum((Decimal(e["cash"]) for e in ev), ZERO)
    opening = cash - flows
    res["opening"] = {"date": iso(start - timedelta(days=1)), "cash": dec(opening), "derived": True}
    n_div = sum(1 for e in ev if e["type"] == "DIVIDEND")
    res["checks"] = [
        check(
            "account value = positions + cash",
            ov.get("Account value", ZERO),
            cash + sum((Decimal(p["value"]) for p in positions), ZERO),
            rounding_tolerance(len(positions) + 1),
        ),
        check("deposits = overview", ov.get("Deposits", ZERO), by("DEPOSIT"), rounding_tolerance(1)),
        check("withdrawals = overview", ov.get("Withdrawals", ZERO), -by("WITHDRAWAL"), rounding_tolerance(1)),
        check(
            "dividends = overview",
            ov.get("Dividends", ZERO),
            by("DIVIDEND"),
            rounding_tolerance(n_div),
            Decimal("0.05") * (n_div or 1),
        ),
        check(
            "opening cash derived from the statement is zero",
            ZERO,
            opening,
            rounding_tolerance(len(ev)),
            max(Decimal(1), cash * Decimal("0.01")),
        ),
    ]
    return [res]
