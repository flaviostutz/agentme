#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Exact calculations over one or more classified normalized files (.tmp/<id>/normalized/*.md).

  totals       credits, debits, net balance, totals per category/flow/relevance
  flow         Income = Savings (put aside + kept in accounts) + Expenditures; exit 1 if it does not hold
  relevance    share of Expenditures per relevance class and the top 6 counterparties
  recurrence   Daily/Weekly/Monthly/Quarterly/Yearly/One-off buckets; exit 1 if buckets do not sum to the total
  recurring    recurring charges (stable amount, Weekly..Yearly) with totals and active/stopped status
  insights     small-but-adds-up, large counterparties and hidden spending (--hidden title map)
  query        filter (k=v exact, k~v contains, k=- empty) and group rows
  duplicates   identical rows across files of the same account
  estimate     saving when reducing a title, category or relevance class by a percentage
Every result carries the analysis currency taken from the file headers.
"""

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import ledger
import patterns
from ledger import CATEGORIES, FLOWS, RELEVANCES, LedgerError

ZERO = Decimal(0)
TENTH = Decimal("0.1")
DAYS_PER_MONTH = Decimal("30.4375")
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
GROUP_KEYS = ["category", "flow", "relevance", "title", "weekday", "month", "hour", "bucket"]
FILTER_KEYS = ["category", "flow", "relevance", "needs", "title", "description", "weekday", "month", "hour", "bucket",
               "file"]


class Tagged:
    """A row plus the file it came from."""

    def __init__(self, file: str, row):
        self.file, self.row = file, row

    def __getattr__(self, name):
        return getattr(self.row, name)


def load(paths: list, cwd: Path) -> tuple:
    files, rows = [], []
    for p in paths:
        path = ledger.resolve_tmp(p, cwd)
        led = ledger.read(path)
        files.append({"file": path.name, "meta": led.meta, "rows": len(led.rows)})
        rows.extend(Tagged(path.name, r) for r in led.rows)
    return files, rows


def share(part: Decimal, whole: Decimal) -> str:
    return str((part * 100 / whole).quantize(TENTH, ROUND_HALF_UP)) if whole else "0.0"


def months_covered(files: list, rows: list) -> Decimal:
    starts, ends = [], []
    for f in files:
        start, _, end = f["meta"].get("period", "").partition("..")
        if len(start) == 10 and len(end) == 10:
            starts.append(start)
            ends.append(end)
    if len(starts) != len(files):
        dates = sorted(r.timestamp[:10] for r in rows)
        starts, ends = dates[:1], dates[-1:]
    if not starts:
        return Decimal(1)
    days = (patterns.to_date(max(ends)) - patterns.to_date(min(starts))).days + 1
    return max(Decimal(days) / DAYS_PER_MONTH, Decimal(1))


def period_ends(files: list, rows: list) -> dict:
    """{file: coverage end of its account (latest end across files of the same IBAN), "": latest end};
    a file without a period falls back to its last row date."""
    last = {}
    for r in rows:
        last[r.file] = max(last.get(r.file, ""), r.timestamp[:10])
    account = {f["file"]: f["meta"].get("iban", "") for f in files}
    account = {k: (k if v in ("", "unknown", "none") else v) for k, v in account.items()}
    account_end = {}
    for f in files:
        end = f["meta"].get("period", "").partition("..")[2]
        end = end if len(end) == 10 else last.get(f["file"], "")
        if end:
            key = account[f["file"]]
            account_end[key] = max(account_end.get(key, end), end)
    if not account_end:
        raise LedgerError("no rows and no period end")
    ends = {k: patterns.to_date(account_end[v]) for k, v in account.items() if v in account_end}
    ends[""] = max(ends.values())
    return ends


def totals(rows: list) -> dict:
    groups = {}
    for r in rows:
        groups.setdefault((r.category, r.flow, r.relevance), []).append(r.value)
    order = {c: i for i, c in enumerate(CATEGORIES)}
    per = [{"category": c, "flow": f, "relevance": rel, "rows": len(v), "total": sum(v, ZERO)}
           for (c, f, rel), v in sorted(groups.items(), key=lambda kv: (order.get(kv[0][0], 99), kv[0][1:]))]
    credits = sum((r.value for r in rows if r.value > 0), ZERO)
    debits = sum((r.value for r in rows if r.value < 0), ZERO)
    return {"rows": len(rows), "credits": credits, "debits": debits, "net_balance": credits + debits,
            "per_category": per}


def flow(rows: list) -> dict:
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
        "ok": ok, "rows": len(rows), "rows_per_flow": counts, "unassigned_rows": unassigned,
        "income": income, "expenditures": expenditures,
        "refunds": {"rows": sum(r.value > 0 for r in spend), "total": sum((r.value for r in spend if r.value > 0), ZERO)},
        "savings": savings, "put_aside": put_aside, "kept_in_accounts": kept,
        "savings_out": -sum((r.value for r in savings_rows if r.value < 0), ZERO),
        "savings_in": sum((r.value for r in savings_rows if r.value > 0), ZERO),
        "check": f"{income} = {savings} + {expenditures}",
    }


def relevance(rows: list) -> dict:
    spend = [r for r in rows if r.flow == "Expenditure"]
    total = -sum((r.value for r in spend), ZERO)
    classes = []
    for name in RELEVANCES + ["Unclassified"]:
        members = [r for r in spend if (r.relevance or "Unclassified") == name]
        amount = -sum((r.value for r in members), ZERO)
        per_title = {}
        for r in members:
            per_title.setdefault(r.title, []).append(r.value)
        top = sorted(({"title": t, "rows": len(v), "total": -sum(v, ZERO)} for t, v in per_title.items()),
                     key=lambda x: (-x["total"], x["title"]))[:6]
        classes.append({"relevance": name, "rows": len(members), "total": amount, "share": share(amount, total),
                        "top": top})
    shown = sum(Decimal(c["share"]) for c in classes)
    return {"expenditures": total, "classes": classes, "shares_display_sum": str(shown)}


def key_of(r, key: str, buckets: dict) -> str:
    ts = r.timestamp
    if key == "weekday":
        return WEEKDAYS[patterns.to_date(ts).weekday()]
    if key == "month":
        return ts[:7]
    if key == "hour":
        return ts[11:13] if len(ts) > 10 else "unknown"
    if key == "bucket":
        return buckets[r.title][0]
    return getattr(r, key) or "-"


def query(rows: list, filters: list, group_by, assign: dict) -> dict:
    buckets = patterns.classify_titles(rows, assign)
    selected = rows
    for f in filters:
        op = "~" if "~" in f and ("=" not in f or f.index("~") < f.index("=")) else "="
        key, _, value = f.partition(op)
        if key not in FILTER_KEYS or not value:
            raise LedgerError(f"invalid filter {f!r}; keys: {FILTER_KEYS}")
        v = value.lower()
        selected = [r for r in selected if (v in key_of(r, key, buckets).lower() if op == "~"
                                            else key_of(r, key, buckets).lower() == v)]
    result = {"rows": len(selected), "total": sum((r.value for r in selected), ZERO)}
    if not group_by:
        result["items"] = [{"file": r.file, "timestamp": r.timestamp, "title": r.title, "value": r.value,
                            "category": r.category} for r in selected[:200]]
        return result
    groups = {}
    for r in selected:
        groups.setdefault(key_of(r, group_by, buckets), []).append(r.value)
    order = WEEKDAYS if group_by == "weekday" else sorted(groups)
    result["groups"] = [{"key": k, "rows": len(groups[k]), "total": sum(groups[k], ZERO),
                         "share_of_rows": share(Decimal(len(groups[k])), Decimal(len(selected)))}
                        for k in order if k in groups]
    return result


def duplicates(files: list, rows: list) -> dict:
    iban = {f["file"]: f["meta"].get("iban", "unknown") for f in files}
    index = {}
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


def estimate(files: list, rows: list, target: str, pct: Decimal) -> dict:
    key, _, value = target.partition("=")
    if key not in ("title", "category", "relevance") or not value:
        raise LedgerError("--target must be title=..., category=... or relevance=...")
    if not ZERO < pct <= 100:
        raise LedgerError("--reduce-pct must be above 0 and at most 100")
    matched = [r for r in rows if r.flow == "Expenditure" and getattr(r, key).lower() == value.lower()]
    current = -sum((r.value for r in matched), ZERO)
    months = months_covered(files, rows)
    saving = (current * pct / 100).quantize(ledger.CENT, ROUND_HALF_UP)
    return {"target": target, "rows": len(matched), "current": current, "reduce_pct": pct, "saving": saving,
            "months": months.quantize(TENTH, ROUND_HALF_UP),
            "saving_per_month": (saving / months).quantize(ledger.CENT, ROUND_HALF_UP),
            "assumption": f"reduce {value} by {pct}%"}


def encode(obj):
    if isinstance(obj, Decimal):
        return str(obj.quantize(ledger.CENT, ROUND_HALF_UP))
    raise TypeError(type(obj).__name__)


def read_assign(text) -> dict:
    if not text:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise LedgerError(f"--assign must be JSON like {{\"Title\": \"Yearly\"}}: {err}") from err
    if not isinstance(data, dict):
        raise LedgerError("--assign must be a JSON object")
    return data


def read_hidden(path, cwd: Path) -> dict:
    if not path:
        return {}
    try:
        return json.loads(ledger.resolve_tmp(path, cwd).read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise LedgerError(f"--hidden is not valid JSON: {err}") from err


def read_thresholds(items: list) -> dict:
    result = {}
    for item in items:
        key, _, value = item.partition("=")
        result[key] = ledger.parse_decimal(value)
    return result


def currency_of(files: list) -> str:
    found = sorted({f["meta"].get("currency", "unknown") for f in files})
    return found[0] if len(found) == 1 else "mixed: " + ", ".join(found)


def run(args) -> tuple:
    files, rows = load(args.files, Path.cwd())
    result, ok = compute(args, files, rows)
    return {"currency": currency_of(files), **result}, ok


def compute(args, files: list, rows: list) -> tuple:
    assign = read_assign(args.assign)
    if args.cmd == "totals":
        return totals(rows), True
    if args.cmd == "flow":
        result = flow(rows)
        return result, result["ok"]
    if args.cmd == "relevance":
        return relevance(rows), True
    if args.cmd == "recurrence":
        result = patterns.recurrence(rows, assign)
        return result, result["ok"]
    if args.cmd == "recurring":
        return patterns.recurring(rows, assign, period_ends(files, rows)), True
    if args.cmd == "insights":
        return patterns.insights(rows, read_hidden(args.hidden, Path.cwd()), read_thresholds(args.threshold)), True
    if args.cmd == "query":
        return query(rows, args.filter, args.group_by, assign), True
    if args.cmd == "duplicates":
        return duplicates(files, rows), True
    return estimate(files, rows, args.target, ledger.parse_decimal(args.reduce_pct)), True


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cmd", choices=["totals", "flow", "relevance", "recurrence", "recurring", "insights",
                                        "query", "duplicates", "estimate"])
    parser.add_argument("files", nargs="+", help="normalized files inside .tmp/")
    parser.add_argument("--assign", help='JSON {"Title": "Quarterly"|"Yearly"} for one-off titles (inferred)')
    parser.add_argument("--hidden", help='insights: JSON file {"Title": "cash"|"card"|"provider"|"fees"}')
    parser.add_argument("--threshold", action="append", default=[], metavar="KEY=VALUE",
                        help=f"insights: override {', '.join(patterns.THRESHOLDS)}")
    parser.add_argument("--filter", action="append", default=[], help="query filter k=v or k~v; k=- matches empty fields (repeatable)")
    parser.add_argument("--group-by", choices=GROUP_KEYS, help="query grouping key")
    parser.add_argument("--target", help="estimate target: title=..., category=... or relevance=...")
    parser.add_argument("--reduce-pct", default="0", help="estimate reduction percentage (0-100]")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON (default output)")
    args = parser.parse_args(argv)
    if args.cmd == "estimate" and not args.target:
        parser.error("estimate needs --target and --reduce-pct")
    try:
        result, ok = run(args)
    except (LedgerError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, default=encode))
    if not ok:
        print(f"error: {args.cmd} invariant failed", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
