"""Exact calculations over one or more classified normalized files (.tmp/<id>/normalized/*.md).

totals       credits, debits, net balance, totals per category/flow/relevance
flow         Income = Savings (put aside + kept in accounts) + Expenditures
relevance    share of Expenditures per relevance class and the top 6 counterparties
recurrence   Daily/Weekly/Monthly/Quarterly/Yearly/One-off buckets
recurring    recurring charges (stable amount, Weekly..Yearly) with totals and active/stopped status
insights     small-but-adds-up, large counterparties and hidden spending (hidden title map)
query        filter (k=v exact, k~v contains, k=- empty) and group rows
duplicates   identical rows across files of the same account
estimate     saving when reducing a title, category or relevance class by a percentage
"""

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from analyse_account_transactions.app import ledger, patterns
from analyse_account_transactions.app.ports import LedgerStore
from analyse_account_transactions.shared.constants import CATEGORIES, CENT, FLOWS, RELEVANCES
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Row
from analyse_account_transactions.shared.values import parse_decimal

ZERO = Decimal(0)
TENTH = Decimal("0.1")
PERCENT = 100
DAYS_PER_MONTH = Decimal("30.4375")
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
GROUP_KEYS = ["category", "flow", "relevance", "title", "weekday", "month", "hour", "bucket"]
FILTER_KEYS = [
    "category",
    "flow",
    "relevance",
    "needs",
    "title",
    "description",
    "weekday",
    "month",
    "hour",
    "bucket",
    "file",
]
COMMANDS = ["totals", "flow", "relevance", "recurrence", "recurring", "insights", "query", "duplicates", "estimate"]
DATE_LEN = 10
HOUR_FROM = 11
MONTH_LEN = 7
QUERY_ITEMS = 200
UNORDERED = 99


class Tagged:
    """A row plus the file it came from."""

    def __init__(self, file: str, row: Row) -> None:
        self.file, self.row = file, row

    def __getattr__(self, name: str) -> Any:
        return getattr(self.row, name)


FileInfo = dict[str, Any]


@dataclass
class Request:
    cmd: str
    files: list[str]
    assign: str | None = None
    hidden: str | None = None
    threshold: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    group_by: str | None = None
    target: str | None = None
    reduce_pct: str = "0"


def load(store: LedgerStore, paths: list[str]) -> tuple[list[FileInfo], list[Tagged]]:
    files: list[FileInfo] = []
    rows: list[Tagged] = []
    for p in paths:
        path = store.resolve_tmp(p)
        led = ledger.read(store, path)
        files.append({"file": path.name, "meta": led.meta, "rows": len(led.rows)})
        rows.extend(Tagged(path.name, r) for r in led.rows)
    return files, rows


def share(part: Decimal, whole: Decimal) -> str:
    return str((part * PERCENT / whole).quantize(TENTH, ROUND_HALF_UP)) if whole else "0.0"


def months_covered(files: list[FileInfo], rows: list[Tagged]) -> Decimal:
    starts: list[str] = []
    ends: list[str] = []
    for f in files:
        start, _, end = f["meta"].get("period", "").partition("..")
        if len(start) == DATE_LEN and len(end) == DATE_LEN:
            starts.append(start)
            ends.append(end)
    if len(starts) != len(files):
        dates = sorted(r.timestamp[:DATE_LEN] for r in rows)
        starts, ends = dates[:1], dates[-1:]
    if not starts:
        return Decimal(1)
    days = (patterns.to_date(max(ends)) - patterns.to_date(min(starts))).days + 1
    return max(Decimal(days) / DAYS_PER_MONTH, Decimal(1))


def period_ends(files: list[FileInfo], rows: list[Tagged]) -> dict[str, date]:
    """{file: coverage end of its account (latest end across files of the same IBAN), "": latest end}.

    A file without a period falls back to its last row date.
    """
    last: dict[str, str] = {}
    for r in rows:
        last[r.file] = max(last.get(r.file, ""), r.timestamp[:DATE_LEN])
    ibans = {f["file"]: f["meta"].get("iban", "") for f in files}
    account = {k: (k if v in ("", "unknown", "none") else v) for k, v in ibans.items()}
    account_end: dict[str, str] = {}
    for f in files:
        end = f["meta"].get("period", "").partition("..")[2]
        end = end if len(end) == DATE_LEN else last.get(f["file"], "")
        if end:
            key = account[f["file"]]
            account_end[key] = max(account_end.get(key, end), end)
    if not account_end:
        msg = "no rows and no period end"
        raise LedgerError(msg)
    ends = {k: patterns.to_date(account_end[v]) for k, v in account.items() if v in account_end}
    ends[""] = max(ends.values())
    return ends


