"""investment-accounts.md: one section per investment account with its cash, positions, flows and checks."""

from portfolio_manager.app.fmt import money, table
from portfolio_manager.app.reports.common import PERIOD_HEAD, Ctx, embed, h2, header, is_window, period_rows


def _label(label: str) -> bool:
    return label == "inception" or is_window(label) or label.startswith("year")


def _split(analysis: dict, key: str) -> dict:
    return next((x for x in (analysis.get("portfolio") or {}).get("accounts", []) if x["account"] == key), {})


def _facts(analysis: dict, key: str, a: dict) -> list:
    acct, split = a["account"], _split(analysis, key)
    out = [
        f"- Institution: {acct['institution']}; mode: {acct['mode']}; currency: {acct['currency']}",
        f"- Valuations from {a['first']} to {a['last']}; latest value {money(a['latest_value'])} {acct['currency']} ({money(a['latest_value_eur'])} EUR)",
    ]
    if split.get("cash") is not None:
        out.append(
            f"- Cash {money(split['cash'])} and positions {money(split['positions'])} {acct['currency']} on {a['last']}"
        )
    out.append(f"- Flows status: {a['flows_status']}")
    acc = a["accounting"]
    if acc is not None:
        out += [
            f"- Realized P&L rows: {len(acc['realized'])} ({acc['realized_status']} cost basis); open lots: {len(acc['lots'])}",
            f"- Cash balance: {money(acc['cash'])}; days with negative cash: {len(acc['negative_cash_days'])}",
            *[f"- ERROR: {e}" for e in acc["errors"]],
        ]
    mine = [c for c in analysis["checks"] if c["account"] == key]
    out.append(
        f"- Reconciliation: {sum(c['level'] == 'ok' for c in mine)} ok, {sum(c['level'] == 'warn' for c in mine)} warn, "
        f"{sum(c['level'] == 'fail' for c in mine)} fail"
    )
    return [*out, ""]


def investment_accounts_report(ctx: Ctx) -> str:
    a = ctx.analysis
    out = header("Investment accounts", "investment-accounts", ctx)
    if a["portfolio"]:
        out += [*h2("Wealth share by investment account", "wealth"), *embed(ctx, "wealth-by-account")]
    for k, acct in sorted(a["accounts"].items()):
        out += [*h2(k, "investment-account", "cash-positions", "reconciliation"), *_facts(a, k, acct)]
        out += table(PERIOD_HEAD, period_rows(acct["periods"], _label))
    return "\n".join(out)
