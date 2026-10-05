"""Number and text formatting shared by the report modules; n/a is never rendered as 0."""

from decimal import Decimal

APPROX = ("approximate", "interpolated")


def money(v) -> str:
    return "n/a" if v is None else f"{Decimal(v):,.2f}"


def pct(v, status: str = "complete") -> str:
    if v is None or status == "unavailable":
        return "n/a"
    return f"{Decimal(v) * 100:.2f} %{mark(status)}"


def mark(status: str) -> str:
    return "~" if status in APPROX else ""


def cell(value) -> str:
    """Table-safe text: pipes, backticks and HTML from statements cannot break the table or inject markup."""
    text = str(value).replace("\n", " ")
    for raw, safe in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ("|", "&#124;"), ("`", "&#96;")):
        text = text.replace(raw, safe)
    return text


def table(head: list, rows: list) -> list:
    """Markdown table lines; every data cell is escaped."""
    if not rows:
        return ["_No data._", ""]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return [*out, ""]
