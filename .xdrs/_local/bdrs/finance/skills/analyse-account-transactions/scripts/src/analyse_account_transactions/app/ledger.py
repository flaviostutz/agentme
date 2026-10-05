"""Read, write and classify normalized transaction files (.tmp/<id>/normalized/<name>-<ext>.md).

Values, timestamps and descriptions are never changed by classification: apply writes category, flow, relevance and
needs-investigation from a plan, drop removes confirmed duplicate rows, trim removes rows outside the analysis period.
"""

import json
import re
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

from analyse_account_transactions.app.jsonfile import read_json, write_json
from analyse_account_transactions.app.ports import LedgerStore
from analyse_account_transactions.shared.constants import (
    CATEGORIES,
    CLASS_FIELDS,
    COLUMNS,
    FLOWS,
    MAX_DESCRIPTION,
    META_KEYS,
    RELEVANCES,
)
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Ledger, Row
from analyse_account_transactions.shared.values import format_value, parse_value

_META_RE = re.compile(r"^([a-z][a-z-]*): ?(.*)$")
_PIPE_SPLIT = re.compile(r"(?<!\\)\|")
_ISO_DAY = re.compile(r"\d{4}-\d{2}-\d{2}")
Change = dict[str, Any]


def escape_cell(text: str) -> str:
    text = re.sub(r"\s+", " ", text.replace("\\|", "|")).strip()
    return text.replace("|", "\\|")


