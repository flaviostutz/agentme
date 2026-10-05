"""Exact calculations over one or more classified normalized files (.tmp/<id>/normalized/*.md).

  totals       credits, debits, net balance, totals per category/flow/relevance
  flow         Income = Savings (put aside + kept in accounts) + Expenditures; exit 1 if it does not hold
  relevance    share of Expenditures per relevance class and the top 6 counterparties
  recurrence   Daily/Weekly/Monthly/Quarterly/Yearly/One-off buckets; exit 1 if buckets do not sum to the total
  recurring    recurring charges (stable amount, Weekly..Yearly) with totals and active/stopped status
  insights     small-but-adds-up, large counterparties and hidden spending (--hidden title map)
  query        filter (k=v exact, k~v contains, k=- empty) and group rows
  duplicates   identical rows across files of the same account
  estimate     saving when reducing a title, category or relevance class by a percentage
Every result carries the analysis currency taken from the file headers.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.app import patterns, stats
from analyse_account_transactions.shared.errors import LedgerError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aat-stats",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("cmd", choices=stats.COMMANDS)
    parser.add_argument("files", nargs="+", help="normalized files inside .tmp/")
    parser.add_argument("--assign", help='JSON {"Title": "Quarterly"|"Yearly"} for one-off titles (inferred)')
    parser.add_argument("--hidden", help='insights: JSON file {"Title": "cash"|"card"|"provider"|"fees"}')
    parser.add_argument(
        "--threshold",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=f"insights: override {', '.join(patterns.THRESHOLDS)}",
    )
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="query filter k=v or k~v; k=- matches empty fields (repeatable)",
    )
    parser.add_argument("--group-by", choices=stats.GROUP_KEYS, help="query grouping key")
    parser.add_argument("--target", help="estimate target: title=..., category=... or relevance=...")
    parser.add_argument("--reduce-pct", default="0", help="estimate reduction percentage (0-100]")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON (default output)")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.cmd == "estimate" and not args.target:
        parser.error("estimate needs --target and --reduce-pct")
    request = stats.Request(
        cmd=args.cmd,
        files=args.files,
        assign=args.assign,
        hidden=args.hidden,
        threshold=args.threshold,
        filters=args.filter,
        group_by=args.group_by,
        target=args.target,
        reduce_pct=args.reduce_pct,
    )
    try:
        result, ok = stats.run(LocalWorkspace(Path.cwd()), request)
    except (LedgerError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, default=stats.encode))
    if not ok:
        print(f"error: {args.cmd} invariant failed", file=sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
