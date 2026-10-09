"""'How far to trust' section: per-account data quality, announced coverage gaps and fixed disclosures."""

from portfolio_manager.app import concepts
from portfolio_manager.app.fmt import cell, table

DISCLOSURES = (
    "Flows of snapshot and value-only accounts are estimated at the middle of each statement period.",
    "An account that starts being tracked later enters the portfolio as an inflow of its first value.",
    "Realized P&L is partial when the cost basis of a sale is unknown.",
    "Gains of non-EUR accounts include the effect of the exchange rate.",
)


def _status(finding: dict) -> str:
    given = finding["accepted"]
    return f'accepted: {given["reason"]} "{given["note"]}"' if given else "open"


def _finding_text(findings: list) -> str:
    return "; ".join(f"{f['label']} {_status(f)}" for f in findings) or "none"


def _portfolio_wide(check: dict) -> list:
    """Findings that belong to no single account (overlaps, scope, expected start) with the user's answer."""
    mine = [f for f in check["findings"] if not f["account"]]
    lines = [cell("- " + f"{f['kind']} ({f['message']}): {_status(f)}") for f in mine]
    return [*lines, ""] if lines else []


def _warnings(analysis: dict, account: str) -> str:
    mine = [c for c in analysis["checks"] if c["account"] == account and c["level"] != "ok"]
    return f"{len(mine)} warn/fail" if mine else "none"


def late_starters(analysis: dict) -> list:
    first = (analysis["portfolio"] or {}).get("first")
    return [k for k, a in sorted(analysis["accounts"].items()) if first and a["first"] > first]


def section(analysis: dict, check: dict | None) -> list:
    found = (check or {}).get("findings", [])
    rows = [
        [
            k,
            a["account"]["mode"],
            "exact" if a["flows_status"] == "complete" else "estimated",
            a["last"],
            _finding_text([f for f in found if f["account"] == k]),
            _warnings(analysis, k),
        ]
        for k, a in sorted(analysis["accounts"].items())
    ]
    counts = analysis["check_counts"]
    out = [
        f"## How far to trust ({concepts.link('trust')})",
        "",
        "<details>",
        f"<summary>Data quality per investment account and coverage findings ({counts['warn'] + counts['fail']} warn/fail checks)</summary>",
        "",
    ]
    out += table(
        ["Investment account", "Mode", "Flows", "Latest date", "Coverage findings (user status)", "Warnings"], rows
    )
    if check is None:
        out += ["Coverage was not checked in this run (`pm check-input`).", ""]
    else:
        out += [f"Coverage start expected by the user: {cell(check['expected_start'] or 'not given')}.", ""]
        out += _portfolio_wide(check)
    late = late_starters(analysis)
    out += [f"- {d}" for d in DISCLOSURES]
    if late:
        out.append(f"- Late start in this data set: {', '.join(late)}.")
    return [*out, "", "</details>", ""]
