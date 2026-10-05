"""Parse the BB investment portfolio report: per-asset balances at both ends of the period plus aggregate entries and exits."""

import re
from decimal import Decimal

from portfolio_manager.app.records import (
    account_id,
    check,
    dec,
    position,
    result,
    rounding_tolerance,
    snapshot,
    unresolved,
)
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import ZERO, iso, parse_date, parse_money, sha256_file

NAME = "bb_portfolio"
KIND = "snapshot"
UNSUPPORTED = ("poupanca",)  # savings products are listed but excluded from wealth
PERIOD = re.compile(r"(\d{2}/\d{2}/\d{4}) até (\d{2}/\d{2}/\d{4})")
CLASS_TITLES = {
    "renda fixa": "fixed-income",
    "renda variável": "equity",
    "multimercado": "multi-asset",
    "previdência": "pension",
}


def detect(doc: Doc) -> bool:
    text = doc.text()
    return "PORTFÓLIO DE INVESTIMENTOS" in text and "bb.com.br" in text


def _brl(token: str) -> Decimal:
    return parse_money(token, decimal=",")[1]


def _is_brl(token: str) -> bool:
    return token.startswith("R$")


def parse(doc: Doc, answers: dict) -> list:
    sha = sha256_file(doc.path)
    lines = doc.lines()
    try:
        number = re.search(r"CC ([\d-]+)", lines[lines.index("Agência/Conta") + 1]).group(1)
        m = PERIOD.search(" ".join(lines[lines.index("Período:") + 1 :][:2]))
        total_end = _brl(lines[lines.index("Saldo Bruto:") + 1])
        pstart, pend = parse_date(m.group(1), "dd/mm/yyyy"), parse_date(m.group(2), "dd/mm/yyyy")
        summary = lines.index("TOTAL")
        s_start, s_in, s_out, s_end = (_brl(lines[summary + k]) for k in (1, 2, 3, 4))
    except (ValueError, AttributeError) as err:
        msg = f"bb portfolio: unexpected layout ({err})"
        raise PmError(msg) from err
    acct = account_id("bb", number)
    res = result(
        NAME,
        KIND,
        {"id": acct, "institution": "banco-do-brasil", "currency": "BRL", "mode": "value-only"},
        {"start": iso(pstart), "end": iso(pend)},
    )
    stop = next((i for i, s in enumerate(lines) if s == "Liquidez da carteira"), len(lines))
    first = next((i for i, s in enumerate(lines) if s == "Distribuição da carteira"), None)
    if first is None:
        msg = "bb portfolio: missing 'Distribuição da carteira' section"
        raise PmError(msg)
    cls, rows = "", []
    for i in range(first, stop):
        low = lines[i].lower()
        for title, label in CLASS_TITLES.items():
            if low.startswith(title) and i + 1 < stop and lines[i + 1].startswith("Alocação"):
                cls = label
        if (
            i + 7 < stop
            and not _is_brl(lines[i])
            and all(_is_brl(lines[i + k]) for k in range(1, 7))
            and lines[i + 7].endswith("%")
        ):
            rows.append((lines[i], cls, [_brl(lines[i + k]) for k in range(1, 7)]))
    start_pos, end_pos = [], []
    for name, cls, v in rows:
        kind = "savings" if name.lower().startswith(UNSUPPORTED) else cls
        for bucket, value in ((start_pos, v[0]), (end_pos, v[3])):
            pos = position("", "", name.title(), None, None, value, "BRL")
            pos["asset_class"] = kind
            if kind == "savings":
                pos["unsupported"] = "savings product"
            bucket.append(pos)
        res["references"].append(
            {
                "kind": "period-flows",
                "account": acct,
                "asset": name.title(),
                "from": iso(pstart),
                "to": iso(pend),
                "entries": dec(v[1]),
                "exits": dec(v[2]),
                "start": dec(v[0]),
                "end": dec(v[3]),
            }
        )
    if not rows:
        res["unresolved"].append(
            unresolved(
                sha, "no-positions", "no asset rows found", "Is this report empty or a new layout?", doc.path.name
            )
        )
    res["snapshots"] = [
        snapshot(
            acct,
            iso(pstart),
            start_pos,
            positions_value=sum((Decimal(p["value"]) for p in start_pos), ZERO),
            currency="BRL",
            ref=f"{sha[:8]}:start",
        ),
        snapshot(
            acct,
            iso(pend),
            end_pos,
            positions_value=sum((Decimal(p["value"]) for p in end_pos), ZERO),
            total=total_end,
            currency="BRL",
            ref=f"{sha[:8]}:end",
        ),
    ]
    tol = rounding_tolerance(len(rows))
    res["checks"] = [
        check("sum of start balances = report total", s_start, sum((v[0] for _, _, v in rows), ZERO), tol),
        check("sum of entries = report total", s_in, sum((v[1] for _, _, v in rows), ZERO), tol),
        check("sum of exits = report total", s_out, sum((v[2] for _, _, v in rows), ZERO), tol),
        check("sum of end balances = report total", s_end, sum((v[3] for _, _, v in rows), ZERO), tol),
        check("report total = cover page gross balance", total_end, s_end, rounding_tolerance(1)),
    ]
    return [res]
