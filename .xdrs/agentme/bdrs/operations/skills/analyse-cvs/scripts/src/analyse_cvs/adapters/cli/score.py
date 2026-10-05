"""Compute scores exactly: scenario dry-run and Overall, read from the report tables.

  cvs-score dryrun <report> <name> --adjustments '{"S2": {"Stakeholder management": "-0.5"}}'
      Applies the scenario adjustments (at most +-1.0 per scenario and aspect, +-2.0 per aspect in
      total) to the row's aspect scores and shifts Base by their weighted sum. Prints the new
      aspect scores and Base; refuses rows that already have Scenario notes.
  cvs-score overall <report> <name>
      Prints Overall = Base + (Credibility - 5.5) / 4.5, clamped to 1.0-10.0, rounded half up to
      one decimal, plus whether the unrounded value is above 5.0.

Reads the report only and never writes it. Uses exact decimal arithmetic.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from analyse_cvs.adapters.connectors.local_fs.reports import read_lines, resolve_report
from analyse_cvs.app.report_tables import aspect_weights, candidates_table, find_row, parse_criteria
from analyse_cvs.app.scoring import dry_run, overall, parse_adjustments
from analyse_cvs.shared.decimals import parse_decimal


def _run(args: argparse.Namespace) -> dict[str, Any]:
    lines = read_lines(resolve_report(args.report, Path.cwd()))
    weights = aspect_weights(parse_criteria(lines))
    row = find_row(candidates_table(lines, list(weights)), args.name)
    base, credibility = parse_decimal(row["Base"]), parse_decimal(row["Credibility"])
    if args.command == "overall":
        return overall(base, credibility)
    if row["Scenario notes"]:
        msg = f"{args.name} already has Scenario notes; the dry-run was already applied and must not be repeated"
        raise ValueError(msg)
    scores = {aspect: parse_decimal(row[aspect]) for aspect in weights}
    return dry_run(scores, base, weights, parse_adjustments(args.adjustments))


def main(argv: list[str] | None = None) -> int:
    """Run the score command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-score",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    dry = sub.add_parser("dryrun", help="apply scenario adjustments to one candidate row")
    dry.add_argument("--adjustments", default="{}", help='JSON {"S1": {"<aspect>": "+0.5"}}; omit scenarios with "="')
    over = sub.add_parser("overall", help="compute Overall for one candidate row")
    for p in (dry, over):
        p.add_argument("report", help="report file inside .tmp/")
        p.add_argument("name", help="candidate slug (preferred) or name from the Candidates table")
        p.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        result = _run(args)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "overall":
        print(f"Overall {result['overall']} (unrounded {result['unrounded']}, invited: {result['invited']})")
    else:
        print(f"Base {result['base']} (shift {result['shift']})")
        for aspect, score in result["aspects"].items():
            print(f"{aspect}: {score}")
    return 0
