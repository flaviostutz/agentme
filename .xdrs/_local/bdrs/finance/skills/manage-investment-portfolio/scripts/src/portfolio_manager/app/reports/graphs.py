"""Graph files: Mermaid line, bar and pie charts plus the SVG wealth bridge and quadrants. Unavailable months are left out, never drawn as 0."""

from decimal import Decimal

from portfolio_manager.app import svgchart
from portfolio_manager.app.reports.common import (
    MONTH_LIMIT,
    TOP_PIE,
    dec,
    is_month,
    is_year,
    scope_slugs,
    select_rows,
)

LINE, BAR = "line", "bar"


def _clean(text: str) -> str:
    """Names go inside Mermaid double quotes: no quotes, one line."""
    return " ".join(str(text).replace('"', "'").split())


def xychart(title: str, labels: list, series: list, y: str) -> str:
    """series: [(kind, [value string])]; every series has one value per label."""
    names = ", ".join(f'"{_clean(lbl)}"' for lbl in labels)
    lines = ["xychart-beta", f'    title "{_clean(title)}"', f"    x-axis [{names}]", f'    y-axis "{y}"']
    lines += [f"    {kind} [{', '.join(values)}]" for kind, values in series]
    return "\n".join([*lines, ""])


def _pct(value) -> str:
    return f"{Decimal(value) * 100:.2f}"


def _eur(value) -> str:
    return f"{Decimal(value):.2f}"


def pie_rows(analysis: dict) -> tuple:
    """(rows [(name, Decimal)], negatives excluded, title): top open positions plus Others, else wealth by account."""
    rows = [(r["name"], Decimal(r["value_eur"])) for r in (analysis.get("positions") or {}).get("rows", [])]
    positive = [r for r in rows if r[1] > 0]
    if positive:
        top = positive[:TOP_PIE]
        rest = sum((v for _, v in positive[TOP_PIE:]), Decimal(0))
        if rest > 0:
            top.append(("Others", rest))
        return top, len(rows) - len(positive), "Open positions (EUR, share of the largest)"
    pf = analysis["portfolio"]
    accounts = [(a["account"], Decimal(a["value_eur"])) for a in pf["accounts"] if a["value_eur"] is not None]
    positive = [r for r in accounts if r[1] > 0]
    return positive, len(accounts) - len(positive), "Wealth by account (EUR, latest valuations)"


def _pie(analysis: dict) -> str | None:
    rows, _neg, title = pie_rows(analysis)
    if not rows:
        return None
    return "\n".join(["pie showData", f'    title "{title}"', *[f'    "{_clean(k)}" : {v:.2f}' for k, v in rows], ""])


def _account_pie(analysis: dict) -> str | None:
    """Share of the latest wealth per investment account (negative or unknown values are left out)."""
    accounts = [
        (a["account"], Decimal(a["value_eur"])) for a in analysis["portfolio"]["accounts"] if a["value_eur"] is not None
    ]
    rows = [r for r in accounts if r[1] > 0]
    if not rows:
        return None
    title = "Wealth by investment account (EUR, latest valuations)"
    return "\n".join(["pie showData", f'    title "{title}"', *[f'    "{_clean(k)}" : {v:.2f}' for k, v in rows], ""])


def _trend_charts(analysis: dict) -> dict:
    """Cumulative TWR, XIRR and net flows of the last 12 months; only drawn when that window is a full 12 months."""
    out = {}
    rows = analysis.get("trend") or []
    if not (analysis.get("window") or {}).get("full"):
        return out
    twr = [r for r in rows if r["twr"] is not None and r["twr_status"] == "complete"]
    if twr:
        out["twr-12m.mmd"] = xychart(
            "Cumulative TWR (12 months)",
            [r["date"][:7] for r in twr],
            [(LINE, [_pct(r["twr"]) for r in twr])],
            "%",
        )
    xirr = [r for r in rows if r["xirr"] is not None and r["xirr_status"] == "complete"]
    if xirr:
        out["xirr-12m.mmd"] = xychart(
            "Cumulative XIRR (12 months)",
            [r["date"][:7] for r in xirr],
            [(LINE, [_pct(r["xirr"]) for r in xirr])],
            "%",
        )
    flows, previous = [], Decimal(0)
    for r in rows:
        if r["net_flows"] is None:
            continue
        flows.append((r["date"][:7], Decimal(r["net_flows"]) - previous))
        previous = Decimal(r["net_flows"])
    if flows:
        out["net-flows-12m.mmd"] = xychart(
            "Net flows per month in the window (EUR)",
            [m for m, _ in flows],
            [(LINE, [f"{v:.2f}" for _, v in flows])],
            "EUR",
        )
    return out


