"""Shared pieces of every report: context, navigation bar, headers, concept-linked headings and period tables."""

import re
from decimal import Decimal
from typing import NamedTuple

from portfolio_manager.app import concepts
from portfolio_manager.app.fmt import mark, money, pct

PAGES = (
    ("portfolio", "Portfolio"),
    ("monthly", "Monthly"),
    ("yearly", "Yearly"),
    ("investment-accounts", "Investment accounts"),
    ("securities", "Securities"),
    ("income", "Income"),
    ("risk", "Risk"),
    ("markets", "Markets"),
    ("concepts", "Concepts"),
)
LEGEND = "Legend: `~` approximate or interpolated, `n/a` unavailable (never 0), `partial` incomplete cost basis."
PERIOD_CONCEPTS = ["twr", "xirr", "window", "period-return", "gain", "net-flows", "first-day", "partial-period"]
PERIOD_HEAD = [
    "Period",
    "First day .. last day",
    "Window",
    "Start (EUR)",
    "End (EUR)",
    "Net flows",
    "Gain",
    "TWR (natural)",
    "XIRR (actual)",
    "Period return",
]
TOP_PIE = 8
MONTH_LIMIT = 24


class Ctx(NamedTuple):
    """Everything a report needs: the analysis, open items, classifications, the input check and the chart texts."""

    analysis: dict
    unresolved: list
    known: list
    check: dict | None
    charts: dict

    @property
    def pages(self) -> list:
        return [k for k, _ in PAGES if k != "markets" or self.known]


def nav(current: str, pages: list) -> str:
    """One line linking every report; the current page is bold and not linked."""
    names = dict(PAGES)
    return " | ".join(f"**{names[k]}**" if k == current else f"[{names[k]}]({k}.md)" for k in pages)


def header(title: str, current: str, ctx: Ctx, *, legend: bool = False) -> list:
    c = ctx.analysis["check_counts"]
    out = [
        f"# {title}",
        "",
        nav(current, ctx.pages),
        "",
        f"> Unresolved records: **{len(ctx.unresolved)}** | Reconciliation checks: {c['ok']} ok, {c['warn']} warn, {c['fail']} fail",
    ]
    if legend:
        out.append(f"> {LEGEND}")
    return [*out, ""]


def h2(title: str, *keys: str) -> list:
    """Section heading with the concepts it uses linked inline."""
    links = f" ({', '.join(concepts.link(k) for k in keys)})" if keys else ""
    return [f"## {title}{links}", ""]


def embed(ctx: Ctx, name: str) -> list:
    """The mermaid chart of graphs/<name>.mmd as a fenced block; nothing when that chart does not exist."""
    text = ctx.charts.get(f"{name}.mmd")
    return ["```mermaid", text.rstrip(), "```", ""] if text else []


def _xirr_cell(p: dict) -> str:
    if p["xirr"] is None and str(p.get("xirr_reason", "")).startswith("n/a"):
        return p["xirr_reason"]
    return pct(p["xirr"], p["xirr_status"])


def select_rows(periods: list, labels, limit: int | None = None) -> list:
    """Rows whose label passes `labels`; with a limit only the latest ones."""
    rows = [p for p in periods if labels(p["label"])]
    return rows[-limit:] if limit else rows


def period_rows(periods: list, labels, limit: int | None = None) -> list:
    rows = []
    for p in select_rows(periods, labels, limit):
        rows.append(
            [
                p["label"],
                f"{p['first_day']} .. {p['to']}",
                p["window"],
                money(p["start_value"]) + mark(p["start_status"]),
                money(p["end_value"]) + mark(p["end_status"]),
                money(p["net_flows"]),
                money(p.get("gain")),
                pct(p["twr"], p["twr_status"]),
                _xirr_cell(p),
                pct(p.get("period_return"), p.get("period_return_status", "unavailable")),
            ]
        )
    return rows


def is_window(label: str) -> bool:
    return label.startswith("last 12 months")


def is_month(label: str) -> bool:
    return label.startswith("month ")


def is_year(label: str) -> bool:
    return label.startswith("year ")


def scope_slugs(accounts: dict) -> dict:
    """{account id: file-name slug}; slugs are unique and never 'portfolio', which is reserved for the portfolio."""
    used, out = {"portfolio"}, {}
    for key in sorted(accounts):
        base = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-") or "account"
        slug, n = base, 2
        while slug in used:
            slug, n = f"{base}-{n}", n + 1
        used.add(slug)
        out[key] = slug
    return out


def window_row(periods: list) -> dict | None:
    return next((p for p in periods if is_window(p["label"])), None)


def dec(value) -> Decimal | None:
    return None if value is None else Decimal(value)
