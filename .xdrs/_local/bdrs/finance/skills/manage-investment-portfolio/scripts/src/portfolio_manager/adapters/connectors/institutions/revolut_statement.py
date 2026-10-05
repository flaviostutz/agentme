"""Parse a Revolut Account Statement: per-currency summary, portfolio breakdown and transactions."""

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

NAME = "revolut_statement"
KIND = "ledger"
TIMESTAMP = re.compile(r"^(\d{2} [A-Z][a-z]{2} \d{4}) (\d{2}:\d{2}:\d{2}) GMT$")
SUMMARY = re.compile(r"^([A-Z]{3}) Account summary$")
SYMBOL = re.compile(r"^[A-Z0-9.]{1,8}$")
NOISE = ("Account Statement", "Generated on the ")
TX_HEADER = ["Date", "Symbol", "Type", "Quantity", "Price", "Side", "Value", "Fees", "Commission"]


def detect(doc: Doc) -> bool:
    text = doc.text()
    return "Revolut Securities" in text and "Account Statement" in text and "Portfolio breakdown" in text


def _after(lines: list, label: str, start: int = 0) -> int:
    for i in range(start, len(lines)):
        if lines[i] == label:
            return i
    msg = f"revolut statement: missing section {label!r}"
    raise PmError(msg)


def _pair(lines: list, i: int) -> tuple:
    return parse_money(lines[i + 1])[1], parse_money(lines[i + 2])[1]


def _summary(block: list) -> dict:
    out = {}
    for key, label in (("positions", "Positions Value"), ("cash", "Cash value*"), ("total", "Total")):
        i = _after(block, label)
        out[key] = _pair(block, i)
    return out


def _positions(block: list, ccy: str) -> tuple:
    start = _after(block, "% of Portfolio") + 1
    end = _after(block, "Positions Value", start)
    rows, bad = [], []
    for i in range(start, end):
        if not ISIN_RE.match(block[i]) or i < start + 2:
            continue
        pieces, j = [], i + 1
        while j < end and not block[j].endswith("%"):
            pieces.extend(block[j].split())
            j += 1
        if len(pieces) != 3:
            bad.append(" | ".join(block[i - 2 : j + 1]))
            continue
        qty, price, value = (
            parse_number(pieces[0]),
            parse_money(pieces[1], default_currency=ccy)[1],
            parse_money(pieces[2])[1],
        )
        rows.append(position(block[i], block[i - 2], block[i - 1], qty, price, value, ccy))
    return rows, bad


def _records(block: list) -> list:
    """Split the transactions section into (date, time, tokens)."""
    recs, current = [], None
    stop = block.index("Glossary") if "Glossary" in block else len(block)
    for s in block[:stop]:
        m = TIMESTAMP.match(s)
        if m:
            current = (m.group(1), m.group(2), [])
            recs.append(current)
        elif current is not None and not s.startswith(NOISE) and s not in TX_HEADER:
            current[2].append(s)
    return recs


def _event(account: str, ccy: str, day: str, time: str, tokens: list, ref: str, symbol_isin: dict):
    """Return an event or None when the record layout is unknown."""
    symbol = tokens[0] if tokens and SYMBOL.match(tokens[0]) and not tokens[0][:1].islower() else ""
    body = tokens[1:] if symbol else tokens
    if not body:
        return None
    kind, rest = body[0], body[1:]
    isin = symbol_isin.get(symbol, "")

    def money(s):
        return parse_money(s, default_currency=ccy)[1]

    if kind.startswith("Trade") and len(rest) == 6 and rest[2] in ("Buy", "Sell"):
        qty, price, side = parse_number(rest[0]), money(rest[1]), rest[2]
        value, fees, commission = money(rest[3]), money(rest[4]), money(rest[5])
        cost = fees + commission
        cash = -(value + cost) if side == "Buy" else value - cost
        return event(
            account,
            side.upper(),
            day,
            ref,
            time=time,
            isin=isin,
            symbol=symbol,
            quantity=qty,
            price=price,
            currency=ccy,
            gross=value,
            cash=cash,
            fee=cost,
            raw_type=kind,
        )
    if kind == "Dividend" and len(rest) == 3:
        return event(
            account,
            "DIVIDEND",
            day,
            ref,
            time=time,
            isin=isin,
            symbol=symbol,
            currency=ccy,
            gross=money(rest[0]),
            cash=money(rest[0]),
            raw_type=kind,
        )
    if kind.endswith("fee") and len(rest) == 3 and not symbol:
        return event(
            account,
            "FEE",
            day,
            ref,
            time=time,
            currency=ccy,
            cash=money(rest[0]),
            fee=abs(money(rest[0])),
            raw_type=kind,
        )
    if kind == "Cash top-up" and len(rest) == 3:
        return event(account, "DEPOSIT", day, ref, time=time, currency=ccy, cash=money(rest[0]), raw_type=kind)
    if kind == "Cash withdrawal" and len(rest) == 3:
        return event(account, "WITHDRAWAL", day, ref, time=time, currency=ccy, cash=money(rest[0]), raw_type=kind)
    return None


