"""Fill the Sources and Candidates tables after the documents are converted and organised.

  cvs-sources <run> <report> <docs.json> [--json]

docs.json maps each staged document id to a decision:
  {"doc-01": {"candidate": "Roger Mathias", "slug": "roger-mathias", "type": "cv"},
   "doc-02": {"skip": "unreadable"}}
Types: cv, cover-letter, portfolio, certificate, reference-letter, other.
Moves <run>/.work/staging/doc-NN-converted.md to <run>/.work/md/<slug>-<type>.md (with -2, -3 for
repeats), adds one Sources row per document (unsupported files are recorded as skipped), adds a
Candidates row with only the Name for each new candidate, then deletes the staging folder. The
whole input is validated before anything changes.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.folders import remove_staging, resolve_run
from analyse_cvs.adapters.connectors.local_fs.reports import read_lines, resolve_report, write_lines
from analyse_cvs.app.registering import register


def main(argv: list[str] | None = None) -> int:
    """Run the sources command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-sources",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("run", help="run folder, relative to the current directory, inside .tmp/")
    parser.add_argument("report", help="report file inside .tmp/")
    parser.add_argument("docs", help="JSON file with one decision per staged document id")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        run = resolve_run(args.run, Path.cwd())
        report = resolve_report(args.report, Path.cwd())
        docs = json.loads(Path(args.docs).read_text(encoding="utf-8"))
        if not isinstance(docs, dict) or not all(isinstance(v, dict) for v in docs.values()):
            msg = "docs file must map document ids to objects"
            raise ValueError(msg)  # noqa: TRY301
        lines, summary = register(run, read_lines(report), docs)
        write_lines(report, lines)
        remove_staging(run)
    except (ValueError, OSError, KeyError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for doc_id, path in summary["renamed"].items():
            print(f"{doc_id} -> {path}")
        print(f"{summary['sources_added']} source row(s), {len(summary['candidates_added'])} new candidate(s)")
    return 0
