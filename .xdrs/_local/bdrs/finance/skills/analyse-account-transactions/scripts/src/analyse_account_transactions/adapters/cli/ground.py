"""Ground a normalized file against its source: every row's date and amount must appear in the source.

  aat-ground <normalized.md> [--sample N] [--json]
Matching is one-to-one (identical rows need identical source entries): first the same line, then a date up to
DATE_SLACK days later (booking after purchase) or an amount up to two lines below the date. Numeric dates such as
03-01-2026 are read in the day/month order of the source's unambiguous dates, or both ways when mixed. Also reports
source-only lines (date + amount but no row), the balance chain and the institution module check, and writes
<stem>.grounding.json. Exit codes: 0 grounded, 1 unmatched rows or failed checks, 2 invalid input.
Image transcriptions (normalizer: llm-image) cannot be grounded: all rows are reported as unverified, exit 0.
"""

import argparse
import json
import sys
from pathlib import Path

from analyse_account_transactions.adapters.connectors.institutions import default_registry
from analyse_account_transactions.adapters.connectors.local_fs.workspace import LocalWorkspace
from analyse_account_transactions.adapters.connectors.sources.sourcedoc import LocalSources
from analyse_account_transactions.app import ground
from analyse_account_transactions.shared.errors import LedgerError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="aat-ground",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file", help="normalized file inside .tmp/")
    parser.add_argument("--sample", type=int, default=ground.DEFAULT_SAMPLE, help="matched rows to spot-check")
    parser.add_argument("--json", action="store_true", help="print the full JSON result")
    args = parser.parse_args(argv)
    store = LocalWorkspace(Path.cwd())
    try:
        path = store.resolve_tmp(args.file)
        result = ground.ground(store, LocalSources(), default_registry(), path, max(0, args.sample))
    except (LedgerError, OSError, KeyError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    except Exception as err:  # noqa: BLE001 - third-party parsers raise many types for corrupt files
        print(f"error: cannot read the source of {args.file}: {type(err).__name__}: {err}", file=sys.stderr)
        return 2
    out = ground.write_grounding(store, path, result)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(
            f"{result['file']}: {result.get('matched', 0)}/{result['rows']} rows grounded"
            f", {len(result.get('unmatched', []))} unmatched, {len(result.get('source-only', []))} source-only"
            f" lines, balance {result.get('balance-chain', {}).get('ok')}"
            f", module check {[f['check'] for f in result.get('module-check', []) if not f.get('ok')] or 'ok'}"
            f" -> {out.name}" + (f"; {result['warning']}" if "warning" in result else ""),
        )
    return result["exit"]


if __name__ == "__main__":
    sys.exit(main())
