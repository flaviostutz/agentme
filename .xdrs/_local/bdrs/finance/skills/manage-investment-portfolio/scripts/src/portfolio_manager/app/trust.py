"""'How far to trust' section: per-account data quality, announced coverage gaps and fixed disclosures."""

from portfolio_manager.app.fmt import table

DISCLOSURES = (
    "Flows of snapshot and value-only accounts are estimated at the middle of each statement period.",
    "An account that starts being tracked later enters the portfolio as an inflow of its first value.",
    "Realized P&L is partial when the cost basis of a sale is unknown.",
    "Gains of non-EUR accounts include the effect of the exchange rate.",
)


def _gap_text(gaps: list) -> str:
    if not gaps:
        return "none"
    return "; ".join(
        f"{g['start']}..{g['end']} " + (f"accepted: {g['note']}" if g.get("note") else "unconfirmed") for g in gaps
    )


def _warnings(analysis: dict, account: str) -> str:
    mine = [c for c in analysis["checks"] if c["account"] == account and c["level"] != "ok"]
    return f"{len(mine)} warn/fail" if mine else "none"


def late_starters(analysis: dict) -> list:
    first = (analysis["portfolio"] or {}).get("first")
    return [k for k, a in sorted(analysis["accounts"].items()) if first and a["first"] > first]


def section(analysis: dict, check: dict | None) -> list:
    gaps = (check or {}).get("gaps", [])
    rows = [
        [
            k,
            a["account"]["mode"],
            "exact" if a["flows_status"] == "complete" else "estimated",
            a["last"],
            _gap_text([g for g in gaps if g["account"] == k]),
            _warnings(analysis, k),
        ]
        for k, a in sorted(analysis["accounts"].items())
    ]
    out = ["## How far to trust", ""]
    out += table(["Account", "Mode", "Flows", "Latest date", "Coverage gaps (user status)", "Warnings"], rows)
    if check is None:
        out += ["Coverage was not checked in this run (`pm check-input`).", ""]
    else:
        open_gaps = sum(1 for g in gaps if not g.get("note"))
        out += [f"Detected coverage gaps: {len(gaps)} ({open_gaps} unconfirmed).", ""]
    late = late_starters(analysis)
    out += [f"- {d}" for d in DISCLOSURES]
    if late:
        out.append(f"- Late start in this data set: {', '.join(late)}.")
    return [*out, ""]
