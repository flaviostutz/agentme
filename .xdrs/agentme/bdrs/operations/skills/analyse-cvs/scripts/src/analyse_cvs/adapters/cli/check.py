"""Check a report mechanically at one stage of the analysis.

  cvs-check <report> --stage criteria|scores|scenarios|interview [--name <candidate>] [--json]

criteria   weights, criteria count, 3 aspects and aspect weight bounds
scores     score ranges, one decimal, Rationale and Notes limits, source references, Base gap
scenarios  S1-S3 lines in Scenario notes and the adjustment limits
interview  the interview list matches the ranking and every Chart link is filled
Prints errors (exit 1) and warnings (the skill must resolve or justify each one). Never writes.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.reports import read_lines, resolve_report
from analyse_cvs.app.checking import Findings, check_criteria, check_interview_findings, check_rows
from analyse_cvs.app.report_tables import aspect_weights, candidates_table, parse_criteria

STAGES = ("criteria", "scores", "scenarios", "interview")


def _run(report: str, stage: str, name: str | None) -> Findings:
    lines = read_lines(resolve_report(report, Path.cwd()))
    criteria = parse_criteria(lines)
    if stage == "criteria":
        return check_criteria(criteria)
    weights = aspect_weights(criteria)
    table = candidates_table(lines, list(weights))
    if stage == "interview":
        return check_interview_findings(lines, table)
    return check_rows(table, weights, stage, name)


def main(argv: list[str] | None = None) -> int:
    """Run the check command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-check",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("report", help="report file inside .tmp/")
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--name", help="check only this candidate, by slug or name (scores and scenarios stages)")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        findings = _run(args.report, args.stage, args.name)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for error in findings["errors"]:
            print(f"error: {error}")
        for warning in findings["warnings"]:
            print(f"warning: {warning}")
        print(f"{len(findings['errors'])} error(s), {len(findings['warnings'])} warning(s)")
    return 1 if findings["errors"] else 0
