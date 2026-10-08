"""Rank the candidates by unrounded Overall and prepare the interview list.

  cvs-rank <report> [--write] [--json]

Recomputes every Overall from Base and Credibility with exact arithmetic and lists the candidates
by Overall, highest first, ties by Name. Exits with an error when a row is incomplete or a stored
Overall differs from the recomputed one. Invites every candidate whose unrounded Overall is above 5.0.
With --write it also sorts the Candidates table and writes the interview list section with the
heading, counts, closing sentence and one `- Chart: <fill>` bullet per invited candidate; replace
each `<fill>` with the link to the candidate's interview chart and run `cvs-check --stage interview`.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.reports import read_lines, resolve_report, write_lines
from analyse_cvs.app.ranking import apply_ranking, rank_table
from analyse_cvs.app.report_tables import aspect_weights, candidates_table, parse_criteria
from analyse_cvs.shared.decimals import show


def main(argv: list[str] | None = None) -> int:
    """Run the rank command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-rank",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("report", help="report file inside .tmp/")
    parser.add_argument("--write", action="store_true", help="sort the Candidates table and write the interview list")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        path = resolve_report(args.report, Path.cwd())
        lines = read_lines(path)
        table = candidates_table(lines, list(aspect_weights(parse_criteria(lines))))
        ranked = rank_table(table)
        if args.write:
            write_lines(path, apply_ranking(lines, table, ranked))
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    invited = sum(1 for r in ranked if r.invited)
    if args.json:
        rows = [
            {"rank": i, "name": r.name, "overall": show(r.overall), "invited": r.invited}
            for i, r in enumerate(ranked, start=1)
        ]
        print(json.dumps({"invited": invited, "total": len(ranked), "ranking": rows}, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(ranked, start=1):
            print(f"{i}. {r.name} {show(r.overall)}{' (invite)' if r.invited else ''}")
        print(f"Invited: {invited} of {len(ranked)}")
    return 0
