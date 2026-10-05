"""Report footers: links to the concepts a report uses plus short notes built from that report's own numbers.

Every note is a template with a conditional trigger, so a hint is only printed when the numbers support it.
"""

from decimal import Decimal

from portfolio_manager.app import concepts
from portfolio_manager.app.fmt import money, pct

MAX_NOTE_WORDS = 40
TEMPLATES = {
    "partial": "{label} covers {first_day} .. {to} only; do not compare it with a full period.",
    "xirr_above": (
        "{label}: XIRR (actual) {xirr} is above TWR (natural) {twr}, so the money you added before gains "
        "worked better than the assets alone."
    ),
    "xirr_below": (
        "{label}: XIRR (actual) {xirr} is below TWR (natural) {twr}, so money added before weaker days "
        "cost you part of the assets' own result."
    ),
    "unavailable": "{n} of {m} rows have no TWR (natural); n/a means a valuation is missing, not a zero return.",
    "deposits_led": "{share} % of the wealth change since inception came from your deposits, not from markets.",
    "costs_exceed_income": "Fees and taxes ({fees} EUR) were larger than dividends and interest ({income} EUR).",
    "observation": "{account} was last observed on {last}; {n} of {m} period-end values are interpolated (~).",
    "fx": "{account}: the exchange rate moved your EUR result by {fx} EUR since inception.",
}


def _dec(v) -> Decimal | None:
    return None if v is None else Decimal(v)


def period_notes(rows: list) -> list:
    """Hints for a list of period rows (dicts from the analysis)."""
    out = [
        TEMPLATES["partial"].format(label=r["label"], first_day=r["first_day"], to=r["to"])
        for r in rows
        if r.get("partial")
    ]
    inception = next((r for r in rows if r["label"] == "inception"), None)
    x, t = (_dec(inception["xirr"]), _dec(inception["twr"])) if inception else (None, None)
    if inception and x is not None and t is not None and x != t:
        key = "xirr_above" if x > t else "xirr_below"
        out.append(
            TEMPLATES[key].format(
                label="inception",
                xirr=pct(x, inception["xirr_status"]),
                twr=pct(t, inception["twr_status"]),
            )
        )
    missing = sum(r["twr"] is None for r in rows)
    if missing:
        out.append(TEMPLATES["unavailable"].format(n=missing, m=len(rows)))
    return out


def observation_notes(analysis: dict) -> list:
    """One note per account: last real observation and how many period-end values are interpolated."""
    out = []
    for k, a in sorted(analysis["accounts"].items()):
        ends = [p for p in a["periods"] if p["label"].startswith("month ")] or a["periods"]
        estimated = sum(p["end_status"] != "complete" for p in ends)
        out.append(TEMPLATES["observation"].format(account=k, last=a["last"], n=estimated, m=len(ends)))
    return out


def portfolio_notes(analysis: dict) -> list:
    pf = analysis["portfolio"]
    out = period_notes(pf["periods"]) if pf else []
    inception = next((p for p in (pf or {}).get("periods", []) if p["label"] == "inception"), None)
    if inception and inception["gain"] is not None and inception["start_value"] is not None:
        change = Decimal(inception["end_value"]) - Decimal(inception["start_value"])
        flows = Decimal(inception["net_flows"])
        if change > 0 and flows / change > Decimal("0.5"):
            out.append(TEMPLATES["deposits_led"].format(share=f"{100 * flows / change:.0f}"))
    income = fees = Decimal(0)
    for a in analysis["accounts"].values():
        acc = a["accounting"]
        if acc is not None and acc["currency"] == "EUR":
            income += Decimal(acc["income"]["dividends"]) + Decimal(acc["income"]["interest"])
            fees += Decimal(acc["income"]["fees"]) + Decimal(acc["income"]["taxes"])
    if fees > income > 0 or (fees > 0 and income == 0):
        out.append(TEMPLATES["costs_exceed_income"].format(fees=money(fees), income=money(income)))
    return out


def fx_notes(analysis: dict) -> list:
    out = []
    for k, a in sorted(analysis["accounts"].items()):
        inception = next((p for p in a["periods"] if p["label"] == "inception"), None)
        if a["account"]["currency"] != "EUR" and inception and inception.get("fx_effect") is not None:
            out.append(TEMPLATES["fx"].format(account=k, fx=money(inception["fx_effect"])))
    return out


def footer(keys: list, notes: list, analysis: dict | None = None) -> list:
    """Markdown footer: concept links, then notes; with an analysis it also lists the observation dates."""
    lines = ["## Notes", "", "Concepts used: " + ", ".join(concepts.link(k) for k in keys) + ".", ""]
    all_notes = [*notes, *(observation_notes(analysis) if analysis else [])]
    return [*lines, *(f"- {n}" for n in all_notes), ""] if all_notes else lines
