"""Organise a staged .tmp/ source folder into one plainly named folder per candidate.

Reads md/.staging/manifest.json written by cvs-stage and a plan file:
  {"folders": {"g-01": "roger-mathias"}, "files": {"doc-05": "anna-silva"}}
"folders" renames a group folder to a candidate slug, merging into an existing slug folder.
"files" moves a staged document's source file into the candidate slug folder.
Clashing filenames get a -2, -3 suffix. Folders left empty are removed. Safe to re-run.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.folders import resolve_folder
from analyse_cvs.app.organising import organise
from analyse_cvs.shared.constants import MANIFEST


def main(argv: list[str] | None = None) -> int:
    """Run the organise command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-organise",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("folder", help="source folder, relative to the current directory, inside .tmp/")
    parser.add_argument("plan", help="JSON plan file")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        folder = resolve_folder(args.folder, Path.cwd())
        if not (folder / MANIFEST).is_file():
            msg = "manifest not found; run cvs-stage first"
            raise ValueError(msg)  # noqa: TRY301
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        result = organise(folder, plan)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for r in result["renamed"]:
            print(f"{'merged' if r['merged'] else 'renamed'} {r['from']!r} -> {r['to']}")
        for path in result["removed"]:
            print(f"removed empty folder {path!r}")
        print(f"{len(result['renamed'])} folder(s) renamed or merged, {len(result['removed'])} removed")
    return 0
