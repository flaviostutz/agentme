# Runtime: Python >=3.10; Upvest (N26) "Securities account statement" adapter (snapshot source).
"""Parse an Upvest quarterly securities account statement into a positions snapshot (English pages only)."""

import re
from decimal import Decimal

from institutions.common import account_id, check, position, result, rounding_tolerance, snapshot, unresolved
from sourcedoc import Doc, PmError, sha256_file
from util import ZERO, iso, parse_date, parse_money, parse_number

NAME = "upvest_snapshot"
KIND = "snapshot"
AS_OF = re.compile(r"Securities account statement as of (\d{2}\.\d{2}\.\d{4})")
QTY = re.compile(r"^([\d.,]+) / unit\(s\)$")
ISIN_WKN = re.compile(r"^([A-Z]{2}[A-Z0-9]{9}\d) \(\w+\)$")


def detect(doc: Doc) -> bool:
    text = doc.text()
    return "Upvest Securities" in text and bool(AS_OF.search(text))


def _english(lines: list) -> list:
    """English pages only; an amount whose currency code wrapped onto the next line is re-joined."""
    for i, s in enumerate(lines):
        if s.startswith(("Kontomitteilung", "Depotauszug per")):
            lines = lines[:i]
            break
    out = []
    for s in lines:
        if s == "EUR" and out and out[-1][:1].isdigit():
            out[-1] += " EUR"
        else:
            out.append(s)
    return out


def _value_after(lines: list, label: str) -> str:
    """Value line after a label, skipping repeated (doubled) label lines."""
    i = lines.index(label)
    while i + 1 < len(lines) and lines[i + 1] == label:
        i += 1
    return lines[i + 1]


def _block(lines: list):
    """lines: from the quantity line to the line before the next position; returns a position or None."""
    qty = parse_number(QTY.match(lines[0]).group(1))
    k = next((i for i, s in enumerate(lines) if s == "ISIN (WKN)"), None)
    if k is None or k + 1 >= len(lines) or not ISIN_WKN.match(lines[k + 1]):
        return None
    name = " ".join(s for s in lines[1:k] if not QTY.match(s))
    money = []
    for s in lines[k + 2:]:
        try:
            cur, value = parse_money(s)
        except ValueError:
            continue
        if cur == "EUR":
            money.append(value)
    if len(money) < 2:
        return None
    return position(ISIN_WKN.match(lines[k + 1]).group(1), "", name, qty, money[-2], money[-1], "EUR")


def parse(doc: Doc, answers: dict) -> list:
    sha = sha256_file(doc.path)
    lines = _english(doc.lines())
    text = " ".join(lines)
    m = AS_OF.search(text)
    number = _value_after(lines, "Securities account number")
    day = iso(parse_date(m.group(1), "dd.mm.yyyy"))
    acct = account_id("upvest", number, drop_suffix=True)
    res = result(NAME, KIND, {"id": acct, "institution": "upvest", "currency": "EUR", "mode": "snapshot"}, {"start": day, "end": day})
    starts = [i for i, s in enumerate(lines) if QTY.match(s) and not (i and lines[i - 1] == s)]
    stop = next((i for i, s in enumerate(lines) if s == "Number of positions"), len(lines))
    positions = []
    for n, i in enumerate(starts):
        block = lines[i:starts[n + 1] if n + 1 < len(starts) else stop]
        pos = _block(block)
        if pos is None:
            res["unresolved"].append(unresolved(sha, "unparsed-position", " | ".join(block), "How should this position be read?", doc.path.name))
        else:
            positions.append(pos)
    if "Number of positions" not in lines or "Total value" not in lines:
        raise PmError("upvest snapshot: missing totals")
    count = int(_value_after(lines, "Number of positions"))
    total = parse_money(_value_after(lines, "Total value"))[1]
    pos_sum = sum((Decimal(p["value"]) for p in positions), ZERO)
    res["snapshots"] = [snapshot(acct, day, positions, cash=None, positions_value=pos_sum, total=total, currency="EUR", ref=f"{sha[:8]}:snap")]
    res["checks"] = [
        check("sum of positions = total value", total, pos_sum, rounding_tolerance(len(positions))),
        check("position count = number of positions", Decimal(count), Decimal(len(positions)), ZERO),
    ]
    return [res]
