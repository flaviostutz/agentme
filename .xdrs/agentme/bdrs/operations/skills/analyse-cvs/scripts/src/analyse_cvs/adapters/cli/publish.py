"""Copy the original documents of each invited candidate into its own folder in the run folder.

  cvs-publish <run> <slug>... [--json]

Copies <run>/.work/sources/<slug>/ to <run>/<slug>/ keeping subpaths. Existing files are never
overwritten, so it is safe to re-run after new documents arrive. An original named
interview-chart.md is copied as original-interview-chart.md so it cannot pass for the chart.
All slugs are validated before anything is copied.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.adapters.connectors.local_fs.folders import resolve_run
from analyse_cvs.app.publishing import publish


def main(argv: list[str] | None = None) -> int:
    """Run the publish command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-publish",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("run", help="run folder, relative to the current directory, inside .tmp/")
    parser.add_argument("slugs", nargs="+", help="candidate slugs to publish")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        result = publish(resolve_run(args.run, Path.cwd()), args.slugs)
    except (ValueError, OSError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for slug, r in result.items():
            print(f"{slug}: {len(r['copied'])} copied, {len(r['existing'])} already there")
    return 0
