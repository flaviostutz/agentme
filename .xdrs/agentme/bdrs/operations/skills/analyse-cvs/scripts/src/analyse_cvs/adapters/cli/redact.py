"""Redact labelled protected attributes and all images from a converted CV markdown file, in place.

Labels are matched in EN, NL, PT, DE, FR and ES. Free-text mentions are left for the agent pass.
Name, work permit/visa, location, languages and employment/education dates are never touched.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_cvs.app.redaction import redact


def main(argv: list[str] | None = None) -> int:
    """Run the redact command and return the exit code."""
    parser = argparse.ArgumentParser(prog="cvs-redact", description=__doc__)
    parser.add_argument("file", help="markdown file to redact in place")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    original = path.read_text(encoding="utf-8")
    redacted, counts = redact(original)
    if redacted != original:
        path.write_text(redacted, encoding="utf-8")

    total = sum(counts.values())
    if args.json:
        print(json.dumps({"file": str(path), "redactions": counts, "total": total}, indent=2))
    else:
        details = ", ".join(f"{k}={v}" for k, v in counts.items() if v)
        print(f"{path}: {total} redaction(s){' (' + details + ')' if details else ''}")
    return 0