def totals(rows: list[Tagged]) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[Decimal]] = {}
    for r in rows:
        groups.setdefault((r.category, r.flow, r.relevance), []).append(r.value)
    order = {c: i for i, c in enumerate(CATEGORIES)}
    per = [
        {"category": c, "flow": f, "relevance": rel, "rows": len(v), "total": sum(v, ZERO)}
        for (c, f, rel), v in sorted(groups.items(), key=lambda kv: (order.get(kv[0][0], UNORDERED), kv[0][1:]))
    ]
    incoming = sum((r.value for r in rows if r.value > 0), ZERO)
    debits = sum((r.value for r in rows if r.value < 0), ZERO)
    return {
        "rows": len(rows),
        "credits": incoming,
        "debits": debits,
        "net_balance": incoming + debits,
        "per_category": per,
    }


def flow(rows: list[Tagged]) -> dict[str, Any]:
    by_flow = {f: [r for r in rows if r.flow == f] for f in FLOWS}
    unassigned = [i for i, r in enumerate(rows, 1) if r.flow not in FLOWS]
    income = sum((r.value for r in by_flow["Income"]), ZERO)
    spend = by_flow["Expenditure"]
    expenditures = -sum((r.value for r in spend), ZERO)
    savings_rows = by_flow["Savings"]
    put_aside = -sum((r.value for r in savings_rows), ZERO)
    kept = sum((r.value for r in rows), ZERO)
    savings = put_aside + kept
    counts = {f: len(v) for f, v in by_flow.items()}
    ok = not unassigned and sum(counts.values()) == len(rows) and income == savings + expenditures
    return {
        "ok": ok,
        "rows": len(rows),
        "rows_per_flow": counts,
        "unassigned_rows": unassigned,
        "income": income,
        "expenditures": expenditures,
        "refunds": {
            "rows": sum(r.value > 0 for r in spend),
            "total": sum((r.value for r in spend if r.value > 0), ZERO),
        },
        "savings": savings,
        "put_aside": put_aside,
        "kept_in_accounts": kept,
        "savings_out": -sum((r.value for r in savings_rows if r.value < 0), ZERO),
        "savings_in": sum((r.value for r in savings_rows if r.value > 0), ZERO),
        "check": f"{income} = {savings} + {expenditures}",
    }


def relevance(rows: list[Tagged]) -> dict[str, Any]:
    spend = [r for r in rows if r.flow == "Expenditure"]
    total = -sum((r.value for r in spend), ZERO)
    classes: list[dict[str, Any]] = []
    for name in [*RELEVANCES, "Unclassified"]:
        members = [r for r in spend if (r.relevance or "Unclassified") == name]
        amount = -sum((r.value for r in members), ZERO)
        per_title: dict[str, list[Decimal]] = {}
        for r in members:
            per_title.setdefault(r.title, []).append(r.value)
        titles: list[dict[str, Any]] = [
            {"title": t, "rows": len(v), "total": -sum(v, ZERO)} for t, v in per_title.items()
        ]
        top = sorted(titles, key=lambda x: (-x["total"], x["title"]))[:6]
        classes.append(
            {"relevance": name, "rows": len(members), "total": amount, "share": share(amount, total), "top": top},
        )
    shown = sum(Decimal(c["share"]) for c in classes)
    return {"expenditures": total, "classes": classes, "shares_display_sum": str(shown)}


def key_of(r: Tagged, key: str, buckets: dict[str, tuple[str, Decimal | None, bool]]) -> str:
    ts = r.timestamp
    if key == "weekday":
        return WEEKDAYS[patterns.to_date(ts).weekday()]
    if key == "month":
        return ts[:MONTH_LEN]
    if key == "hour":
        return ts[HOUR_FROM : HOUR_FROM + 2] if len(ts) > DATE_LEN else "unknown"
    if key == "bucket":
        return buckets[r.title][0]
    return getattr(r, key) or "-"


def _select(
    rows: list[Tagged], filters: list[str], buckets: dict[str, tuple[str, Decimal | None, bool]]
) -> list[Tagged]:
    selected = rows
    for f in filters:
        op = "~" if "~" in f and ("=" not in f or f.index("~") < f.index("=")) else "="
        key, _, value = f.partition(op)
        if key not in FILTER_KEYS or not value:
            msg = f"invalid filter {f!r}; keys: {FILTER_KEYS}"
            raise LedgerError(msg)
        v = value.lower()
        selected = [
            r
            for r in selected
            if (v in key_of(r, key, buckets).lower() if op == "~" else key_of(r, key, buckets).lower() == v)
        ]
    return selected


def query(rows: list[Tagged], filters: list[str], group_by: str | None, assign: dict[str, str]) -> dict[str, Any]:
    buckets = patterns.classify_titles(rows, assign)
    selected = _select(rows, filters, buckets)
    result: dict[str, Any] = {"rows": len(selected), "total": sum((r.value for r in selected), ZERO)}
    if not group_by:
        result["items"] = [
            {"file": r.file, "timestamp": r.timestamp, "title": r.title, "value": r.value, "category": r.category}
            for r in selected[:QUERY_ITEMS]
        ]
        return result
    groups: dict[str, list[Decimal]] = {}
    for r in selected:
        groups.setdefault(key_of(r, group_by, buckets), []).append(r.value)
    order = WEEKDAYS if group_by == "weekday" else sorted(groups)
    result["groups"] = [
        {
            "key": k,
            "rows": len(groups[k]),
            "total": sum(groups[k], ZERO),
            "share_of_rows": share(Decimal(len(groups[k])), Decimal(len(selected))),
        }
        for k in order
        if k in groups
    ]
    return result


