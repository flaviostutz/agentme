"""Stage, discover and normalize source files of one analysis (working files in .tmp/<id>/.work/).

Subcommands:
  stage <input> --id ID      copy a file, folder or zip into .tmp/<id>/.work/sources/ (tree kept, duplicates skipped)
  discover --id ID           per file: module, text layer, account, period; groups, conflicts, gaps, period proposal
  rename --id ID --to NEW    move .tmp/<id>/ to .tmp/<new>/ (before any file is normalized)
  run <source> --id ID       write .tmp/<id>/.work/normalized/<name>-<ext>.md with an institution module or --mapping
Sources are never modified. Exit codes: 0 ok, 2 invalid input or no known format (use the LLM path).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analyse_account_transactions.adapters.connectors.institutions import default_registry
from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.adapters.connectors.sources.sourcedoc import LocalSources
from analyse_account_transactions.app import normalize
from analyse_account_transactions.shared.errors import LedgerError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aat-normalize",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("stage", help="copy input files into .tmp/<id>/.work/sources/")
    p.add_argument("input", help="file, folder or zip (read only)")
    p = sub.add_parser("discover", help="describe staged files and propose the analysis period")
    p = sub.add_parser("rename", help="move the analysis folder to a new id (before normalizing)")
    p.add_argument("--to", required=True, help="new analysis id, e.g. transactions-2026-09-28-jane-doe")
    p = sub.add_parser("run", help="normalize one staged file")
    p.add_argument("source", help="path relative to .tmp/<id>/.work/sources/")
    p.add_argument("--module", help="force an institution module by name")
    p.add_argument("--mapping", help="mapping JSON inside .tmp/ for unknown tables")
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="override a header field")
    p.add_argument("--force", action="store_true", help="overwrite an existing normalized file")
    for p in sub.choices.values():
        p.add_argument("--id", required=True, help="analysis id, e.g. transactions-2026-09-28-jane-doe")
    return parser


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    fs = LocalWorkspace(Path.cwd())
    sources = LocalSources()
    registry = default_registry()
    if args.cmd == "stage":
        return normalize.stage(fs, args.input, args.id)
    if args.cmd == "discover":
        return normalize.discover(fs, sources, registry, args.id)
    if args.cmd == "rename":
        return normalize.rename(fs, args.id, args.to)
    options = {"module": args.module, "mapping": args.mapping, "set": args.set, "force": args.force}
    return normalize.run(fs, sources, registry, args.id, args.source, options)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = _execute(args)
    except (LedgerError, OSError, KeyError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    except Exception as err:  # noqa: BLE001 - third-party parsers raise many types for corrupt files
        print(f"error: cannot read {getattr(args, 'source', '')}: {type(err).__name__}: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
