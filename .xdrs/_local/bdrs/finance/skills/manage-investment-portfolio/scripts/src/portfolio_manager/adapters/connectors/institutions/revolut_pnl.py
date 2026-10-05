"""Parse a Revolut P&L report: per-sale lots (acquired date, cost, proceeds) and the summary totals."""

import re
from decimal import Decimal

from portfolio_manager.app.records import ISIN_RE, account_id, check, dec, result, rounding_tolerance, unresolved
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import ZERO, iso, parse_date, parse_money, parse_number

NAME = "revolut_pnl"
KIND = "reference"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEADER = {
    "Date acquired",
    "Date sold",
    "Symbol",
    "Security name",
    "ISIN",
    "Country",
    "Quantity",
    "Cost basis",
    "Gross proceeds",
    "Gross PnL",
    "Fees",
}


def detect(doc: Doc) -> bool:
    text = doc.text()
    return "Profit and Loss Statement" in text and "Sells Summary" in text


def _after(lines: list, label: str) -> str:
    return lines[lines.index(label) + 1]


def parse(doc: Doc, answers: dict) -> list:
    lines = doc.lines()
    ccy = lines[0].split()[0]
    try:
        number = _after(lines, "Account number")
        first, last = _after(lines, "Period").split(" - ")
        proceeds = parse_money(_after(lines, "Gross Proceeds"))[1]
        cost = parse_money(_after(lines, "Cost Basis"))[1]
        pnl = parse_money(_after(lines, "Gross PnL"))[1]
        other = parse_money(_after(lines, "Net other income"))[1]
    except (ValueError, IndexError) as err:
        msg = f"revolut pnl: unexpected layout ({err})"
        raise PmError(msg) from err
    acct = account_id("revolut", number) + "-" + ccy.lower()
    pstart, pend = iso(parse_date(first, "dd Mon yyyy")), iso(parse_date(last, "dd Mon yyyy"))
    res = result(
        NAME,
        KIND,
        {"id": acct, "institution": "revolut", "currency": ccy, "mode": "transactions"},
        {"start": pstart, "end": pend},
    )
    sales = []
    table = (
        [s for s in lines[: lines.index("Other income & fees")] if s not in HEADER]
        if "Other income & fees" in lines
        else lines
    )
    for i, s in enumerate(table):
        if not ISIN_RE.match(s) or i < 4 or i + 13 > len(table):
            continue
        r = table[i - 4 : i + 13]
        if not (ISO_DATE.match(r[0]) and ISO_DATE.match(r[1])):
            continue
        m = [parse_money(t)[1] for t in r[7:] if not t.startswith("Rate")]
        # two print orders exist: paired columns (c,c,p,p,g,g,f,f) or halves (c,p,g,f,c,p,g,f); pick the one where pnl = proceeds - cost
        pick = next(
            (
                x
                for x in ((m[0], m[2], m[4], m[6]), (m[0], m[1], m[2], m[3]))
                if abs(x[1] - x[0] - x[2]) <= Decimal("0.02")
            ),
            None,
        )
        if pick is None:
            res["unresolved"].append(
                unresolved(
                    doc.path.name, "unparsed-sale", " | ".join(r[:7]), "How should this P&L row be read?", doc.path.name
                )
            )
            continue
        sales.append(
            {
                "kind": "pnl-sale",
                "account": acct,
                "acquired": r[0],
                "sold": r[1],
                "symbol": r[2],
                "isin": r[4],
                "quantity": dec(parse_number(r[6])),
                "cost": dec(pick[0]),
                "proceeds": dec(pick[1]),
                "pnl": dec(pick[2]),
                "fees": dec(pick[3]),
            }
        )
    res["references"] = [
        *sales,
        {
            "kind": "pnl-summary",
            "account": acct,
            "from": pstart,
            "to": pend,
            "gross_proceeds": dec(proceeds),
            "cost_basis": dec(cost),
            "gross_pnl": dec(pnl),
            "net_other_income": dec(other),
        },
    ]
    tol = rounding_tolerance(len(sales))
    res["checks"] = [
        check("sum of sale proceeds = summary", proceeds, sum((Decimal(x["proceeds"]) for x in sales), ZERO), tol),
        check("sum of sale cost basis = summary", cost, sum((Decimal(x["cost"]) for x in sales), ZERO), tol),
        check("sum of sale pnl = summary", pnl, sum((Decimal(x["pnl"]) for x in sales), ZERO), tol),
    ]
    return [res]