def _xirr_line(file: str, title: str, rows: list, label) -> dict:
    """XIRR of each row as a line; partial rows and rows without XIRR are skipped and fewer than 2 points draws nothing."""
    points = [(label(r), r["xirr"]) for r in rows if not r["partial"] and r["xirr"] is not None]
    if len(points) < 2:
        return {}
    return {f"{file}.mmd": xychart(title, [x for x, _ in points], [(LINE, [_pct(v) for _, v in points])], "%")}


def _periodic_charts(analysis: dict) -> dict:
    """monthly-xirr-<scope>.mmd (latest months) and yearly-xirr-<scope>.mmd for the portfolio and each account."""
    slugs = scope_slugs(analysis["accounts"])
    scopes = [("portfolio", "portfolio", analysis["portfolio"]["periods"])]
    scopes += [(slugs[k], k, a["periods"]) for k, a in sorted(analysis["accounts"].items())]
    out = {}
    for slug, name, periods in scopes:
        months = select_rows(periods, is_month, MONTH_LIMIT)
        out.update(_xirr_line(f"monthly-xirr-{slug}", f"XIRR per month, {name} (%)", months, lambda r: r["to"][:7]))
        years = select_rows(periods, is_year)
        out.update(_xirr_line(f"yearly-xirr-{slug}", f"XIRR per year, {name} (%)", years, lambda r: r["label"][5:]))
    return out


def _risk_charts(analysis: dict) -> dict:
    """CAGR per calendar year plus the volatility vs CAGR quadrants (a quadrant needs both measures)."""
    risk = analysis.get("risk") or {}
    out = {}
    years = risk.get("yearly") or []
    if len(years) >= 2:
        out["cagr-per-year.mmd"] = xychart(
            "CAGR per calendar year (%)",
            [y["year"] for y in years],
            [(LINE, [_pct(y["twr"]) for y in years])],
            "%",
        )
    last = risk.get("last_12m") or {}
    for name, title, r in (
        ("quadrant-inception.svg", "Volatility vs CAGR, from inception", risk),
        ("quadrant-12m.svg", "Volatility vs CAGR, last 12 months", last),
    ):
        if r.get("volatility") is not None and r.get("cagr") is not None:
            out[name] = svgchart.quadrant(title, Decimal(r["volatility"]), Decimal(r["cagr"]))
    return out


def _benchmark_chart(analysis: dict) -> dict:
    b = analysis.get("benchmark") or {}
    rows = [r for r in b.get("rows", []) if r["twr"] is not None and r["benchmark"] is not None]
    if b.get("state") != "ok" or not rows:
        return {}
    title = f"Portfolio TWR (first line) vs {b['ticker']} in EUR (second line), %"
    series = [(LINE, [_pct(r["twr"]) for r in rows]), (LINE, [_pct(r["benchmark"]) for r in rows])]
    return {"benchmark.mmd": xychart(title, [r["date"][:7] for r in rows], series, "%")}


def _income_chart(analysis: dict) -> dict:
    months = (analysis.get("income") or {}).get("months") or {}
    totals = [(m, Decimal(v["dividends"]) + Decimal(v["interest"])) for m, v in months.items()]
    if not any(v > 0 for _, v in totals):
        return {}
    return {
        "income.mmd": xychart(
            "Dividends and interest per month (EUR)",
            [m for m, _ in totals],
            [(BAR, [f"{v:.2f}" for _, v in totals])],
            "EUR",
        )
    }


def build(analysis: dict) -> dict:
    """{file name: text} for graphs/ (Mermaid .mmd and the SVG bridge)."""
    pf = analysis.get("portfolio")
    if not pf:
        return {}
    out = {}
    months = [p for p in pf["periods"] if p["label"].startswith("month ") and p["end_value"] is not None]
    if months:
        out["wealth.mmd"] = xychart(
            "Wealth since inception (EUR, month end)",
            [p["to"] for p in months],
            [(LINE, [_eur(p["end_value"]) for p in months])],
            "EUR",
        )
    out.update(_trend_charts(analysis))
    out.update(_benchmark_chart(analysis))
    out.update(_income_chart(analysis))
    drawdown = (analysis.get("risk") or {}).get("drawdown") or []
    if drawdown:
        out["drawdown.mmd"] = xychart(
            "Drawdown from the previous peak (%)",
            [d["date"][:7] for d in drawdown],
            [(LINE, [_pct(d["drawdown"]) for d in drawdown])],
            "%",
        )
    pie = _pie(analysis)
    if pie:
        out["allocation.mmd"] = pie
    account_pie = _account_pie(analysis)
    if account_pie:
        out["wealth-by-account.mmd"] = account_pie
    out.update(_periodic_charts(analysis))
    out.update(_risk_charts(analysis))
    bridge = analysis.get("bridge")
    if bridge:
        steps = [(s["label"], dec(s["amount"]), s["kind"]) for s in bridge["steps"]]
        out["wealth-bridge.svg"] = svgchart.waterfall(f"Wealth bridge {bridge['from']} to {bridge['to']} (EUR)", steps)
    return out
