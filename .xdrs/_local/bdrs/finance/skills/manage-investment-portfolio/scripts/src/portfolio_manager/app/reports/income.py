"""income.md: dividends, interest, fees and taxes per year and per investment account, with the trailing yield."""

from decimal import Decimal

from portfolio_manager.app import notes
from portfolio_manager.app.fmt import money, pct, table
from portfolio_manager.app.reports.common import Ctx, embed, h2, header

DRAG_HEAD = [
    "Investment account",
    "Currency",
    "Dividends",
    "Interest",
    "Fees",
    "Taxes",
    "Withholding",
    "Income yield",
    "Fee/tax drag",
]


def _drag(analysis: dict) -> list:
    rows = []
    for k, a in sorted(analysis["accounts"].items()):
        acc = a["accounting"]
        if acc is None:
            continue
        first = a["periods"][0] if a["periods"] else None
        avg = (Decimal(first["start_value"] or 0) + Decimal(first["end_value"] or 0)) / 2 if first else Decimal(0)
        inc = acc["income"]
        yield_ = (Decimal(inc["dividends"]) + Decimal(inc["interest"])) / avg if avg > 0 else None
        drag = (Decimal(inc["fees"]) + Decimal(inc["taxes"])) / avg if avg > 0 else None
        rows.append(
            [
                k,
                acc["currency"],
                money(inc["dividends"]),
                money(inc["interest"]),
                money(inc["fees"]),
                money(inc["taxes"]),
                money(inc["withholding"]),
                pct(yield_, "approximate"),
                pct(drag, "approximate"),
            ]
        )
    return rows


def _years(inc: dict) -> list:
    rows = [
        [y, money(v["dividends"]), money(v["interest"]), money(v["fees"]), money(v["taxes"]), money(v["withholding"])]
        for y, v in inc["years"].items()
    ]
    out = h2("Per calendar year (EUR)", "dividends-interest", "fees-taxes")
    out += table(["Year", "Dividends", "Interest", "Fees", "Taxes", "Withholding"], rows)
    return [
        *out,
        "Amounts are converted to EUR at the date of each event, so they match the tax-year view of your statements.",
        "",
    ]


def _trailing(ctx: Ctx, inc: dict) -> list:
    out = h2("Last 12 months", "trailing-yield", "dividends-interest")
    out += [
        (
            f"Dividends and interest received: **{money(inc['trailing_eur'])} EUR**; "
            f"trailing income yield on open positions: **{pct(inc['yield'], 'approximate')}**."
        ),
        "",
        *embed(ctx, "income"),
    ]
    payers = [[p["name"], money(p["amount_eur"])] for p in inc["payers"]]
    return [*out, *(table(["Top dividend payers", "EUR"], payers) if payers else [])]


def income_report(ctx: Ctx) -> str:
    a = ctx.analysis
    out = header("Income, fees and taxes", "income", ctx)
    inc = a.get("income")
    if inc:
        out += [*_trailing(ctx, inc), *_years(inc)]
    out += [
        *h2("Income yield and fee/tax drag per investment account", "income-yield", "fee-drag"),
        *table(DRAG_HEAD, _drag(a)),
    ]
    return "\n".join([*out, *notes.section(notes.overview_notes(a))])
