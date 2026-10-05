"""Parse an Upvest annual tax statement (English pages): year transactions and dividend distributions."""

import re
from decimal import Decimal

from portfolio_manager.app.records import account_id, check, dec, result
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import iso, parse_date, parse_number

NAME = "upvest_tax"
KIND = "reference"
TX = re.compile(
    r"(\d{2}/\d{2}/\d{4}) (Buy|Sell) ([\d.,]+) EUR (.+?) ISIN: ([A-Z0-9]{12}) ([\d.,]+) ([\d.,]+) EUR ([\d.,]+) EUR"
)
DIV = re.compile(
    r"(\d{2}/ ?\d{2}/ ?\d{4}) ([\d.,]+) ([\d.,]+) EUR (.+?) ISIN: ([A-Z0-9]{12}) .*?([\d.,]+) EUR ([\d.,]+) EUR"
)
YEAR = re.compile(r"all transactions which took place on your account in (\d{4})")


def detect(doc: Doc) -> bool:
    text = doc.text()
    return "Upvest Securities" in text and "Annual tax statement" in text


def parse(doc: Doc, answers: dict) -> list:
    lines = doc.lines()
    cut = next((i for i, s in enumerate(lines) if s.startswith("Kontomitteilung")), len(lines))
    text = " ".join(lines[:cut])
    year = YEAR.search(text.replace("\n", " "))
    if not year:
        msg = "upvest tax: cannot find the statement year"
        raise PmError(msg)
    number = lines[lines.index("Securities account number") + 1]
    acct = account_id("upvest", number, drop_suffix=True)
    y = year.group(1)
    res = result(
        NAME,
        KIND,
        {"id": acct, "institution": "upvest", "currency": "EUR", "mode": "snapshot"},
        {"start": f"{y}-01-01", "end": f"{y}-12-31"},
    )
    refs = []
    t_start = text.find("Transactions Transactions") if "Transactions Transactions" in text else 0
    d_start = text.find("Dividend Distributions")
    for m in TX.finditer(text[t_start : d_start if d_start > 0 else None]):
        refs.append(
            {
                "kind": "tax-transaction",
                "account": acct,
                "date": iso(parse_date(m.group(1), "dd/mm/yyyy")),
                "side": m.group(2).upper(),
                "isin": m.group(5),
                "price": dec(parse_number(m.group(3))),
                "units": dec(parse_number(m.group(6))),
                "value": dec(parse_number(m.group(7))),
                "fee": dec(parse_number(m.group(8))),
            }
        )
    for m in DIV.finditer(text[d_start:] if d_start > 0 else ""):
        refs.append(
            {
                "kind": "tax-dividend",
                "account": acct,
                "date": iso(parse_date(m.group(1).replace(" ", ""), "dd/mm/yyyy")),
                "isin": m.group(5),
                "units": dec(parse_number(m.group(2))),
                "per_unit": dec(parse_number(m.group(3))),
                "tax": dec(parse_number(m.group(6))),
                "income": dec(parse_number(m.group(7))),
            }
        )
    res["references"] = refs
    res["checks"] = []
    for r in refs:
        if r["kind"] == "tax-transaction":
            units, price, value = Decimal(r["units"]), Decimal(r["price"]), Decimal(r["value"])
            res["checks"].append(
                check(
                    f"units x price = value ({r['date']} {r['isin']})",
                    value,
                    units * price,
                    Decimal("0.01") + price * Decimal("0.005"),
                )
            )  # units are printed with 2 decimals
    return [res]
