"""Keep the user's classification answers so later analyses of the same rows never ask again.

export  rows answered by the user (needs-investigation: user) into an answers file
apply   re-apply matching answers to a normalized file as user answers
import  merge answers of other analyses
An answer is keyed by timestamp, value, description and occurrence (nth identical row of a file); the newest
answer wins. Only classification is stored (category, flow, relevance); values are never changed.
"""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from analyse_account_transactions.app import ledger
from analyse_account_transactions.app.jsonfile import read_json, write_json
from analyse_account_transactions.app.ports import LedgerStore
from analyse_account_transactions.shared.constants import CLASS_FIELDS
from analyse_account_transactions.shared.errors import LedgerError
from analyse_account_transactions.shared.models import Ledger, Row

VERSION = 1
Clock = Callable[[], datetime]


def keyed_rows(led: Ledger) -> list[tuple[str, int, Row]]:
    """[(key, row index, row)] with the occurrence number making identical rows distinct."""
    seen: dict[str, int] = {}
    result = []
    for i, r in enumerate(led.rows, 1):
        base = "|".join(r.key())
        seen[base] = seen.get(base, 0) + 1
        result.append((f"{base}|{seen[base]}", i, r))
    return result


def load_answers(store: LedgerStore, path: Path) -> dict[str, Any]:
    data = read_json(store, path)
    if data is None:
        return {}
    if not isinstance(data, dict) or data.get("version") != VERSION or not isinstance(data.get("answers"), dict):
        msg = f"{path.name} is not an answers file (version {VERSION})"
        raise LedgerError(msg)
    return data["answers"]


def save_answers(store: LedgerStore, path: Path, answers: dict[str, Any]) -> None:
    write_json(store, path, {"version": VERSION, "answers": dict(sorted(answers.items()))})


def export_answers(store: LedgerStore, files: list[str], into: str, clock: Clock) -> dict[str, Any]:
    target = store.resolve_tmp(into, must_exist=False)
    answers = load_answers(store, target)
    added = updated = 0
    for p in files:
        path = store.resolve_tmp(p)
        for key, _, r in keyed_rows(ledger.read(store, path)):
            if r.needs != "user":
                continue
            fields = {k: getattr(r, k) for k in CLASS_FIELDS}
            old = answers.get(key)
            if old and {k: old[k] for k in CLASS_FIELDS} == fields:
                continue
            added += old is None
            updated += old is not None
            answered = clock().strftime("%Y-%m-%dT%H:%M:%SZ")
            answers[key] = {**fields, "title": r.title, "answered": answered, "file": path.name}
    save_answers(store, target, answers)
    return {"answers": store.rel(target), "total": len(answers), "added": added, "updated": updated}


def import_answers(store: LedgerStore, files: list[str], into: str) -> dict[str, Any]:
    target = store.resolve_tmp(into, must_exist=False)
    answers = load_answers(store, target)
    added = updated = 0
    for p in files:
        for key, entry in load_answers(store, store.resolve_tmp(p)).items():
            old = answers.get(key)
            if old is None or entry.get("answered", "") > old.get("answered", ""):
                added += old is None
                updated += old is not None
                answers[key] = entry
    save_answers(store, target, answers)
    return {"answers": store.rel(target), "total": len(answers), "added": added, "updated": updated}


def apply_answers(store: LedgerStore, file: str, answers_file: str) -> dict[str, Any]:
    path = store.resolve_tmp(file)
    answers = load_answers(store, store.resolve_tmp(answers_file))
    led = ledger.read(store, path)
    snapshot = ledger.load_snapshot(store, path)
    plan = {}
    skipped = []
    for key, i, _ in keyed_rows(led):
        entry = answers.get(key)
        if entry:
            plan[str(i)] = {k: entry[k] for k in CLASS_FIELDS}
    valid = {}
    for num, entry in plan.items():
        try:
            ledger.plan_changes(led, {"rows": {num: entry}}, "user")
            valid[num] = entry
        except LedgerError as err:
            skipped.append({"row": int(num), "message": str(err)})
    changes, _ = ledger.plan_changes(led, {"rows": valid}, "user")
    ledger.apply_changes(led, changes)
    for num in valid:
        snapshot["user"][num] = {k: getattr(led.rows[int(num) - 1], k) for k in CLASS_FIELDS}
    ledger.write(store, path, led)
    ledger.write_snapshot(store, path, led, snapshot["user"])
    return {
        "file": path.name,
        "applied": len(valid),
        "changes": len(changes),
        "skipped": skipped,
        "rows": len(led.rows),
    }
