"""Keep the user's classification answers so later analyses of the same rows never ask again.

  aat-answers export <normalized...> --into answers.json    rows answered by the user (needs-investigation: user)
  aat-answers apply <normalized> --answers answers.json     re-apply matching answers as user answers
  aat-answers import <other answers.json...> --into answers.json    merge answers of other analyses
An answer is keyed by timestamp, value, description and occurrence (nth identical row of a file); the newest
answer wins. Only classification is stored (category, flow, relevance); values are never changed.
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import answers
from analyse_account_transactions.shared.errors import LedgerError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aat-answers",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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
    return parser


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    store = LocalWorkspace(Path.cwd())
    if args.cmd == "export":
        return answers.export_answers(store, args.files, args.into, lambda: datetime.now(UTC))
    if args.cmd == "apply":
        return answers.apply_answers(store, args.file, args.answers)
    return answers.import_answers(store, args.files, args.into)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = _execute(args)
    except (LedgerError, OSError, KeyError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
