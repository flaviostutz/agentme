"""Cache of web research about counterparties (.tmp/<id>/research/cache.json). Makes no network calls.

  aat-research lookup <name...> --cache FILE          cached findings for these names (case/space-insensitive)
  aat-research add --cache FILE --name N --url U --finding F [--city C] [--category-hint CAT]
  aat-research import <other cache.json...> --cache FILE    merge caches of other analyses (newest wins)
Names and cities are what may be sent to a search engine, so they are rejected when they contain an IBAN,
an amount or a long number (account, card or reference). Exit codes: 0 ok, 1 not found, 2 invalid input.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import research
from analyse_account_transactions.shared.errors import LedgerError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aat-research",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
    return parser


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    store = LocalWorkspace(Path.cwd())
    if args.cmd == "lookup":
        return research.lookup(store, args.cache, args.names)
    if args.cmd == "add":
        finding = research.Finding(
            name=args.name,
            url=args.url,
            finding=args.finding,
            city=args.city or "",
            category_hint=args.category_hint or "",
        )
        return research.add(store, args.cache, finding, lambda: datetime.now(UTC))
    return research.import_caches(store, args.cache, args.files)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = _execute(args)
    except (LedgerError, OSError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 1 if args.cmd == "lookup" and result["missing"] else 0


if __name__ == "__main__":
    sys.exit(main())
