#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Read, write and classify normalized transaction files (.tmp/<id>/normalized/<name>-<ext>.md).

Subcommands:
  apply  write category, flow, relevance and needs-investigation from a JSON plan; never touches values
  drop   remove confirmed duplicate rows and update the snapshot
  trim   drop rows outside the analysis period and move the balances so they still reconcile
Values, timestamps and descriptions are never changed by this script.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

CREDIT_CATEGORIES = ["Income", "Transfers In"]
DEBIT_CATEGORIES = [
    "Housing & Utilities", "Groceries & Household", "Transport", "Health & Insurance", "Eating Out",
    "Leisure, Shopping & Gifts", "Obligations & Family", "Transfers Out & Savings",
]
UNKNOWN = "Unknown"
CATEGORIES = CREDIT_CATEGORIES + DEBIT_CATEGORIES + [UNKNOWN]
FLOWS = ["Income", "Savings", "Expenditure"]
RELEVANCES = ["Essential", "Important", "Discretionary"]
NEEDS = ["yes", "no", "user"]
COLUMNS = ["timestamp", "title", "value", "description", "category", "flow", "relevance", "needs-investigation"]
CLASS_FIELDS = ["category", "flow", "relevance"]
META_KEYS = ["source", "normalizer", "bank", "account-type", "account-holder", "iban", "currency", "period",
             "opening-balance", "closing-balance"]
NORMALIZERS = re.compile(r"^(?:module:[a-z0-9_]+|mapping|llm|llm-image)$")
MAX_TITLE_WORDS = 4
MAX_DESCRIPTION = 399
CENT = Decimal("0.01")
_META_RE = re.compile(r"^([a-z][a-z-]*): ?(.*)$")
_PIPE_SPLIT = re.compile(r"(?<!\\)\|")


class LedgerError(ValueError):
    """Invalid input: path, file layout or plan."""


@dataclass
class Row:
    timestamp: str
    title: str
    value: Decimal
    description: str
    category: str = ""
    flow: str = ""
    relevance: str = ""
    needs: str = ""

    @property
    def date(self) -> str:
        return self.timestamp[:10]

    def key(self) -> list:
        return [self.timestamp, format_value(self.value), self.description]


@dataclass
class Ledger:
    meta: dict
    rows: list


def format_value(value: Decimal) -> str:
    q = value.quantize(CENT)
    return f"+{q}" if q >= 0 else str(q)


def parse_value(text: str) -> Decimal:
    if not re.fullmatch(r"[+-]\d+\.\d{2}", text):
        raise LedgerError(f"value must be signed with 2 decimals (e.g. -12.34): {text!r}")
    return Decimal(text)


def parse_decimal(text: str) -> Decimal:
    try:
        return Decimal(text)
    except InvalidOperation as err:
        raise LedgerError(f"not a number: {text!r}") from err


def escape_cell(text: str) -> str:
    text = re.sub(r"\s+", " ", text.replace("\\|", "|")).strip()
    return text.replace("|", "\\|")


