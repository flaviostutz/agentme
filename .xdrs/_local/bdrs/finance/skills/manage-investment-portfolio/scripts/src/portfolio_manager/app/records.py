"""Canonical record builders (events, snapshots, checks, unresolved items) shared by all adapters."""

import hashlib
import re
from decimal import Decimal

from portfolio_manager.shared.values import ZERO, fmt_decimal

EVENT_TYPES = (
    "BUY",
    "SELL",
    "DIVIDEND",
    "INTEREST",
    "FEE",
    "TAX",
    "DEPOSIT",
    "WITHDRAWAL",
    "SPLIT",
    "TRANSFER_IN",
    "TRANSFER_OUT",
)
ISIN_RE = re.compile(r"^[A-Z]{2}[A-Z0-9]{9}\d$")


def dec(value) -> str:
    return fmt_decimal(Decimal(value))


def short_hash(*parts) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode(), usedforsecurity=False).hexdigest()[:12]


def account_id(prefix: str, number: str, drop_suffix: bool = False) -> str:
    """Institution prefix + last 4 alphanumerics of the account number; drop_suffix ignores a trailing sub-account '-<digit>'."""
    base = re.sub(r"-\d$", "", number.strip()) if drop_suffix else number
    tail = re.sub(r"[^A-Za-z0-9]", "", base)[-4:].lower()
    return f"{prefix}-{tail}"


def event(
    account: str,
    etype: str,
    day: str,
    ref: str,
    *,
    time: str = "",
    isin: str = "",
    symbol: str = "",
    name: str = "",
    quantity: Decimal = ZERO,
    price: Decimal | None = None,
    currency: str = "",
    gross: Decimal | None = None,
    fx_rate: Decimal | None = None,
    cash: Decimal = ZERO,
    fee: Decimal = ZERO,
    tax: Decimal = ZERO,
    raw_type: str = "",
) -> dict:
    """Cash = signed net effect on the account cash (fees and taxes included); fee/tax are informational parts."""
    rec = {
        "account": account,
        "type": etype,
        "date": day,
        "time": time,
        "isin": isin,
        "symbol": symbol,
        "name": name,
        "quantity": dec(quantity),
        "currency": currency,
        "cash": dec(cash),
        "fee": dec(fee),
        "tax": dec(tax),
        "ref": ref,
    }
    if price is not None:
        rec["price"] = dec(price)
    if gross is not None:
        rec["gross"] = dec(gross)
    if fx_rate is not None:
        rec["fx_rate"] = dec(fx_rate)
    if raw_type:
        rec["raw_type"] = raw_type
    return rec


def position(isin: str, symbol: str, name: str, quantity, price, value, currency: str) -> dict:
    return {
        "isin": isin,
        "symbol": symbol,
        "name": name,
        "quantity": None if quantity is None else dec(quantity),
        "price": None if price is None else dec(price),
        "value": dec(value),
        "currency": currency,
    }


def snapshot(
    account: str, day: str, positions: list, *, cash=None, positions_value=None, total=None, currency: str, ref: str
) -> dict:
    return {
        "account": account,
        "date": day,
        "positions": positions,
        "currency": currency,
        "ref": ref,
        "cash": None if cash is None else dec(cash),
        "positions_value": None if positions_value is None else dec(positions_value),
        "total": None if total is None else dec(total),
    }


def check(
    name: str, expected: Decimal, actual: Decimal, tolerance: Decimal, warn_tolerance: Decimal | None = None
) -> dict:
    """level: ok within tolerance, warn within warn_tolerance (an unexplained residual is reported), else fail."""
    diff = abs(Decimal(expected) - Decimal(actual))
    level = "ok" if diff <= tolerance else "warn" if warn_tolerance is not None and diff <= warn_tolerance else "fail"
    return {
        "name": name,
        "expected": dec(expected),
        "actual": dec(actual),
        "diff": dec(Decimal(actual) - Decimal(expected)),
        "tolerance": dec(tolerance),
        "level": level,
    }


def rounding_tolerance(rows: int, base: str = "0.01") -> Decimal:
    """Sums of rows printed with 2 decimals can drift by half a cent per row."""
    return Decimal(base) + Decimal("0.005") * rows


def unresolved(source_sha: str, kind: str, text: str, question: str, where: str = "") -> dict:
    return {
        "id": short_hash(source_sha, kind, text),
        "kind": kind,
        "text": text[:400],
        "where": where,
        "question": question,
    }


def result(adapter: str, kind: str, account: dict, period: dict) -> dict:
    return {
        "adapter": adapter,
        "kind": kind,
        "account": account,
        "period": period,
        "events": [],
        "snapshots": [],
        "references": [],
        "unresolved": [],
        "checks": [],
        "opening": {},
    }
