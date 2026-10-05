"""Validate normalized transaction files of one analysis.

accounts  per account: continuity, missing months, rows repeated in overlapping files; one currency; row count warning
file      one normalized file for a phase (convert | auto | final); convert also writes the snapshot
"""

import re
from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from itertools import pairwise
from pathlib import Path
from typing import Any

from analyse_account_transactions.app import ledger
from analyse_account_transactions.app.ports import LedgerStore
from analyse_account_transactions.app.textutil import months
from analyse_account_transactions.shared.constants import (
    CATEGORIES,
    CREDIT_CATEGORIES,
    DEBIT_CATEGORIES,
    FLOWS,
    MAX_DESCRIPTION,
    MAX_TITLE_WORDS,
    NEEDS,
    NORMALIZERS,
    RELEVANCES,
    UNKNOWN,
)
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Ledger, Row
from analyse_account_transactions.shared.values import format_value, parse_value

TIMESTAMP = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?: ([01]\d|2[0-3]):([0-5]\d))?$")
INJECTION = re.compile(
    r"(?i)ignore (?:all |any )?(?:previous|prior|above) instructions|system prompt|you are (?:an? )?(?:ai|assistant)"
    r"|(?:classify|categori[sz]e|mark) (?:this|me|it) as|disregard (?:the )?rules",
)
MAX_ROWS = 2000
PERIOD = re.compile(r"(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})")
PERIOD_TOLERANCE_DAYS = 7
PERIOD_START_LEN = 10
PERIOD_END_FROM = 12
ALLOWED_FLOWS = {
    "Income": {"Income"},
    "Transfers In": {"Savings"},
    "Transfers Out & Savings": {"Savings", "Expenditure"},
}
ALLOWED_FLOWS.update({c: {"Expenditure"} for c in DEBIT_CATEGORIES if c != "Transfers Out & Savings"})
Report = Callable[[int, str, str], None]


def _account_entry(path: Path, led: Ledger) -> dict[str, Any]:
    iban = led.meta.get("iban", "unknown")
    return {
        "file": path.name,
        "iban-last4": iban[-4:],
        "currency": led.meta.get("currency", "unknown"),
        "account-type": led.meta.get("account-type", "unknown"),
        "rows": len(led.rows),
        "period": led.meta.get("period", "unknown"),
        "opening": led.meta.get("opening-balance", "none"),
        "closing": led.meta.get("closing-balance", "none"),
        "account": f"{led.meta.get('bank', 'unknown')}:{iban}",
    }


def _account_warnings(group: list[dict[str, Any]], key: str) -> list[dict[str, str]]:
    warnings = []
    for prev, nxt in pairwise(group):
        if "none" not in (prev["closing"], nxt["opening"]) and prev["closing"] != nxt["opening"]:
            msg = (
                f"{prev['file']} closes at {prev['closing']} but {nxt['file']} opens at {nxt['opening']}; "
                "a statement is probably missing or overlaps"
            )
            warnings.append({"rule": "continuity", "message": msg})
    dated = [a["period"] for a in group if PERIOD.fullmatch(a["period"])]
    if dated:
        covered = set().union(*(months(p) for p in dated))
        wanted = months(f"{dated[0][:PERIOD_START_LEN]}..{max(p[PERIOD_END_FROM:] for p in dated)}")
        missing = sorted(wanted - covered)
        if missing:
            warnings.append({"rule": "gap", "message": f"account ...{key[-4:]} has no statement for {missing}"})
    return warnings


def check_accounts(store: LedgerStore, paths: list[str]) -> dict[str, Any]:
    accounts: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    ledgers: dict[str, Ledger] = {}
    for p in paths:
        path = store.resolve_tmp(p)
        led = ledger.read(store, path)
        ledgers[path.name] = led
        accounts.append(_account_entry(path, led))
    by_account: dict[str, list[dict[str, Any]]] = {}
    for a in accounts:
        by_account.setdefault(a.pop("account"), []).append(a)
    overlaps: list[dict[str, Any]] = []
    for key, group in by_account.items():
        group.sort(key=lambda a: a["period"])
        warnings += _account_warnings(group, key)
        overlaps += repeated_rows(group, ledgers)
    for o in overlaps:
        msg = (
            f"{o['file']} row {o['row']} repeats {o['other']} row {o['other-row']}; drop one copy with aat-ledger drop"
        )
        warnings.append({"rule": "overlap", "message": msg})
    currencies = sorted({a["currency"] for a in accounts})
    if len(currencies) > 1:
        errors.append({"rule": "currency", "message": f"mixed account currencies {currencies}; analyse one currency"})
    total = sum(a["rows"] for a in accounts)
    if total > MAX_ROWS:
        warnings.append({"rule": "rows", "message": f"{total} rows (> {MAX_ROWS}); confirm or narrow the period"})
    return {
        "ok": not errors,
        "accounts": accounts,
        "rows": total,
        "overlap-rows": overlaps,
        "errors": errors,
        "warnings": warnings,
    }


