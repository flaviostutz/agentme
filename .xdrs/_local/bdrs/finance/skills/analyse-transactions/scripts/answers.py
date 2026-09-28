#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Keep the user's classification answers so later analyses of the same rows never ask again.

  answers.py export <normalized...> --into answers.json    rows answered by the user (needs-investigation: user)
  answers.py apply <normalized> --answers answers.json     re-apply matching answers as user answers
  answers.py import <other answers.json...> --into answers.json    merge answers of other analyses
An answer is keyed by timestamp, value, description and occurrence (nth identical row of a file); the newest
answer wins. Only classification is stored (category, flow, relevance); values are never changed.
Exit codes: 0 ok, 2 invalid input.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import ledger
from ledger import CLASS_FIELDS, LedgerError

VERSION = 1


def keyed_rows(led) -> list:
    """[(key, row index, row)] with the occurrence number making identical rows distinct."""
    seen, result = {}, []
    for i, r in enumerate(led.rows, 1):
        base = "|".join(r.key())
        seen[base] = seen.get(base, 0) + 1
        result.append((f"{base}|{seen[base]}", i, r))
    return result


def load_answers(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != VERSION or not isinstance(data.get("answers"), dict):
        raise LedgerError(f"{path.name} is not an answers file (version {VERSION})")
    return data["answers"]


def save_answers(path: Path, answers: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"version": VERSION, "answers": dict(sorted(answers.items()))}
    path.write_text(json.dumps(body, ensure_ascii=False, indent=1), encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_export(args, cwd: Path) -> dict:
    target = ledger.resolve_tmp(args.into, cwd, must_exist=False)
    answers = load_answers(target)
    added = updated = 0
    for p in args.files:
        path = ledger.resolve_tmp(p, cwd)
        for key, _, r in keyed_rows(ledger.read(path)):
            if r.needs != "user":
                continue
            fields = {k: getattr(r, k) for k in CLASS_FIELDS}
            old = answers.get(key)
            if old and {k: old[k] for k in CLASS_FIELDS} == fields:
                continue
            added += old is None
            updated += old is not None
            answers[key] = {**fields, "title": r.title, "answered": now(), "file": path.name}
    save_answers(target, answers)
    return {"answers": str(target.relative_to(cwd.resolve())), "total": len(answers), "added": added,
            "updated": updated}


def cmd_import(args, cwd: Path) -> dict:
    target = ledger.resolve_tmp(args.into, cwd, must_exist=False)
    answers = load_answers(target)
    added = updated = 0
    for p in args.files:
        for key, entry in load_answers(ledger.resolve_tmp(p, cwd)).items():
            old = answers.get(key)
            if old is None or entry.get("answered", "") > old.get("answered", ""):
                added += old is None
                updated += old is not None
                answers[key] = entry
    save_answers(target, answers)
    return {"answers": str(target.relative_to(cwd.resolve())), "total": len(answers), "added": added,
            "updated": updated}


def cmd_apply(args, cwd: Path) -> dict:
    path = ledger.resolve_tmp(args.file, cwd)
    answers = load_answers(ledger.resolve_tmp(args.answers, cwd))
    led = ledger.read(path)
    snapshot = ledger.load_snapshot(path)
    plan, skipped = {}, []
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
    ledger.write(path, led)
    ledger.write_snapshot(path, led, snapshot["user"])
    return {"file": path.name, "applied": len(valid), "changes": len(changes), "skipped": skipped,
            "rows": len(led.rows)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("export", help="store user answers of normalized files")
    p.add_argument("files", nargs="+", help="normalized files inside .tmp/")
    p.add_argument("--into", required=True, help="answers JSON inside .tmp/ (created when missing)")
    p = sub.add_parser("apply", help="re-apply stored answers to a normalized file (after its snapshot)")
    p.add_argument("file", help="normalized file inside .tmp/")
    p.add_argument("--answers", required=True, help="answers JSON inside .tmp/")
    p = sub.add_parser("import", help="merge answers files of other analyses")
    p.add_argument("files", nargs="+", help="answers JSON files inside .tmp/")
    p.add_argument("--into", required=True, help="answers JSON inside .tmp/")
    args = parser.parse_args(argv)
    try:
        result = {"export": cmd_export, "apply": cmd_apply, "import": cmd_import}[args.cmd](args, Path.cwd())
    except (LedgerError, OSError, KeyError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
