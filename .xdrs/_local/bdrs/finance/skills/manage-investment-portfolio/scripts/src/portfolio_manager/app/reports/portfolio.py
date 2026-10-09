"""portfolio.md: the main entry with the 12-month overview first and the full-history detail below."""

from decimal import Decimal

from portfolio_manager.app import notes, trust
from portfolio_manager.app.fmt import money, pct, table
from portfolio_manager.app.reports import graphs
from portfolio_manager.app.reports.common import (
    PERIOD_HEAD,
    Ctx,
    embed,
    h2,
    header,
    is_window,
    period_rows,
    window_row,
)

TOP = 10


def _wealth(ctx: Ctx) -> list:
    a, pf = ctx.analysis, ctx.analysis["portfolio"]
    out = h2("Wealth", "wealth", "investment-account", "cash-positions")
    out += [
        (
            f"Consolidated wealth **{money(pf['value_eur'])} EUR** at {pf['common_date']} (latest date where every tracked "
            f"investment account has a valuation; status {pf['value_status']})."
        ),
        "",
        *embed(ctx, "wealth"),
    ]
    values = [Decimal(x["value_eur"]) for x in pf["accounts"] if x["value_eur"] is not None]
    total = sum(values, Decimal(0))
    rows = []
    for x in pf["accounts"]:
        win = window_row(a["accounts"][x["account"]]["periods"])
        share = f"{100 * Decimal(x['value_eur']) / total:.1f} %" if x["value_eur"] is not None and total else "n/a"
        rows.append(
            [
                x["account"],
                x["last"],
                money(x["cash_eur"]),
                money(x["positions_eur"]),
                money(x["value_eur"]),
                share,
                pct(win["twr"], win["twr_status"]) if win else "n/a",
                pct(win["xirr"], win["xirr_status"]) if win else "n/a",
            ]
        )
    out += table(
        [
            "Investment account",
            "Latest date",
            "Cash (EUR)",
            "Positions (EUR)",
            "Wealth (EUR)",
            "Share",
            "TWR 12m",
            "XIRR 12m",
        ],
        rows,
    )
    out += [f"Sum of the latest value per account: {money(total)} EUR (mixed dates, not a consolidated figure).", ""]
    return out


def _returns(ctx: Ctx) -> list:
    win = ctx.analysis.get("window")
    if not win:
        return []
    out = h2(f"Returns, {win['label']}, {win['from']} .. {win['to']}", "last-12-months", "twr", "xirr", "net-flows")
    out += table(PERIOD_HEAD, period_rows(ctx.analysis["portfolio"]["periods"], is_window))
    charts = [c for name in ("twr-12m", "xirr-12m", "net-flows-12m") for c in embed(ctx, name)]
    if charts:
        return [*out, *charts]
    why = (
        "_No complete month-end inside the window yet, so there is nothing to chart._"
        if win["full"]
        else "_The history is shorter than 12 months, so the 12-month charts are not drawn._"
    )
    return [*out, why, ""]


def _bridge(ctx: Ctx) -> list:
    br = ctx.analysis.get("bridge")
    if not br:
        return []
    alt = (
        f"Wealth bridge from {br['from']} to {br['to']}: start, money added, income, fees and taxes, "
        "FX effect, market and other, end"
    )
    out = h2("Wealth bridge, last 12 months", "wealth-bridge", "fx-effect", "dividends-interest")
    out += [f"![{alt}](../graphs/wealth-bridge.svg)", ""]
    out += table(["Step", "EUR"], [[s["label"], money(s["amount"])] for s in br["steps"]])
    out += [
        (
            "Income, fees and taxes come from investment accounts with transactions; "
            f"market and other is the remainder (status {br['status']})."
        ),
        "",
    ]
    return out


def _position_row(i: int, r: dict) -> list:
    name = f"{r['name']}{'~' if r['no_isin'] else ''}: {money(r['value_eur'])}"
    return [
        i,
        name,
        r["as_of"],
        pct(r["weight"], "complete"),
        pct(r["pnl_pct"], "complete" if r["pnl_pct"] is not None else "unavailable"),
        ", ".join(r["accounts"]),
    ]


