"""Parse an Upvest ex-post cost report: covered period, average valuation, total costs and product costs per ISIN."""

import re
from decimal import Decimal

from portfolio_manager.app.records import ISIN_RE, account_id, check, dec, result, rounding_tolerance
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import ZERO, iso, parse_date, parse_number

NAME = "upvest_expost"
KIND = "reference"
COVERED = re.compile(r"Covered period: (\d{2}/\d{2}/\d{4})-(\d{2}/\d{2}/\d{4})")
AVG = re.compile(r"Average account valuation: ([\d.,]+) EUR")
TOTAL = re.compile(r"decreased by ([\d.,]+) EUR .*? corresponds to ([\d.,]+)\s*%")
NUMBER = re.compile(r"^\d[\d.,]*$")


def detect(doc: Doc) -> bool:
    return "Upvest Securities" in doc.text() and "Ex-post cost report" in doc.text()


def parse(doc: Doc, answers: dict) -> list:
    lines = doc.lines()
    if "Ex-post-Kosteninformation" in lines:  # the German copy follows the English pages
        lines = lines[: lines.index("Ex-post-Kosteninformation")]
    text = " ".join(lines)
    cov, avg, tot = COVERED.search(text), AVG.search(text), TOTAL.search(text)
    if not (cov and avg and tot):
        msg = "upvest expost: unexpected layout"
        raise PmError(msg)
    number = lines[lines.index("Securities account number") + 1]
    acct = account_id("upvest", number, drop_suffix=True)
    start, end = iso(parse_date(cov.group(1), "dd/mm/yyyy")), iso(parse_date(cov.group(2), "dd/mm/yyyy"))
    res = result(
        NAME,
        KIND,
        {"id": acct, "institution": "upvest", "currency": "EUR", "mode": "snapshot"},
        {"start": start, "end": end},
    )
    per = []
    for i, s in enumerate(lines):
        if ISIN_RE.match(s) and (i == 0 or lines[i - 1] != s):
            nums = [t for t in lines[i + 1 : i + 12] if NUMBER.match(t)][:3]
            if len(nums) == 3:
                per.append(
                    {
                        "isin": s,
                        "service_costs": dec(parse_number(nums[0])),
                        "product_costs": dec(parse_number(nums[1])),
                        "inducements": dec(parse_number(nums[2])),
                    }
                )
    total = parse_number(tot.group(1))
    res["references"] = [
        {
            "kind": "cost-report",
            "account": acct,
            "from": start,
            "to": end,
            "avg_valuation": dec(parse_number(avg.group(1))),
            "total_cost": dec(total),
            "cost_pct": dec(parse_number(tot.group(2))),
            "per_instrument": per,
        }
    ]
    summed = sum(
        (Decimal(p["service_costs"]) + Decimal(p["product_costs"]) + Decimal(p["inducements"]) for p in per), ZERO
    )
    res["checks"] = [check("sum of per-instrument costs = total cost", total, summed, rounding_tolerance(len(per)))]
    return [res]
