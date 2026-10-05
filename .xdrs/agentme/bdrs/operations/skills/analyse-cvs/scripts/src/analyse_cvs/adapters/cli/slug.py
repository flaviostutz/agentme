"""Derive plain ASCII kebab-case slugs for a role or for candidates.

Each name is treated as a different person: when a slug is already taken (listed in
--existing, or produced earlier in the same call) it gets the next free -2, -3 suffix.
"""

import argparse
import json
import sys

from analyse_cvs.app.slugs import make_slugs


def main(argv: list[str] | None = None) -> int:
    """Run the slug command and return the exit code."""
    parser = argparse.ArgumentParser(
        prog="cvs-slug",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("names", nargs="+", help="role or candidate names")
    parser.add_argument("--existing", default="", help="comma-separated slugs that are already taken")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    try:
        slugs = make_slugs(args.names, [s.strip() for s in args.existing.split(",") if s.strip()])
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([{"name": n, "slug": s} for n, s in zip(args.names, slugs, strict=True)], ensure_ascii=False))
    else:
        print("\n".join(slugs))
    return 0