def _top_positions(ctx: Ctx) -> list:
    out = h2(f"Top {TOP} open positions", "security", "weight", "unrealized-pl")
    rows = (ctx.analysis.get("positions") or {}).get("rows", [])
    if not rows:
        return [*out, "_No open positions._", ""]
    out += embed(ctx, "allocation")
    out += table(
        ["#", "Security: value (EUR)", "Latest date", "Weight", "P&L %", "Investment accounts"],
        [_position_row(i, r) for i, r in enumerate(rows[:TOP], 1)],
    )
    if any(r["no_isin"] for r in rows[:TOP]):
        out += ["`~` after a name: no ISIN, so the same security in two accounts is listed twice.", ""]
    _rows, negatives, _title = graphs.pie_rows(ctx.analysis)
    if negatives:
        out += ["Negative positions are left out of the chart.", ""]
    return out


def _benchmark(ctx: Ctx) -> list:
    b: dict = ctx.analysis.get("benchmark") or {"state": "not-configured"}
    out = h2("Benchmark", "benchmark", "twr")
    if b["state"] == "not-configured":
        return [*out, "_No benchmark configured. Run `pm benchmark --ticker <ticker>` (e.g. IWDA.AS) to compare._", ""]
    if b["state"] == "no-data":
        return [*out, f"_No saved prices for {b['ticker']}. Run `pm benchmark --ticker {b['ticker']}`._", ""]
    rows = [r for r in b["rows"] if r["twr"] is not None and r["benchmark"] is not None]
    out += embed(ctx, "benchmark")
    out += table(
        ["Date", "Portfolio TWR", f"{b['ticker']} in EUR"],
        [[r["date"], pct(r["twr"]), pct(r["benchmark"], "approximate")] for r in rows],
    )
    return [
        *out,
        f"Prices come from Yahoo Finance ({b['ticker']}, {b['currency']}); month closes, converted to EUR (approximate).",
        "",
    ]


def _performance_label(label: str) -> bool:
    return label == "inception" or is_window(label) or label.startswith("year")


def _performance(ctx: Ctx) -> list:
    pf = ctx.analysis["portfolio"]
    out = h2("Performance", "twr", "xirr", "period-return", "partial-period")
    return [*out, *table(PERIOD_HEAD, period_rows(pf["periods"], _performance_label))]


def _quality(analysis: dict) -> list:
    pf = analysis["portfolio"]
    out = h2("Data quality", "status", "reconciliation")
    statuses = [p["twr_status"] for p in pf["periods"]]
    total = max(len(statuses), 1)
    out += [
        (
            f"- Performance metrics: {statuses.count('complete')} complete, {sum(s in ('approximate', 'interpolated') for s in statuses)} approximate, "
            f"{statuses.count('unavailable')} unavailable ({100 * statuses.count('complete') // total} % complete)."
        ),
        (
            "- Investment accounts with a statement valuation on the common date: "
            f"{sum(1 for a in pf['accounts'] if a['last'] == pf['common_date'])} of {len(pf['accounts'])}."
        ),
    ]
    out += [f"- Excluded from the consolidation: {e['account']} ({e['reason']})." for e in analysis["excluded"]]
    out += [f"- {e}" for e in analysis["errors"]]
    out += [
        f"- Check {c['level']}: {c['account']} {c['name']} (expected {c['expected']}, actual {c['actual']})"
        for c in analysis["checks"]
        if c["level"] != "ok"
    ]
    if analysis.get("fx_notice"):
        out.append(f"- FX: {analysis['fx_notice']}")
    return [*out, ""]


def _costs(analysis: dict) -> list:
    if not analysis["cost_reports"]:
        return []
    rows = [
        [c["account"], f"{c['from']} .. {c['to']}", money(c["total_cost"]), f"{c['cost_pct']} %"]
        for c in analysis["cost_reports"]
    ]
    return [
        *h2("Reported costs", "fees-taxes"),
        *table(["Investment account", "Period", "Total cost", "Of average value"], rows),
    ]


def portfolio_report(ctx: Ctx) -> str:
    a = ctx.analysis
    out = header("Portfolio report", "portfolio", ctx, legend=True)
    if not a["portfolio"]:
        return "\n".join([*out, "_No valued investment accounts yet._", ""])
    out += [*_wealth(ctx), *_returns(ctx), *_bridge(ctx), *_top_positions(ctx), *_benchmark(ctx), *_performance(ctx)]
    out += [*trust.section(a, ctx.check), *_costs(a), *_quality(a)]
    found = [*notes.portfolio_notes(a), *notes.overview_notes(a), *notes.fx_notes(a)]
    return "\n".join([*out, *notes.section(found, a)])
