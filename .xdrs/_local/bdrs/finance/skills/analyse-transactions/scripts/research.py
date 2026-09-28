#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Cache of web research about counterparties (.tmp/<id>/research/cache.json). Makes no network calls.

  research.py lookup <name...> --cache FILE          cached findings for these names (case/space-insensitive)
  research.py add --cache FILE --name N --url U --finding F [--city C] [--category-hint CAT]
  research.py import <other cache.json...> --cache FILE    merge caches of other analyses (newest wins)
Names and cities are what may be sent to a search engine, so they are rejected when they contain an IBAN,
an amount or a long number (account, card or reference). Exit codes: 0 ok, 1 not found, 2 invalid input.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import ledger
from ledger import CATEGORIES, LedgerError

VERSION = 1
PRIVATE = [
    ("an IBAN", re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,}")),
    ("an amount", re.compile(r"\d+[.,]\d{2}\b|[€$£]\s?\d")),
    ("a long number", re.compile(r"\d{6,}")),
    ("an e-mail address", re.compile(r"\S+@\S+\.\w+")),
]
MAX_NAME = 80
MAX_FINDING = 400


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != VERSION or not isinstance(data.get("entries"), dict):
        raise LedgerError(f"{path.name} is not a research cache (version {VERSION})")
    return data["entries"]


def save(path: Path, entries: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": VERSION, "entries": dict(sorted(entries.items()))},
                               ensure_ascii=False, indent=1), encoding="utf-8")


def check_query(field: str, text: str) -> None:
    if not text.strip() or len(text) > MAX_NAME:
        raise LedgerError(f"--{field} must be 1..{MAX_NAME} characters")
    for label, pattern in PRIVATE:
        if pattern.search(text):
            raise LedgerError(f"--{field} contains {label}; search the counterparty name only")


def cmd_lookup(args, cwd: Path) -> dict:
    entries = load(ledger.resolve_tmp(args.cache, cwd, must_exist=False))
    found = {n: entries[norm(n)] for n in args.names if norm(n) in entries}
    return {"found": found, "missing": [n for n in args.names if norm(n) not in entries]}


def cmd_add(args, cwd: Path) -> dict:
    check_query("name", args.name)
    if args.city:
        check_query("city", args.city)
    if not re.match(r"^https?://\S+$", args.url):
        raise LedgerError("--url must be an http(s) URL")
    if not args.finding.strip() or len(args.finding) > MAX_FINDING:
        raise LedgerError(f"--finding must be 1..{MAX_FINDING} characters")
    if args.category_hint and args.category_hint not in CATEGORIES:
        raise LedgerError(f"--category-hint must be one of {CATEGORIES}")
    path = ledger.resolve_tmp(args.cache, cwd, must_exist=False)
    entries = load(path)
    entry = {"name": args.name.strip(), "city": args.city or "", "url": args.url, "finding": args.finding.strip(),
             "category-hint": args.category_hint or "", "checked": datetime.now(timezone.utc).date().isoformat()}
    entries[norm(args.name)] = entry
    save(path, entries)
    return {"added": entry, "total": len(entries)}


def cmd_import(args, cwd: Path) -> dict:
    path = ledger.resolve_tmp(args.cache, cwd, must_exist=False)
    entries = load(path)
    added = 0
    for p in args.files:
        for key, entry in load(ledger.resolve_tmp(p, cwd)).items():
            if key not in entries or entry.get("checked", "") > entries[key].get("checked", ""):
                added += key not in entries
                entries[key] = entry
    save(path, entries)
    return {"total": len(entries), "added": added}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lookup", help="cached findings for names")
    p.add_argument("names", nargs="+")
    p = sub.add_parser("add", help="store one finding")
    p.add_argument("--name", required=True, help="counterparty name as searched")
    p.add_argument("--city", help="city searched with the name, if any")
    p.add_argument("--url", required=True, help="source page of the finding")
    p.add_argument("--finding", required=True, help="what the counterparty is, in one or two sentences")
    p.add_argument("--category-hint", help="suggested category (the LLM still decides)")
    p = sub.add_parser("import", help="merge other caches")
    p.add_argument("files", nargs="+", help="cache JSON files inside .tmp/")
    for p in sub.choices.values():
        p.add_argument("--cache", required=True, help="cache JSON inside .tmp/ (created when missing)")
    args = parser.parse_args(argv)
    try:
        result = {"lookup": cmd_lookup, "add": cmd_add, "import": cmd_import}[args.cmd](args, Path.cwd())
    except (LedgerError, OSError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 1 if args.cmd == "lookup" and result["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
