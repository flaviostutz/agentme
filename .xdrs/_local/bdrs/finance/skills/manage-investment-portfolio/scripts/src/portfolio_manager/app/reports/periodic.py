"""monthly.md and yearly.md: period tables and an XIRR line chart for the portfolio and for each investment account."""

from portfolio_manager.app import notes
from portfolio_manager.app.fmt import table
from portfolio_manager.app.reports.common import (
    MONTH_LIMIT,
    PERIOD_HEAD,
    Ctx,
    embed,
    h2,
    header,
    is_month,
    is_window,
    is_year,
    period_rows,
    scope_slugs,
    select_rows,
)


def _is_yearly(label: str) -> bool:
    return is_year(label) or label == "inception" or is_window(label)


def periodic_report(ctx: Ctx, key: str, title: str) -> str:
    monthly = key == "monthly"
    labels, limit = (is_month, MONTH_LIMIT) if monthly else (_is_yearly, None)
    a = ctx.analysis
    slugs = scope_slugs(a["accounts"])
    out = header(title, key, ctx)
    if monthly:
        out += [
            f"Shows the latest {MONTH_LIMIT} months; each row has its own window for TWR, XIRR and period return.",
            "",
        ]
    shown = []
    pf = a["portfolio"]
    if pf:
        out += [
            *h2("Portfolio", "twr", "xirr", "period-return"),
            *table(PERIOD_HEAD, period_rows(pf["periods"], labels, limit)),
            *embed(ctx, f"{key}-xirr-portfolio"),
        ]
        shown = select_rows(pf["periods"], labels, limit)
    for k, acct in sorted(a["accounts"].items()):
        out += [
            *h2(k, "investment-account"),
            *table(PERIOD_HEAD, period_rows(acct["periods"], labels, limit)),
            *embed(ctx, f"{key}-xirr-{slugs[k]}"),
        ]
    return "\n".join([*out, *notes.section(notes.period_notes(shown), a)])


def monthly_report(ctx: Ctx) -> str:
    return periodic_report(ctx, "monthly", "Monthly report")


def yearly_report(ctx: Ctx) -> str:
    return periodic_report(ctx, "yearly", "Yearly report")
