"""Copy the staged originals into one plainly named folder per candidate in the run folder.

  cvs-organise <run> <plan.json> [--json]

Reads <run>/.work/staging/manifest.json written by cvs-stage and a plan file:
  {"folders": {"g-01": "roger-mathias"}, "files": {"doc-05": "anna-silva"}}
"folders" copies every document of a group folder into <run>/.work/sources/<slug>/, keeping subpaths.
"files" copies one staged document's original into the candidate slug folder (it overrides its group).
Different files with the same name get a -2, -3 suffix. The source folder is only read. Safe to re-run.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.folders import read_json, resolve_folder, resolve_run
from analyse_cvs.app.organising import organise
from analyse_cvs.shared.constants import MANIFEST


def main(argv: list[str] | None = None) -> int:
    """Run the organise command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-organise",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("run", help="run folder, relative to the current directory, inside .tmp/")
    parser.add_argument("plan", help="JSON plan file")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        run = resolve_run(args.run, Path.cwd())
        if not (run / MANIFEST).is_file():
            msg = "manifest not found; run cvs-stage first"
            raise ValueError(msg)  # noqa: TRY301
        source = resolve_folder(read_json(run / MANIFEST)["source_root"], Path.cwd())
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        result = organise(run, source, plan)
    except (ValueError, OSError, KeyError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, path in result["organised"].items():
            print(f"{key!r} -> {path}")
        for doc_id in result["unassigned"]:
            print(f"unassigned {doc_id}")
        print(f"{len(result['organised'])} file(s) copied for {len(result['slugs'])} candidate folder(s)")
    return 0
