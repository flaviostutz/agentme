"""markets.md: allocation of the open securities by every classification field that has data."""

from decimal import Decimal

from portfolio_manager.app import classify as classify_mod
from portfolio_manager.app.fmt import money, table
from portfolio_manager.app.reports.common import Ctx, h2, header

FIELDS = ("security_class", "region", "country", "sector", "currency", "exchange", "theme", "issuer")


def markets_report(ctx: Ctx) -> str:
    out = header("Markets and allocation", "markets", ctx)
    securities = [r for a in ctx.analysis["accounts"].values() for r in a["securities"]]
    for field in FIELDS:
        alloc = classify_mod.allocation(securities, ctx.known, field)
        total = sum(alloc.values(), Decimal(0))
        if not alloc or (set(alloc) == {"unclassified"} and field != "security_class"):
            continue
        out += h2(f"By {field}", "weight")
        out += table(
            [field, "Value (EUR)", "Share"],
            [
                [k, money(v), f"{100 * v / total:.1f} %" if total else "n/a"]
                for k, v in sorted(alloc.items(), key=lambda kv: -kv[1])
            ],
        )
    out += [
        (
            "Classifications come from `data/classifications.json` (each entry has a source URL and an as-of date); "
            "values are per investment account's latest statement."
        ),
        "",
    ]
    return "\n".join(out)
