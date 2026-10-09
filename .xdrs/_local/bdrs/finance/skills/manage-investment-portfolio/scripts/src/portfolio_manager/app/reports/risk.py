"""risk.md: CAGR, volatility, best and worst month, drawdown and the volatility vs CAGR quadrant, from inception and for the last 12 months."""

from decimal import Decimal

from portfolio_manager.app import quadrant
from portfolio_manager.app.fmt import pct, table
from portfolio_manager.app.reports.common import Ctx, embed, h2, header

SOURCES = (
    "[Visual Capitalist](https://www.visualcapitalist.com/charted-asset-class-returns-across-eras-1990-2025/), "
    "[Trustybull](https://www.trustybull.com/explain/en/asset-allocation/volatility-different-asset-classes)"
)


def _rows(r: dict) -> list:
    status = r["status"]
    best, worst = r["best"], r["worst"]
    return [
        ["CAGR (annualised TWR)", pct(r["cagr"], status) if r["cagr"] is not None else r["cagr_reason"]],
        [
            "Volatility (annual)",
            pct(r["volatility"], status) if r["volatility"] is not None else r["volatility_reason"],
        ],
        ["Best month", f"{best['label']}: {pct(best['twr'], best['status'])}" if best else "n/a (no complete month)"],
        [
            "Worst month",
            f"{worst['label']}: {pct(worst['twr'], worst['status'])}" if worst else "n/a (no complete month)",
        ],
        [
            "Maximum drawdown",
            f"{pct(r['max_drawdown'], status)} ({r['max_drawdown_date']})" if r["max_drawdown"] is not None else "n/a",
        ],
    ]


def _quadrant(ctx: Ctx, r: dict, svg: str) -> list:
    """The quadrant picture with the classification, or why there is none."""
    if r["volatility"] is None or r["cagr"] is None or f"{svg}.svg" not in ctx.charts:
        why = "; ".join(x for x in (r["volatility_reason"], r["cagr_reason"]) if x)
        return [f"_No volatility vs CAGR quadrant: {why}._", ""]
    q = quadrant.classify(Decimal(r["volatility"]), Decimal(r["cagr"]))
    alt = (
        f"Volatility vs CAGR quadrant: {q.name}, CAGR {Decimal(r['cagr']) * 100:.1f} %, "
        f"volatility {Decimal(r['volatility']) * 100:.1f} %"
    )
    return [
        f"![{alt}](../graphs/{svg}.svg)",
        "",
        f"Classification: **{q.name}** ({q.profile}). {q.description} Investor match: {q.investor}",
        "",
    ]


def _inception(ctx: Ctx, r: dict) -> list:
    out = h2("From inception", "cagr", "volatility", "best-worst-month", "drawdown")
    out += [f"Based on {r['months']} complete month(s) of portfolio TWR; partial months are left out.", ""]
    out += [*table(["Measure", "Value"], _rows(r)), *_quadrant(ctx, r, "quadrant-inception")]
    per_year = embed(ctx, "cagr-per-year")
    out += [
        "### CAGR per year",
        "",
        *(per_year or ["_Needs at least two full calendar years (each starting on 1 January)._", ""]),
    ]
    drawdown = embed(ctx, "drawdown")
    return [*out, *(["### Drawdown", "", *drawdown] if drawdown else [])]


def _last_12_months(ctx: Ctx, r: dict) -> list:
    out = h2("Last 12 months", "cagr", "volatility", "best-worst-month", "drawdown")
    if not r["available"]:
        return [*out, f"_Needs the latest 12 consecutive complete calendar months: {r['reason']}._", ""]
    out += [f"Based on the 12 complete calendar months from {r['from']} to {r['to']}.", ""]
    return [*out, *table(["Measure", "Value"], _rows(r)), *_quadrant(ctx, r, "quadrant-12m")]


def _reading() -> list:
    return [
        *h2("How to read the quadrant"),
        (
            "Volatility of 12 % or more and CAGR of 8 % or more count as high. The dashed grey boxes show typical "
            "ranges of asset types (cash and short bonds, bond indexes and dividend stocks, broad equities, "
            "emerging markets, tech and crypto), not your holdings. The axes are not linear: each band between the "
            "ticks has the same width. The ranges are an approximate guide from "
            f"{SOURCES}."
        ),
        "",
    ]


def risk_report(ctx: Ctx) -> str:
    r = ctx.analysis.get("risk")
    out = header("Risk", "risk", ctx)
    if not r:
        return "\n".join([*out, "_No risk figures yet: no valued investment accounts._", ""])
    return "\n".join([*out, *_inception(ctx, r), *_last_12_months(ctx, r["last_12m"]), *_reading()])