def repeated_rows(group: list[dict[str, Any]], ledgers: dict[str, Ledger]) -> list[dict[str, Any]]:
    """Rows with the same timestamp, value and description in two files of one account (overlapping exports)."""
    seen: dict[tuple[tuple[str, ...], int], tuple[str, int]] = {}
    found: list[dict[str, Any]] = []
    for a in group:
        counts: dict[tuple[str, ...], int] = {}
        for i, r in enumerate(ledgers[a["file"]].rows, 1):
            key = tuple(r.key())
            n = counts[key] = counts.get(key, 0) + 1
            other = seen.get((key, n))
            if other and other[0] != a["file"]:
                found.append({"file": a["file"], "row": i, "other": other[0], "other-row": other[1]})
            else:
                seen[(key, n)] = (a["file"], i)
    return found


def _date(ts: str) -> date | None:
    m = TIMESTAMP.match(ts)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def check_format(i: int, r: Row, err: Report) -> None:
    if _date(r.timestamp) is None:
        err(i, "format", f"timestamp must be YYYY-MM-DD[ HH:MM]: {r.timestamp!r}")
    if not r.title.strip():
        err(i, "format", "title is empty")
    elif len(r.title.split()) > MAX_TITLE_WORDS:
        err(i, "format", f"title has more than {MAX_TITLE_WORDS} words: {r.title!r}")
    if len(r.description) > MAX_DESCRIPTION:
        err(i, "format", f"description longer than {MAX_DESCRIPTION} characters")


def _allowed_flows(r: Row) -> set[str]:
    fixed = ALLOWED_FLOWS.get(r.category)
    if fixed:
        return fixed
    if r.value == 0:
        return {"Income", "Expenditure"}
    return {"Income"} if r.value > 0 else {"Expenditure"}


def _check_flow(i: int, r: Row, err: Report, warn: Report) -> None:
    zero = r.value == 0
    if r.flow not in _allowed_flows(r):
        err(i, "A10", f"{r.category} with value {format_value(r.value)} cannot have flow {r.flow}")
    if not zero and r.category in CREDIT_CATEGORIES and r.value < 0:
        err(i, "A2", f"credit category {r.category} with a negative value")
    if not zero and r.flow == "Income" and r.value < 0:
        err(i, "A2", "Income flow with a negative value")
    if r.value > 0 and r.flow == "Expenditure":
        warn(i, "refund", f"positive Expenditure row (refund or repayment?) in {r.category}")
    needs_relevance = r.flow == "Expenditure" and r.category != UNKNOWN
    if needs_relevance and r.relevance not in RELEVANCES:
        err(i, "relevance", f"Expenditure row needs relevance {RELEVANCES}: {r.relevance!r}")
    if not needs_relevance and r.relevance:
        err(i, "relevance", f"relevance only applies to Expenditure rows (not Unknown): {r.relevance!r}")


def check_classification(i: int, r: Row, phase: str, err: Report, warn: Report) -> None:
    if phase == "convert":
        if any((r.category, r.flow, r.relevance, r.needs)):
            err(i, "convert", "category, flow, relevance and needs-investigation must be empty after convert")
        return
    if r.category not in CATEGORIES:
        err(i, "A3", f"category outside the fixed list: {r.category!r}")
        return
    if r.needs not in NEEDS:
        err(i, "needs", f"needs-investigation must be one of {NEEDS}: {r.needs!r}")
    if phase == "final" and r.needs == "yes":
        err(i, "final", "row still needs investigation")
    if r.category == UNKNOWN and r.needs != "user":
        err(i, "A4", "Unknown can only be set by the user")
    if r.flow not in FLOWS:
        err(i, "flow", f"flow must be one of {FLOWS}: {r.flow!r}")
        return
    _check_flow(i, r, err, warn)