def duplicates(files: list[FileInfo], rows: list[Tagged]) -> dict[str, Any]:
    iban = {f["file"]: f["meta"].get("iban", "unknown") for f in files}
    index: dict[tuple[str, tuple[str, ...]], list[dict[str, Any]]] = {}
    for f in files:
        n = 0
        for r in rows:
            if r.file == f["file"]:
                n += 1
                index.setdefault((iban[r.file], tuple(r.key())), []).append({"file": r.file, "row": n})
    found = []
    for (acc, key), hits in index.items():
        if acc != "unknown" and len({h["file"] for h in hits}) > 1:
            found.append({"timestamp": key[0], "value": key[1], "description": key[2], "rows": hits})
    return {"duplicates": found}


def estimate(files: list[FileInfo], rows: list[Tagged], target: str, pct: Decimal) -> dict[str, Any]:
    key, _, value = target.partition("=")
    if key not in ("title", "category", "relevance") or not value:
        msg = "--target must be title=..., category=... or relevance=..."
        raise LedgerError(msg)
    if not ZERO < pct <= PERCENT:
        msg = "--reduce-pct must be above 0 and at most 100"
        raise LedgerError(msg)
    matched = [r for r in rows if r.flow == "Expenditure" and getattr(r, key).lower() == value.lower()]
    current = -sum((r.value for r in matched), ZERO)
    months = months_covered(files, rows)
    saving = (current * pct / PERCENT).quantize(CENT, ROUND_HALF_UP)
    return {
        "target": target,
        "rows": len(matched),
        "current": current,
        "reduce_pct": pct,
        "saving": saving,
        "months": months.quantize(TENTH, ROUND_HALF_UP),
        "saving_per_month": (saving / months).quantize(CENT, ROUND_HALF_UP),
        "assumption": f"reduce {value} by {pct}%",
    }


def encode(obj: object) -> str:
    """json.dumps default: Decimals are printed with two decimals."""
    if isinstance(obj, Decimal):
        return str(obj.quantize(CENT, ROUND_HALF_UP))
    raise TypeError(type(obj).__name__)


def read_assign(text: str | None) -> dict[str, str]:
    if not text:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        msg = f'--assign must be JSON like {{"Title": "Yearly"}}: {err}'
        raise LedgerError(msg) from err
    if not isinstance(data, dict):
        msg = "--assign must be a JSON object"
        raise LedgerError(msg)
    return data


def read_hidden(store: LedgerStore, path: str | None) -> dict[str, str]:
    if not path:
        return {}
    try:
        return json.loads(store.read_text(store.resolve_tmp(path)))
    except json.JSONDecodeError as err:
        msg = f"--hidden is not valid JSON: {err}"
        raise LedgerError(msg) from err


def read_thresholds(items: list[str]) -> dict[str, Decimal]:
    result = {}
    for item in items:
        key, _, value = item.partition("=")
        result[key] = parse_decimal(value)
    return result


def currency_of(files: list[FileInfo]) -> str:
    found = sorted({f["meta"].get("currency", "unknown") for f in files})
    return found[0] if len(found) == 1 else "mixed: " + ", ".join(found)


def run(store: LedgerStore, request: Request) -> tuple[dict[str, Any], bool]:
    """The result of the command (with the analysis currency) and whether its invariant holds."""
    files, rows = load(store, request.files)
    result, ok = compute(store, request, files, rows)
    return {"currency": currency_of(files), **result}, ok


def compute(  # noqa: PLR0911 - one return per command
    store: LedgerStore,
    request: Request,
    files: list[FileInfo],
    rows: list[Tagged],
) -> tuple[dict[str, Any], bool]:
    assign = read_assign(request.assign)
    cmd = request.cmd
    if cmd == "totals":
        return totals(rows), True
    if cmd == "flow":
        result = flow(rows)
        return result, result["ok"]
    if cmd == "relevance":
        return relevance(rows), True
    if cmd == "recurrence":
        result = patterns.recurrence(rows, assign)
        return result, result["ok"]
    if cmd == "recurring":
        return patterns.recurring(rows, assign, period_ends(files, rows)), True
    if cmd == "insights":
        return patterns.insights(rows, read_hidden(store, request.hidden), read_thresholds(request.threshold)), True
    if cmd == "query":
        return query(rows, request.filters, request.group_by, assign), True
    if cmd == "duplicates":
        return duplicates(files, rows), True
    return estimate(files, rows, request.target or "", parse_decimal(request.reduce_pct)), True