def parse(doc: Doc, answers: dict) -> list:
    """Return one result per non-empty currency block (usually one)."""
    sha = sha256_file(doc.path)
    lines = [s for s in doc.lines() if not s.startswith(NOISE)]
    number = lines[_after(lines, "Account number") + 1]
    first, last = lines[_after(lines, "Period") + 1].split(" - ")
    pstart, pend = parse_date(first, "dd Mon yyyy"), parse_date(last, "dd Mon yyyy")
    marks = [i for i, s in enumerate(lines) if SUMMARY.match(s)]
    out = []
    for n, i in enumerate(marks):
        block = lines[i : marks[n + 1] if n + 1 < len(marks) else len(lines)]
        ccy = SUMMARY.match(block[0]).group(1)
        summ = _summary(block)
        positions, bad = _positions(block, ccy)
        txs = _records(block[_after(block, f"{ccy} Transactions") :])
        if not positions and not txs and all(v == ZERO for pair in summ.values() for v in pair):
            continue
        acct = account_id("revolut", number) + "-" + ccy.lower()
        res = result(
            NAME,
            KIND,
            {"id": acct, "institution": "revolut", "currency": ccy, "mode": "transactions"},
            {"start": iso(pstart), "end": iso(pend)},
        )
        symbol_isin = {p["symbol"]: p["isin"] for p in positions}
        for k, (day_s, time, tokens) in enumerate(txs):
            day = iso(parse_date(day_s, "dd Mon yyyy"))
            ev = _event(acct, ccy, day, time, tokens, f"{sha[:8]}:tx{k}", symbol_isin)
            if ev is None:
                text = f"{day} {time} " + " | ".join(tokens)
                res["unresolved"].append(
                    unresolved(
                        sha,
                        "unknown-transaction",
                        text,
                        "Which event type is this record, or skip it?",
                        f"{doc.path.name} tx{k}",
                    )
                )
            else:
                res["events"].append(ev)
        for text in bad:
            res["unresolved"].append(
                unresolved(sha, "unparsed-position", text, "How should this position row be read?", doc.path.name)
            )
        eve_day = iso(pend)
        res["snapshots"] = [
            snapshot(
                acct,
                iso(pstart - timedelta(days=1)),
                [],
                cash=summ["cash"][0],
                positions_value=summ["positions"][0],
                total=summ["total"][0],
                currency=ccy,
                ref=f"{sha[:8]}:start",
            ),
            snapshot(
                acct,
                eve_day,
                positions,
                cash=summ["cash"][1],
                positions_value=summ["positions"][1],
                total=summ["total"][1],
                currency=ccy,
                ref=f"{sha[:8]}:end",
            ),
        ]
        res["opening"] = {
            "date": iso(pstart - timedelta(days=1)),
            "cash": dec(summ["cash"][0]),
            "positions_value": dec(summ["positions"][0]),
        }
        pos_sum = sum((Decimal(p["value"]) for p in positions), ZERO)
        cash_sum = sum((Decimal(e["cash"]) for e in res["events"]), ZERO)
        res["checks"] = [
            check(
                "positions value = sum of portfolio rows",
                summ["positions"][1],
                pos_sum,
                rounding_tolerance(len(positions)),
            ),
            check(
                "opening cash + transactions = ending cash",
                summ["cash"][1],
                summ["cash"][0] + cash_sum,
                rounding_tolerance(len(res["events"])),
                max(Decimal(1), summ["total"][1] * Decimal("0.005")),
            ),
            check(
                "cash + positions = total",
                summ["total"][1],
                summ["cash"][1] + summ["positions"][1],
                rounding_tolerance(1),
            ),
        ]
        out.append(res)
    if not out:
        msg = "revolut statement: no non-empty currency block"
        raise PmError(msg)
    return out
