"""Validate normalized transaction files of one analysis.

  aat-validate accounts <normalized...>      per account: continuity, missing months, rows repeated in
                                             overlapping files; one currency; row count warning (> 2000)
  aat-validate <normalized> --phase P        P = convert | auto | final; convert also writes the snapshot
Exit codes: 0 valid, 1 validation errors, 2 invalid input.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import validate
from analyse_account_transactions.shared.errors import LedgerError


def _validate(args: argparse.Namespace, store: LocalWorkspace) -> dict[str, Any]:
    if args.target == "accounts":
        if not args.files:
            msg = "accounts needs at least one file"
            raise LedgerError(msg)
        return validate.check_accounts(store, args.files)
    if not args.phase or args.files:
        msg = "a normalized file needs --phase and no extra files"
        raise LedgerError(msg)
    return validate.check_file(store, store.resolve_tmp(args.target), args.phase)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aat-validate",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="'accounts', or a normalized file inside .tmp/")
    parser.add_argument("files", nargs="*", help="normalized files for 'accounts'")
    parser.add_argument("--phase", choices=["convert", "auto", "final"], help="phase for a normalized file")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)
    try:
        result = _validate(args, LocalWorkspace(Path.cwd()))
    except (LedgerError, OSError, KeyError, json.JSONDecodeError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for kind in ("errors", "warnings"):
            for e in result[kind]:
                where = e.get("file") or (f"row {e['row']}" if e.get("row") else "file")
                print(f"{kind[:-1]:<7} [{e['rule']}] {where}: {e['message']}")
        print("OK" if result["ok"] else f"FAILED: {len(result['errors'])} error(s)")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
