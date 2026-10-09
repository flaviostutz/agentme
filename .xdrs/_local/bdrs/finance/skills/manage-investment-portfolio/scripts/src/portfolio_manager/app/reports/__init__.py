"""Report set: renders every report and graph from the analysis. portfolio.md is the entry and every page links to all others."""

from portfolio_manager.app import concepts
from portfolio_manager.app.fmt import money, pct
from portfolio_manager.app.reports import graphs
from portfolio_manager.app.reports.common import Ctx, header
from portfolio_manager.app.reports.income import income_report
from portfolio_manager.app.reports.investment_accounts import investment_accounts_report
from portfolio_manager.app.reports.markets import markets_report
from portfolio_manager.app.reports.periodic import monthly_report, yearly_report
from portfolio_manager.app.reports.portfolio import portfolio_report
from portfolio_manager.app.reports.risk import risk_report
from portfolio_manager.app.reports.securities import securities_report


def concepts_report(ctx: Ctx) -> str:
    return concepts.render(header("Concepts", "concepts", ctx, legend=True)[2:])


def render(analysis: dict, unresolved: list, known: list, check: dict | None = None) -> dict:
    """Return {relative path: text} for every report and graph."""
    charts = graphs.build(analysis)
    ctx = Ctx(analysis, unresolved, known, check, charts)
    files = {
        "reports/portfolio.md": portfolio_report(ctx),
        "reports/monthly.md": monthly_report(ctx),
        "reports/yearly.md": yearly_report(ctx),
        "reports/investment-accounts.md": investment_accounts_report(ctx),
        "reports/securities.md": securities_report(ctx),
        "reports/income.md": income_report(ctx),
        "reports/risk.md": risk_report(ctx),
        "reports/concepts.md": concepts_report(ctx),
    }
    if known:
        files["reports/markets.md"] = markets_report(ctx)
    files.update({f"graphs/{name}": text for name, text in charts.items()})
    return files


def summary(analysis: dict, unresolved: list, written: int, root: str) -> list:
    """Short script-generated summary for the agent to relay (kept under 150 words)."""
    pf = analysis["portfolio"]
    lines = [f"Wrote {written} report/graph file(s). Unresolved records: {len(unresolved)}."]
    if pf:
        inc = next((p for p in pf["periods"] if p["label"] == "inception"), None)
        lines.append(
            f"Wealth {money(pf['value_eur'])} EUR on {pf['common_date']}"
            + (f"; TWR since inception {pct(inc['twr'], inc['twr_status'])}." if inc else ".")
        )
    c = analysis["check_counts"]
    lines.append(f"Checks: {c['ok']} ok, {c['warn']} warn, {c['fail']} fail. Start with {root}reports/portfolio.md.")
    return lines