def check_snapshot(led: Ledger, snapshot: dict[str, Any], err: Report) -> None:
    rows = [r.key() for r in led.rows]
    if len(rows) != len(snapshot["rows"]):
        err(0, "A7", f"row count changed: {len(snapshot['rows'])} -> {len(rows)}")
        return
    total = format_value(sum((r.value for r in led.rows), Decimal(0)))
    if total != snapshot["sum"]:
        err(0, "A7", f"sum changed: {snapshot['sum']} -> {total}")
    for i, (now, before) in enumerate(zip(rows, snapshot["rows"], strict=False), 1):
        if now != before:
            err(i, "A7", f"timestamp/value/description changed: {before} -> {now}")
    for i, r in enumerate(led.rows, 1):
        saved = snapshot["user"].get(str(i))
        if saved is None and r.needs == "user":
            err(i, "user", "marked user without a recorded answer; use aat-ledger apply --source user")
        elif saved is not None and (r.needs != "user" or {k: getattr(r, k) for k in saved} != saved):
            err(i, "user", f"user answer overwritten: expected {saved}")


def near_duplicate_titles(rows: list[Row]) -> list[list[str]]:
    groups: dict[str, set[str]] = {}
    for r in rows:
        groups.setdefault(re.sub(r"[^a-z0-9]", "", r.title.lower()), set()).add(r.title)
    return [sorted(v) for v in groups.values() if len(v) > 1]


def _check_header(led: Ledger, err: Report, warn: Report) -> None:
    for key in ("source", "currency", "normalizer"):
        if not led.meta.get(key) or led.meta[key] == "unknown":
            err(0, "header", f"header field {key!r} is missing")
    normalizer = led.meta.get("normalizer", "")
    if normalizer and not NORMALIZERS.match(normalizer):
        err(0, "header", f"normalizer must be module:<name>, mapping, llm or llm-image: {normalizer!r}")
    if normalizer == "llm-image":
        warn(0, "unverified", "values transcribed from an image cannot be grounded; report them as unverified")


def _check_rows(led: Ledger, phase: str, err: Report, warn: Report) -> None:
    period = PERIOD.fullmatch(led.meta.get("period", ""))
    start, end = (_date(period.group(1)), _date(period.group(2))) if period else (None, None)
    tol = timedelta(days=PERIOD_TOLERANCE_DAYS)
    for i, r in enumerate(led.rows, 1):
        check_format(i, r, err)
        check_classification(i, r, phase, err, warn)
        if INJECTION.search(r.description):
            warn(i, "A1", "description contains text addressed to an AI; treat as data")
        d = _date(r.timestamp)
        if d and start and end and not (start - tol <= d <= end + tol):
            warn(i, "period", f"date {d} outside period {start}..{end}")


def _check_balance(led: Ledger, total: Decimal, err: Report, warn: Report) -> None:
    opening, closing = led.meta.get("opening-balance", "none"), led.meta.get("closing-balance", "none")
    if opening == "none" or closing == "none":
        warn(0, "balance", "no balances in source; reconciliation skipped")
        return
    try:
        expected = parse_value(opening) + total
        if expected != parse_value(closing):
            err(
                0,
                "balance",
                f"opening {opening} + sum {format_value(total)} = {format_value(expected)}, but closing is {closing}",
            )
    except LedgerError as e:
        err(0, "balance", str(e))


def check_file(store: LedgerStore, path: Path, phase: str) -> dict[str, Any]:
    led = ledger.read(store, path)
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    def err(i: int, rule: str, msg: str) -> None:
        errors.append({"row": i, "rule": rule, "message": msg})

    def warn(i: int, rule: str, msg: str) -> None:
        warnings.append({"row": i, "rule": rule, "message": msg})

    _check_header(led, err, warn)
    _check_rows(led, phase, err, warn)
    total = sum((r.value for r in led.rows), Decimal(0))
    _check_balance(led, total, err, warn)
    if phase == "convert":
        if not errors:
            ledger.write_snapshot(store, path, led, {})
    else:
        check_snapshot(led, ledger.load_snapshot(store, path), err)
        by_title: dict[str, set[tuple[str, str, str]]] = {}
        for r in led.rows:
            by_title.setdefault(r.title, set()).add((r.category, r.flow, r.relevance))
        for title, combos in sorted(by_title.items()):
            if len(combos) > 1:
                warn(0, "A6", f"{title!r} has {len(combos)} classifications; confirm per-row exceptions")
    for group in near_duplicate_titles(led.rows):
        warn(0, "titles", f"near-duplicate titles: {group}")
    return {
        "file": path.name,
        "phase": phase,
        "ok": not errors,
        "rows": len(led.rows),
        "sum": format_value(total),
        "errors": errors,
        "warnings": warnings,
    }