def clip_description(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= MAX_DESCRIPTION else text[:MAX_DESCRIPTION - 3].rstrip() + "..."


def resolve_tmp(path: str, cwd: Path, must_exist: bool = True) -> Path:
    root = (cwd / ".tmp").resolve()
    resolved = (cwd / path).resolve()
    if root not in resolved.parents:
        raise LedgerError(f"path must be inside {root}: {resolved}")
    if must_exist and not resolved.is_file():
        raise LedgerError(f"file does not exist: {resolved}")
    return resolved


def snapshot_path(path: Path) -> Path:
    return path.with_name(path.stem + ".snapshot.json")


def split_cells(line: str) -> list:
    body = line.strip()
    if not (body.startswith("|") and body.endswith("|")) or body.endswith("\\|"):
        raise LedgerError("table row must start and end with '|'")
    return [c.strip().replace("\\|", "|") for c in _PIPE_SPLIT.split(body[1:-1])]


def parse_text(text: str) -> Ledger:
    meta, rows, in_table = {}, [], False
    for n, line in enumerate(text.splitlines(), 1):
        if not in_table:
            m = _META_RE.match(line)
            if m and m.group(1) in META_KEYS:
                meta[m.group(1)] = m.group(2).strip()
            elif line.startswith("| timestamp"):
                if split_cells(line) != COLUMNS:
                    raise LedgerError(f"line {n}: header must be: {' | '.join(COLUMNS)}")
                in_table = True
            continue
        if not line.strip():
            break
        if re.fullmatch(r"\|(\s*-+\s*\|)+", line.strip()):
            continue
        try:
            cells = split_cells(line)
        except LedgerError as err:
            raise LedgerError(f"line {n}: {err}") from err
        if len(cells) != len(COLUMNS):
            raise LedgerError(f"line {n}: expected {len(COLUMNS)} columns, found {len(cells)} (A9)")
        try:
            value = parse_value(cells[2])
        except LedgerError as err:
            raise LedgerError(f"line {n}: {err}") from err
        rows.append(Row(cells[0], cells[1], value, cells[3], *cells[4:]))
    if not in_table:
        raise LedgerError("no transaction table found (header '| timestamp | title | ...')")
    return Ledger(meta, rows)


def read(path: Path) -> Ledger:
    return parse_text(path.read_text(encoding="utf-8"))


def render(ledger: Ledger, name: str) -> str:
    lines = [f"# Transactions: {name}", ""]
    lines += [f"{k}: {ledger.meta[k]}" for k in META_KEYS if k in ledger.meta]
    lines += ["", "| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for r in ledger.rows:
        cells = [r.timestamp, r.title, format_value(r.value), r.description, r.category, r.flow, r.relevance, r.needs]
        lines.append("| " + " | ".join(escape_cell(c) for c in cells) + " |")
    return "\n".join(lines) + "\n"


def write(path: Path, ledger: Ledger) -> None:
    path.write_text(render(ledger, path.stem), encoding="utf-8")


def load_snapshot(path: Path) -> dict:
    snap = snapshot_path(path)
    if not snap.is_file():
        raise LedgerError(f"snapshot missing, run validate.py {path.name} --phase convert first: {snap.name}")
    return json.loads(snap.read_text(encoding="utf-8"))


def write_snapshot(path: Path, ledger: Ledger, user: dict) -> None:
    data = {
        "rows": [r.key() for r in ledger.rows],
        "sum": format_value(sum((r.value for r in ledger.rows), Decimal(0))),
        "user": user,
    }
    snapshot_path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def _check_entry(where: str, entry: dict) -> dict:
    allowed = {"category": CATEGORIES, "flow": FLOWS, "relevance": RELEVANCES + [""], "needs": ["yes", "no"]}
    unknown = set(entry) - set(allowed) - {"title"}
    if unknown:
        raise LedgerError(f"{where}: unknown keys {sorted(unknown)}")
    for key, options in allowed.items():
        if key in entry and entry[key] not in options:
            raise LedgerError(f"{where}: invalid {key} {entry[key]!r}")
    if "title" in entry and not str(entry["title"]).strip():
        raise LedgerError(f"{where}: empty title")
    return entry


def plan_changes(ledger: Ledger, plan: dict, source: str) -> tuple:
    """Return (changes, protected_rows); raises LedgerError for invalid plans."""
    rename = plan.get("rename", {})
    mapping = {t: _check_entry(f"map[{t!r}]", e) for t, e in plan.get("map", {}).items()}
    exceptions = {}
    for num, entry in plan.get("rows", {}).items():
        if not str(num).isdigit() or not 1 <= int(num) <= len(ledger.rows):
            raise LedgerError(f"rows: row {num!r} does not exist (1..{len(ledger.rows)})")
        exceptions[int(num)] = _check_entry(f"rows[{num}]", entry)
    changes, protected = [], []
    for i, row in enumerate(ledger.rows, 1):
        title = rename.get(row.title, row.title)
        entry = {**mapping.get(title, {}), **exceptions.get(i, {})}
        if title != row.title:
            entry.setdefault("title", title)
        if not entry:
            continue
        if row.needs == "user" and source == "auto" and set(entry) - {"title"}:
            if i in exceptions:
                raise LedgerError(f"rows[{i}]: row was answered by the user and cannot be changed automatically")
            protected.append(i)
            entry = {k: v for k, v in entry.items() if k == "title"}
        if source == "user":
            entry["needs"] = "user"
        elif not row.needs and set(entry) - {"title"}:
            entry.setdefault("needs", "no")
        for key, new in entry.items():
            old = getattr(row, key)
            if old != new:
                changes.append({"row": i, "title": row.title, "field": key, "old": old, "new": new})
    return changes, protected


def apply_changes(ledger: Ledger, changes: list) -> None:
    for c in changes:
        setattr(ledger.rows[c["row"] - 1], c["field"], c["new"])


def cmd_apply(args, cwd: Path) -> dict:
    path = resolve_tmp(args.file, cwd)
    ledger = read(path)
    raw = sys.stdin.read() if args.input == "-" else resolve_tmp(args.input, cwd).read_text(encoding="utf-8")
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as err:
        raise LedgerError(f"plan is not valid JSON: {err}") from err
    if not isinstance(plan, dict) or set(plan) - {"rename", "map", "rows"}:
        raise LedgerError("plan must be an object with only 'rename', 'map' and 'rows'")
    snapshot = load_snapshot(path)
    changes, protected = plan_changes(ledger, plan, args.source)
    result = {"file": path.name, "dry_run": args.dry_run, "changes": changes, "protected_rows": protected}
    if args.dry_run:
        return result
    apply_changes(ledger, changes)
    if args.source == "user":
        for i in sorted({c["row"] for c in changes}):
            row = ledger.rows[i - 1]
            snapshot["user"][str(i)] = {k: getattr(row, k) for k in CLASS_FIELDS}
    write(path, ledger)
    write_snapshot(path, ledger, snapshot["user"])
    return result


def cmd_drop(args, cwd: Path) -> dict:
    path = resolve_tmp(args.file, cwd)
    ledger = read(path)
    snapshot = load_snapshot(path)
    try:
        nums = sorted({int(n) for n in args.rows.split(",")})
    except ValueError as err:
        raise LedgerError(f"--rows must be comma-separated row numbers: {args.rows!r}") from err
    if not nums or nums[0] < 1 or nums[-1] > len(ledger.rows):
        raise LedgerError(f"rows out of range 1..{len(ledger.rows)}: {args.rows}")
    dropped = [ledger.rows[n - 1].key() for n in nums]
    keep = [i for i in range(1, len(ledger.rows) + 1) if i not in nums]
    user = {str(new): snapshot["user"][str(old)] for new, old in enumerate(keep, 1) if str(old) in snapshot["user"]}
    ledger.rows = [ledger.rows[i - 1] for i in keep]
    write(path, ledger)
    write_snapshot(path, ledger, user)
    return {"file": path.name, "dropped": dropped, "rows": len(ledger.rows)}


def trim(led: Ledger, start: str, end: str) -> int:
    """Drop rows outside start..end (YYYY-MM-DD) and move known balances so they still reconcile."""
    before = [r for r in led.rows if r.date < start]
    after = [r for r in led.rows if r.date > end]
    for key, dropped, sign in (("opening-balance", before, 1), ("closing-balance", after, -1)):
        if dropped and led.meta.get(key, "none") != "none":
            moved = parse_value(led.meta[key]) + sign * sum((r.value for r in dropped), Decimal(0))
            led.meta[key] = format_value(moved)
    led.rows = [r for r in led.rows if start <= r.date <= end]
    old_start, _, old_end = led.meta.get("period", f"{start}..{end}").partition("..")
    iso = re.compile(r"\d{4}-\d{2}-\d{2}")
    if not (iso.fullmatch(old_start) and iso.fullmatch(old_end)):
        old_start, old_end = start, end
    led.meta["period"] = f"{max(start, old_start)}..{min(end, old_end)}"
    return len(before) + len(after)


def cmd_trim(args, cwd: Path) -> dict:
    for d in (args.start, args.end):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            raise LedgerError(f"--from/--until must be YYYY-MM-DD: {d!r}")
    if args.start > args.end:
        raise LedgerError("--from is after --until")
    path = resolve_tmp(args.file, cwd)
    led = read(path)
    if snapshot_path(path).exists():
        raise LedgerError("trim before the snapshot (validate.py --phase convert), not after")
    dropped = trim(led, args.start, args.end)
    write(path, led)
    return {"file": path.name, "dropped": dropped, "rows": len(led.rows), "period": led.meta["period"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("apply", help="write classification from a JSON plan {rename, map, rows}")
    p.add_argument("file", help="converted file inside .tmp/")
    p.add_argument("--input", required=True, help="plan JSON file inside .tmp/, or - for stdin")
    p.add_argument("--source", choices=["auto", "user"], default="auto", help="user marks rows as answered")
    p.add_argument("--dry-run", action="store_true", help="only list the changes")
    p = sub.add_parser("drop", help="remove confirmed duplicate rows")
    p.add_argument("file", help="converted file inside .tmp/")
    p.add_argument("--rows", required=True, help="comma-separated row numbers (1-based)")
    p = sub.add_parser("trim", help="drop rows outside the analysis period (before the snapshot)")
    p.add_argument("file", help="normalized file inside .tmp/")
    p.add_argument("--from", dest="start", required=True, metavar="YYYY-MM-DD")
    p.add_argument("--until", dest="end", required=True, metavar="YYYY-MM-DD")
    for p in sub.choices.values():
        p.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        result = {"apply": cmd_apply, "drop": cmd_drop, "trim": cmd_trim}[args.cmd](args, Path.cwd())
    except (LedgerError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cmd == "apply":
        for c in result["changes"]:
            print(f"row {c['row']:>5} {c['title']!r}: {c['field']} {c['old']!r} -> {c['new']!r}")
        print(f"{len(result['changes'])} change(s), {len(result['protected_rows'])} protected user row(s)"
              + (" (dry run)" if args.dry_run else ""))
    elif args.cmd == "trim":
        print(f"{result['file']}: dropped {result['dropped']} row(s) outside the period; {result['rows']} left")
    else:
        print(f"dropped {len(result['dropped'])} row(s); {result['rows']} left")
    return 0


if __name__ == "__main__":
    sys.exit(main())
