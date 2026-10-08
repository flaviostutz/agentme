"""Parse the BB annual income report: balances at both year ends and income per asset (pt-BR numbers)."""

import re

from portfolio_manager.app.records import account_id, dec, result
from portfolio_manager.shared.errors import PmError
from portfolio_manager.shared.models import Doc
from portfolio_manager.shared.values import parse_number

NAME = "bb_informe"
KIND = "reference"
YEAR = re.compile(r"Ano Calendário (\d{4})")
ROW = re.compile(
    r"^(?P<name>\S.*?)\s{2,}(?P<a>[\d.]+,\d{2}-?)\s+(?P<b>[\d.]+,\d{2}-?)(?:\s+(?P<c>[\d.]+,\d{2}-?))?\s*$"
)
SECTIONS = {"01.": "exempt", "02.": "exclusive-tax", "03.": "current-account", "04.": "prepaid-cards"}


def detect(doc: Doc) -> bool:
    return "Informe de Rendimentos Financeiros" in doc.text()


def holder(doc: Doc) -> str:
    """Account holder name from the 'Conta Nome CPF' block (alphabetic words only; the CPF is never read)."""
    lines = doc.lines()
    i = next((i for i, s in enumerate(lines) if s.startswith("Conta") and "Nome" in s), None)
    if i is None or i + 1 >= len(lines):
        return ""
    return " ".join(t for t in lines[i + 1].split()[1:] if t.isalpha())


def parse(doc: Doc, answers: dict) -> list:
    lines = doc.lines()
    text = "\n".join(lines)
    year = YEAR.search(text)
    holder = next((i for i, s in enumerate(lines) if s.startswith("Conta") and "Nome" in s), None)
    if not year or holder is None:
        msg = "bb informe: unexpected layout"
        raise PmError(msg)
    number = lines[holder + 1].split()[0]
    acct = account_id("bb", number)
    y = year.group(1)
    res = result(
        NAME,
        KIND,
        {"id": acct, "institution": "banco-do-brasil", "currency": "BRL", "mode": "value-only"},
        {"start": f"{y}-01-01", "end": f"{y}-12-31"},
    )
    section, refs = "", []
    for s in lines:
        if s[:3] in SECTIONS:
            section = SECTIONS[s[:3]]
            continue
        m = ROW.match(s)
        if m and section in ("exempt", "exclusive-tax", "current-account"):
            refs.append(
                {
                    "kind": "year-end-balance",
                    "account": acct,
                    "year": int(y),
                    "section": section,
                    "security": m.group("name").title(),
                    "start": dec(parse_number(m.group("a"), ",")),
                    "end": dec(parse_number(m.group("b"), ",")),
                    "income": dec(parse_number(m.group("c"), ",")) if m.group("c") else None,
                }
            )
    res["references"] = refs
    return [res]
