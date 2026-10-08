"""Copy candidate documents from a .tmp/ source folder to safe staging names in a run folder.

  cvs-stage <source> --run <run> [--json]

Top-level files and files inside top-level subfolders (any depth) are staged to <run>/.work/staging/doc-NN.<ext>.
Each top-level subfolder becomes a group (g-NN), a clue that its documents belong to one candidate.
The source folder is only read, never changed. The run folder must be inside .tmp/ and separate from the source.
Raw file and folder names are never passed to a shell: the agent only ever sees staged names and ids.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.folders import resolve_folder, resolve_run
from analyse_cvs.app.staging import stage


def main(argv: list[str] | None = None) -> int:
    """Run the stage command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-stage",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("source", help="source folder, relative to the current directory, inside .tmp/")
    parser.add_argument("--run", required=True, help="run folder inside .tmp/, separate from the source")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        source = resolve_folder(args.source, Path.cwd())
        run = resolve_run(args.run, Path.cwd(), source)
        manifest = stage(source, run)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    files = manifest["files"]
    if args.json:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        for g in manifest["groups"]:
            print(f"group {g['id']}: {g['name']!r}")
        for r in files:
            target = r["staged"] or "-"
            print(f"{r['status']:<12} {target:<24} {r['group'] or '-':<5} {r['source']!r}")
        staged = sum(r["status"] == "staged" for r in files)
        unsupported = sum(r["status"] == "unsupported" for r in files)
        print(f"{staged} staged, {unsupported} unsupported, {len(manifest['groups'])} group(s)")
    return 0