def clip_description(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= MAX_DESCRIPTION else text[: MAX_DESCRIPTION - 3].rstrip() + "..."


def snapshot_path(path: Path) -> Path:
    return path.with_name(path.stem + ".snapshot.json")


def split_cells(line: str) -> list[str]:
    body = line.strip()
    if not (body.startswith("|") and body.endswith("|")) or body.endswith("\\|"):
        msg = "table row must start and end with '|'"
        raise LedgerError(msg)
    return [c.strip().replace("\\|", "|") for c in _PIPE_SPLIT.split(body[1:-1])]


def _parse_row(n: int, line: str) -> Row:
    try:
        cells = split_cells(line)
    except LedgerError as err:
        msg = f"line {n}: {err}"
        raise LedgerError(msg) from err
    if len(cells) != len(COLUMNS):
        msg = f"line {n}: expected {len(COLUMNS)} columns, found {len(cells)} (A9)"
        raise LedgerError(msg)
    try:
        value = parse_value(cells[2])
    except LedgerError as err:
        msg = f"line {n}: {err}"
        raise LedgerError(msg) from err
    return Row(cells[0], cells[1], value, cells[3], *cells[4:])


def parse_text(text: str) -> Ledger:
    meta: dict[str, str] = {}
    rows: list[Row] = []
    in_table = False
    for n, line in enumerate(text.splitlines(), 1):
        if not in_table:
            m = _META_RE.match(line)
            if m and m.group(1) in META_KEYS:
                meta[m.group(1)] = m.group(2).strip()
            elif line.startswith("| timestamp"):
                if split_cells(line) != COLUMNS:
                    msg = f"line {n}: header must be: {' | '.join(COLUMNS)}"
                    raise LedgerError(msg)
                in_table = True
            continue
        if not line.strip():
            break
        if re.fullmatch(r"\|(\s*-+\s*\|)+", line.strip()):
            continue
        rows.append(_parse_row(n, line))
    if not in_table:
        msg = "no transaction table found (header '| timestamp | title | ...')"
        raise LedgerError(msg)
    return Ledger(meta, rows)


def render(ledger: Ledger, name: str) -> str:
    lines = [f"# Transactions: {name}", ""]
    lines += [f"{k}: {ledger.meta[k]}" for k in META_KEYS if k in ledger.meta]
    lines += ["", "| " + " | ".join(COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for r in ledger.rows:
        cells = [r.timestamp, r.title, format_value(r.value), r.description, r.category, r.flow, r.relevance, r.needs]
        lines.append("| " + " | ".join(escape_cell(c) for c in cells) + " |")
    return "\n".join(lines) + "\n"


def read(store: LedgerStore, path: Path) -> Ledger:
    return parse_text(store.read_text(path))


def write(store: LedgerStore, path: Path, ledger: Ledger) -> None:
    store.write_text(path, render(ledger, path.stem))


def load_snapshot(store: LedgerStore, path: Path) -> dict[str, Any]:
    snap = snapshot_path(path)
    data = read_json(store, snap)
    if data is None:
        msg = f"snapshot missing, run aat-validate {path.name} --phase convert first: {snap.name}"
        raise LedgerError(msg)
    return data


def write_snapshot(store: LedgerStore, path: Path, ledger: Ledger, user: dict[str, Any]) -> None:
    data = {
        "rows": [r.key() for r in ledger.rows],
        "sum": format_value(sum((r.value for r in ledger.rows), Decimal(0))),
        "user": user,
    }
    write_json(store, snapshot_path(path), data)


def _check_entry(where: str, entry: dict[str, Any]) -> dict[str, Any]:
    allowed = {"category": CATEGORIES, "flow": FLOWS, "relevance": [*RELEVANCES, ""], "needs": ["yes", "no"]}
    unknown = set(entry) - set(allowed) - {"title"}
    if unknown:
        msg = f"{where}: unknown keys {sorted(unknown)}"
        raise LedgerError(msg)
    for key, options in allowed.items():
        if key in entry and entry[key] not in options:
            msg = f"{where}: invalid {key} {entry[key]!r}"
            raise LedgerError(msg)
    if "title" in entry and not str(entry["title"]).strip():
        msg = f"{where}: empty title"
        raise LedgerError(msg)
    return entry


def _row_exceptions(ledger: Ledger, plan: dict[str, Any]) -> dict[int, dict[str, Any]]:
    exceptions: dict[int, dict[str, Any]] = {}
    for num, entry in plan.get("rows", {}).items():
        if not str(num).isdigit() or not 1 <= int(num) <= len(ledger.rows):
            msg = f"rows: row {num!r} does not exist (1..{len(ledger.rows)})"
            raise LedgerError(msg)
        exceptions[int(num)] = _check_entry(f"rows[{num}]", entry)
    return exceptions


def plan_changes(ledger: Ledger, plan: dict[str, Any], source: str) -> tuple[list[Change], list[int]]:
    """Return (changes, protected_rows); raises LedgerError for invalid plans."""
    rename = plan.get("rename", {})
    mapping = {t: _check_entry(f"map[{t!r}]", e) for t, e in plan.get("map", {}).items()}
    exceptions = _row_exceptions(ledger, plan)
    changes: list[Change] = []
    protected: list[int] = []
    for i, row in enumerate(ledger.rows, 1):
        title = rename.get(row.title, row.title)
        entry = {**mapping.get(title, {}), **exceptions.get(i, {})}
        if title != row.title:
            entry.setdefault("title", title)
        if not entry:
            continue
        if row.needs == "user" and source == "auto" and set(entry) - {"title"}:
            if i in exceptions:
                msg = f"rows[{i}]: row was answered by the user and cannot be changed automatically"
                raise LedgerError(msg)
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


def apply_changes(ledger: Ledger, changes: list[Change]) -> None:
    for c in changes:
        setattr(ledger.rows[c["row"] - 1], c["field"], c["new"])


def apply_plan(
    store: LedgerStore,
    file: str,
    read_plan: Callable[[], str],
    *,
    source: str,
    dry_run: bool,
) -> dict[str, Any]:
    """Apply a classification plan {rename, map, rows}; read_plan returns the plan JSON text."""
    path = store.resolve_tmp(file)
    ledger = read(store, path)
    raw = read_plan()
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as err:
        msg = f"plan is not valid JSON: {err}"
        raise LedgerError(msg) from err
    if not isinstance(plan, dict) or set(plan) - {"rename", "map", "rows"}:
        msg = "plan must be an object with only 'rename', 'map' and 'rows'"
        raise LedgerError(msg)
    snapshot = load_snapshot(store, path)
    changes, protected = plan_changes(ledger, plan, source)
    result = {"file": path.name, "dry_run": dry_run, "changes": changes, "protected_rows": protected}
    if dry_run:
        return result
    apply_changes(ledger, changes)
    if source == "user":
        for i in sorted({c["row"] for c in changes}):
            row = ledger.rows[i - 1]
            snapshot["user"][str(i)] = {k: getattr(row, k) for k in CLASS_FIELDS}
    write(store, path, ledger)
    write_snapshot(store, path, ledger, snapshot["user"])
    return result


def drop_rows(store: LedgerStore, file: str, rows_arg: str) -> dict[str, Any]:
    """Remove confirmed duplicate rows (comma-separated 1-based numbers) and update the snapshot."""
    path = store.resolve_tmp(file)
    ledger = read(store, path)
    snapshot = load_snapshot(store, path)
    try:
        nums = sorted({int(n) for n in rows_arg.split(",")})
    except ValueError as err:
        msg = f"--rows must be comma-separated row numbers: {rows_arg!r}"
        raise LedgerError(msg) from err
    if not nums or nums[0] < 1 or nums[-1] > len(ledger.rows):
        msg = f"rows out of range 1..{len(ledger.rows)}: {rows_arg}"
        raise LedgerError(msg)
    dropped = [ledger.rows[n - 1].key() for n in nums]
    keep = [i for i in range(1, len(ledger.rows) + 1) if i not in nums]
    user = {str(new): snapshot["user"][str(old)] for new, old in enumerate(keep, 1) if str(old) in snapshot["user"]}
    ledger.rows = [ledger.rows[i - 1] for i in keep]
    write(store, path, ledger)
    write_snapshot(store, path, ledger, user)
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
    if not (_ISO_DAY.fullmatch(old_start) and _ISO_DAY.fullmatch(old_end)):
        old_start, old_end = start, end
    led.meta["period"] = f"{max(start, old_start)}..{min(end, old_end)}"
    return len(before) + len(after)


def trim_file(store: LedgerStore, file: str, start: str, end: str) -> dict[str, Any]:
    """Trim a normalized file to the analysis period; only allowed before the snapshot exists."""
    for d in (start, end):
        if not _ISO_DAY.fullmatch(d):
            msg = f"--from/--until must be YYYY-MM-DD: {d!r}"
            raise LedgerError(msg)
    if start > end:
        msg = "--from is after --until"
        raise LedgerError(msg)
    path = store.resolve_tmp(file)
    led = read(store, path)
    if store.exists(snapshot_path(path)):
        msg = "trim before the snapshot (aat-validate --phase convert), not after"
        raise LedgerError(msg)
    dropped = trim(led, start, end)
    write(store, path, led)
    return {"file": path.name, "dropped": dropped, "rows": len(led.rows), "period": led.meta["period"]}
