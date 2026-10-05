"""Read, write and classify normalized transaction files (.tmp/<id>/normalized/<name>-<ext>.md).

Subcommands:
  apply  write category, flow, relevance and needs-investigation from a JSON plan; never touches values
  drop   remove confirmed duplicate rows and update the snapshot
  trim   drop rows outside the analysis period and move the balances so they still reconcile
Values, timestamps and descriptions are never changed by this tool.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import ledger
from analyse_account_transactions.shared.errors import LedgerError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aat-ledger",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
    return parser


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    store = LocalWorkspace(Path.cwd())
    if args.cmd == "apply":

        def read_plan() -> str:
            return sys.stdin.read() if args.input == "-" else store.read_text(store.resolve_tmp(args.input))

        return ledger.apply_plan(store, args.file, read_plan, source=args.source, dry_run=args.dry_run)
    if args.cmd == "drop":
        return ledger.drop_rows(store, args.file, args.rows)
    return ledger.trim_file(store, args.file, args.start, args.end)


def _print_text(args: argparse.Namespace, result: dict[str, Any]) -> None:
    if args.cmd == "apply":
        for c in result["changes"]:
            print(f"row {c['row']:>5} {c['title']!r}: {c['field']} {c['old']!r} -> {c['new']!r}")
        print(
            f"{len(result['changes'])} change(s), {len(result['protected_rows'])} protected user row(s)"
            + (" (dry run)" if args.dry_run else ""),
        )
    elif args.cmd == "trim":
        print(f"{result['file']}: dropped {result['dropped']} row(s) outside the period; {result['rows']} left")
    else:
        print(f"dropped {len(result['dropped'])} row(s); {result['rows']} left")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = _execute(args)
    except (LedgerError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_text(args, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
