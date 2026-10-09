"""securities.md: open positions across investment accounts, contribution per security and the securities of each account."""

from decimal import Decimal

from portfolio_manager.app import notes
from portfolio_manager.app.fmt import mark, money, pct, table
from portfolio_manager.app.reports.common import Ctx, h2, header

LIMIT = 25
HEAD_CONTRIBUTION = 12
ACCOUNT_HEAD = [
    "Security",
    "ISIN",
    "Quantity",
    "Price",
    "Value",
    "Value (EUR)",
    "Cost",
    "Unrealized",
    "Realized",
    "Note",
]


def _eur_key(row: dict) -> tuple:
    return (row["value_eur"] is None, -Decimal(row["value_eur"] or 0), row["name"] or row["symbol"] or "")


def _row(r: dict) -> list:
    unreal = None if r.get("cost") is None else Decimal(r["value"]) - Decimal(r["cost"])
    realized = "n/a"
    if r.get("realized_pnl") is not None:
        realized = money(r["realized_pnl"]) + (" partial" if r["realized_status"] == "partial" else "")
    return [
        r["name"] or r["symbol"],
        r["isin"] or "-",
        r["quantity"] if r["quantity"] is not None else "n/a",
        money(r["price"]),
        money(r["value"]),
        money(r["value_eur"]),
        money(r.get("cost")) if "cost" in r else "n/a",
        money(unreal),
        realized,
        "unsupported" if r["unsupported"] else "",
    ]


def _lots(shown: list) -> list:
    rows = []
    for r in shown:
        price = Decimal(r["price"]) if r["price"] is not None else None
        for lot in r.get("lots", []):
            unreal = (
                None
                if lot["cost"] is None or price is None
                else Decimal(lot["quantity"]) * price - Decimal(lot["cost"])
            )
            rows.append(
                [
                    r["name"] or r["symbol"],
                    lot["acquired"] or "unknown (opening)",
                    lot["quantity"],
                    money(lot["cost"]),
                    money(unreal),
                    "complete" if lot["cost"] is not None else "partial",
                ]
            )
    return table(["Security", "Acquired", "Quantity", "Cost", "Unrealized", "Cost basis"], rows) if rows else []


def _account(key: str, a: dict) -> list:
    rows = sorted(a["securities"], key=_eur_key)
    shown, rest = rows[:LIMIT], rows[LIMIT:]
    as_of = a["securities"][0]["as_of"] if a["securities"] else a["last"]
    body = [_row(r) for r in shown]
    if rest:
        others = sum((Decimal(r["value_eur"]) for r in rest if r["value_eur"] is not None), Decimal(0))
        body.append([f"Others ({len(rest)} securities)", "", "", "", "", money(others), "", "", "", ""])
    out = [
        *h2(f"{key} (as of {as_of})", "investment-account", "unrealized-pl", "realized-pl"),
        *table(ACCOUNT_HEAD, body),
    ]
    lots = _lots(shown)
    return [*out, f"### Lots {key}", "", *lots] if lots else out


def _positions(ctx: Ctx) -> list:
    pos = ctx.analysis.get("positions") or {"rows": []}
    rows = pos["rows"]
    out = h2("Open positions across investment accounts", "security", "weight", "unrealized-pl")
    if not rows:
        return [*out, "_No open positions._", ""]
    body = [
        [
            i,
            f"{r['name']}{'~' if r['no_isin'] else ''}",
            r["isin"] or "-",
            money(r["value_eur"]),
            pct(r["weight"]),
            pct(r["pnl_pct"], "complete" if r["pnl_pct"] is not None else "unavailable"),
            r["as_of"],
            ", ".join(r["accounts"]),
        ]
        for i, r in enumerate(rows[:LIMIT], 1)
    ]
    if len(rows) > LIMIT:
        rest = sum((Decimal(r["value_eur"]) for r in rows[LIMIT:]), Decimal(0))
        weight = sum((Decimal(r["weight"]) for r in rows[LIMIT:] if r["weight"] is not None), Decimal(0))
        body.append(["", f"Others ({len(rows) - LIMIT} securities)", "", money(rest), pct(weight), "n/a", "", ""])
    head = ["#", "Security", "ISIN", "Value (EUR)", "Weight", "P&L %", "Latest date", "Investment accounts"]
    return [*out, *table(head, body), f"Total of open positions: {money(pos['total_eur'])} EUR.", ""]


def _contribution_row(r: dict) -> list:
    return [r["name"], money(r["contribution_eur"]) + mark(r["status"])]


def _contribution_rows(rows: list) -> list:
    if len(rows) <= LIMIT:
        return [_contribution_row(r) for r in rows]
    tail_size = LIMIT - HEAD_CONTRIBUTION
    head, middle, tail = rows[:HEAD_CONTRIBUTION], rows[HEAD_CONTRIBUTION:-tail_size], rows[-tail_size:]
    other = sum((Decimal(r["contribution_eur"]) for r in middle), Decimal(0))
    return [
        *[_contribution_row(r) for r in head],
        [f"Others ({len(middle)} securities)", money(other)],
        *[_contribution_row(r) for r in tail],
    ]


def _contribution(ctx: Ctx) -> list:
    c = ctx.analysis.get("contribution") or {"rows": []}
    if not c["rows"]:
        return []
    out = h2(f"Contribution per security, {c['from']} .. {c['to']}", "contribution", "wealth-bridge")
    out += table(["Security", "Contribution (EUR)"], _contribution_rows(c["rows"]))
    return [
        *out,
        "Value change plus income minus money put in; `~` marks estimates (accounts known by statements only, converted currencies).",
        "",
    ]


def securities_report(ctx: Ctx) -> str:
    a = ctx.analysis
    out = header("Securities", "securities", ctx)
    out += [*_positions(ctx), *_contribution(ctx)]
    for k, acct in sorted(a["accounts"].items()):
        out += _account(k, acct)
    return "\n".join([*out, *notes.section(notes.overview_notes(a))])
