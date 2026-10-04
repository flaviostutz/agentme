# Runtime: Python >=3.11 stdlib only; renders fully templated Markdown reports and Mermaid graphs from the derived analysis (no prose written by an LLM).
"""Report rendering. Every report starts with the unresolved count and the check counts; ~ marks approximate or interpolated values."""

from decimal import Decimal

import classify as classify_mod

LEGEND = "Legend: `~` approximate or interpolated, `n/a` unavailable (never 0), `partial` incomplete cost basis."


def money(v) -> str:
    return "n/a" if v is None else f"{Decimal(v):,.2f}"


def pct(v, status: str = "complete") -> str:
    if v is None or status == "unavailable":
        return "n/a"
    mark = "~" if status in ("approximate", "interpolated") else ""
    return f"{Decimal(v) * 100:.2f} %{mark}"


def mark(status: str) -> str:
    return "~" if status in ("approximate", "interpolated") else ""


def header(title: str, analysis: dict, unresolved: list) -> list:
    c = analysis["check_counts"]
    return [f"# {title}", "", f"> Unresolved records: **{len(unresolved)}** | Reconciliation checks: {c['ok']} ok, {c['warn']} warn, {c['fail']} fail",
            f"> {LEGEND}", ""]


def table(head: list, rows: list) -> list:
    if not rows:
        return ["_No data._", ""]
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return [*out, ""]


def _period_rows(periods: list, labels) -> list:
    rows = []
    for p in periods:
        if not labels(p["label"]):
            continue
        xirr = pct(p["xirr"], p["xirr_status"]) + (" annualized" if p.get("xirr_annualized") and p["xirr"] is not None else "")
        rows.append([p["label"], f"{p['from']} .. {p['to']}", money(p["start_value"]) + mark(p["start_status"]),
                     money(p["end_value"]) + mark(p["end_status"]), money(p["net_flows"]), money(p.get("gain")),
                     pct(p["twr"], p["twr_status"]), xirr, pct(p.get("period_return"), p.get("period_return_status", "unavailable"))])
    return rows


PERIOD_HEAD = ["Period", "Dates", "Start (EUR)", "End (EUR)", "Net flows", "Gain", "TWR", "XIRR", "Period return"]


def _drag(analysis: dict) -> list:
    rows = []
    for k, a in sorted(analysis["accounts"].items()):
        acc = a["accounting"]
        if acc is None:
            continue
        avg = (Decimal(a["periods"][0]["start_value"] or 0) + Decimal(a["periods"][0]["end_value"] or 0)) / 2 if a["periods"] else Decimal(0)
        inc = acc["income"]
        yield_ = (Decimal(inc["dividends"]) + Decimal(inc["interest"])) / avg if avg > 0 else None
        drag = (Decimal(inc["fees"]) + Decimal(inc["taxes"])) / avg if avg > 0 else None
        rows.append([k, acc["currency"], money(inc["dividends"]), money(inc["interest"]), money(inc["fees"]), money(inc["taxes"]),
                     money(inc["withholding"]), pct(yield_, "approximate"), pct(drag, "approximate")])
    return rows


def _bridge(analysis: dict) -> list:
    pf = analysis["portfolio"]
    inception = next((p for p in pf["periods"] if p["label"] == "inception"), None)
    if not inception or inception["gain"] is None:
        return []
    income = fees = Decimal(0)
    for a in analysis["accounts"].values():
        acc = a["accounting"]
        if acc is not None and acc["currency"] == "EUR":
            income += Decimal(acc["income"]["dividends"]) + Decimal(acc["income"]["interest"])
            fees += Decimal(acc["income"]["fees"]) + Decimal(acc["income"]["taxes"])
    fx = Decimal(inception["fx_effect"]) if inception.get("fx_effect") is not None else Decimal(0)
    gain = Decimal(inception["gain"])
    other = gain - income + fees - fx
    return [("Start value", Decimal(inception["start_value"])), ("Net flows", Decimal(inception["net_flows"])), ("Income (EUR accounts)", income),
            ("Fees and taxes (EUR accounts)", -fees), ("FX effect", fx), ("Market and other", other), ("End value", Decimal(inception["end_value"]))]


def portfolio_report(analysis: dict, unresolved: list) -> str:
    pf = analysis["portfolio"]
    out = header("Portfolio report", analysis, unresolved)
    if not pf:
        return "\n".join([*out, "_No valued accounts yet._", ""])
    out += ["## Wealth", "", (f"Consolidated wealth **{money(pf['value_eur'])} EUR** at {pf['common_date']} (latest date where every tracked account "
                              f"has a valuation; status {pf['value_status']})."), ""]
    out += table(["Account", "Latest date", "Value (account currency)", "Currency", "Value (EUR)"],
                 [[a["account"], a["last"], money(a["value"]), a["currency"], money(a["value_eur"])] for a in pf["accounts"]])
    out += ["## Performance", ""] + table(PERIOD_HEAD, _period_rows(pf["periods"], lambda x: x == "inception" or x.startswith(("ytd", "year"))))
    bridge = _bridge(analysis)
    if bridge:
        out += ["## Wealth bridge (inception)", ""] + table(["Component", "EUR"], [[k, money(v)] for k, v in bridge])
    out += ["## Income yield and fee/tax drag", ""]
    out += table(["Account", "Currency", "Dividends", "Interest", "Fees", "Taxes", "Withholding", "Income yield", "Fee/tax drag"], _drag(analysis))
    if analysis["cost_reports"]:
        out += ["## Reported costs", ""] + table(["Account", "Period", "Total cost", "Of average value"],
                                                  [[c["account"], f"{c['from']} .. {c['to']}", money(c["total_cost"]), f"{c['cost_pct']} %"] for c in analysis["cost_reports"]])
    out += ["## Data quality", ""]
    statuses = [p["twr_status"] for p in pf["periods"]]
    total = max(len(statuses), 1)
    out += [(f"- Performance metrics: {statuses.count('complete')} complete, {sum(s in ('approximate', 'interpolated') for s in statuses)} approximate, "
             f"{statuses.count('unavailable')} unavailable ({100 * statuses.count('complete') // total} % complete)."),
            ("- Accounts with a statement valuation on the common date: "
             f"{sum(1 for a in pf['accounts'] if a['last'] == pf['common_date'])} of {len(pf['accounts'])}.")]
    out += [f"- Excluded from the consolidation: {e['account']} ({e['reason']})." for e in analysis["excluded"]]
    out += [f"- {e}" for e in analysis["errors"]]
    out += [f"- Check {c['level']}: {c['account']} {c['name']} (expected {c['expected']}, actual {c['actual']})" for c in analysis["checks"] if c["level"] != "ok"]
    if analysis.get("fx_notice"):
        out.append(f"- FX: {analysis['fx_notice']}")
    return "\n".join([*out, ""])


def periodic_report(analysis: dict, unresolved: list, title: str, labels) -> str:
    out = header(title, analysis, unresolved)
    pf = analysis["portfolio"]
    if pf:
        out += ["## Portfolio", ""] + table(PERIOD_HEAD, _period_rows(pf["periods"], labels))
    for k, a in sorted(analysis["accounts"].items()):
        out += [f"## {k}", ""] + table(PERIOD_HEAD, _period_rows(a["periods"], labels))
    return "\n".join(out)


def assets_report(analysis: dict, unresolved: list) -> str:
    out = header("Assets", analysis, unresolved)
    for k, a in sorted(analysis["accounts"].items()):
        rows = []
        for r in a["assets"]:
            unreal = None if r.get("cost") is None else Decimal(r["value"]) - Decimal(r["cost"])
            rows.append([r["name"] or r["symbol"], r["isin"] or "-", r["quantity"] if r["quantity"] is not None else "n/a", money(r["price"]), money(r["value"]),
                         money(r["value_eur"]), money(r.get("cost")) if "cost" in r else "n/a", money(unreal),
                         (money(r["realized_pnl"]) + (" partial" if r["realized_status"] == "partial" else "")) if r.get("realized_pnl") is not None else "n/a",
                         "unsupported" if r["unsupported"] else ""])
        out += [f"## {k} (as of {a['assets'][0]['as_of'] if a['assets'] else a['last']})", ""]
        out += table(["Asset", "ISIN", "Quantity", "Price", "Value", "Value (EUR)", "Cost", "Unrealized", "Realized", "Note"], rows)
        lots = [(r, lot) for r in a["assets"] if "lots" in r for lot in r["lots"]]
        if lots:
            lot_rows = []
            for r, lot in lots:
                price = Decimal(r["price"]) if r["price"] is not None else None
                unreal = None if lot["cost"] is None or price is None else Decimal(lot["quantity"]) * price - Decimal(lot["cost"])
                lot_rows.append([r["name"] or r["symbol"], lot["acquired"] or "unknown (opening)", lot["quantity"], money(lot["cost"]), money(unreal),
                                 "complete" if lot["cost"] is not None else "partial"])
            out += [f"### Lots {k}", ""] + table(["Asset", "Acquired", "Quantity", "Cost", "Unrealized", "Cost basis"], lot_rows)
    return "\n".join(out)


def banks_report(analysis: dict, unresolved: list) -> str:
    out = header("Banks and brokers", analysis, unresolved)
    for k, a in sorted(analysis["accounts"].items()):
        acct = a["account"]
        out += [f"## {k}", "", f"- Institution: {acct['institution']}; mode: {acct['mode']}; currency: {acct['currency']}",
                f"- Valuations from {a['first']} to {a['last']}; latest value {money(a['latest_value'])} {acct['currency']} ({money(a['latest_value_eur'])} EUR)",
                f"- Flows status: {a['flows_status']}"]
        acc = a["accounting"]
        if acc is not None:
            out += [f"- Realized P&L rows: {len(acc['realized'])} ({acc['realized_status']} cost basis); open lots: {len(acc['lots'])}",
                    f"- Cash balance: {money(acc['cash'])}; days with negative cash: {len(acc['negative_cash_days'])}"]
            out += [f"- ERROR: {e}" for e in acc["errors"]]
        mine = [c for c in analysis["checks"] if c["account"] == k]
        out += [(f"- Reconciliation: {sum(c['level'] == 'ok' for c in mine)} ok, {sum(c['level'] == 'warn' for c in mine)} warn, "
                 f"{sum(c['level'] == 'fail' for c in mine)} fail"), ""]
        out += table(PERIOD_HEAD, _period_rows(a["periods"], lambda x: x == "inception" or x.startswith("ytd")))
    return "\n".join(out)


def markets_report(analysis: dict, unresolved: list, known: list) -> str:
    out = header("Markets and allocation", analysis, unresolved)
    assets = [r for a in analysis["accounts"].values() for r in a["assets"]]
    for field in ("asset_class", "region", "country", "sector", "currency", "exchange", "theme", "issuer"):
        alloc = classify_mod.allocation(assets, known, field)
        total = sum(alloc.values(), Decimal(0))
        if not alloc or (set(alloc) == {"unclassified"} and field != "asset_class"):
            continue
        out += [f"## By {field}", ""]
        out += table([field, "Value (EUR)", "Share"], [[k, money(v), f"{100 * v / total:.1f} %" if total else "n/a"] for k, v in sorted(alloc.items(), key=lambda kv: -kv[1])])
    out += ["Classifications come from `data/classifications.json` (each entry has a source URL and an as-of date); values are per account's latest statement.", ""]
    return "\n".join(out)


def _mmd_chart(title: str, labels: list, series: list, kind: str, y: str) -> str:
    names = ", ".join(f'"{lbl}"' for lbl in labels)
    return "\n".join(["xychart-beta", f'    title "{title}"', f"    x-axis [{names}]", f'    y-axis "{y}"', f"    {kind} [{', '.join(series)}]", ""])


def graphs(analysis: dict) -> dict:
    out = {}
    pf = analysis["portfolio"]
    if not pf:
        return out
    months = [p for p in pf["periods"] if p["label"].startswith("month ")]
    if months:
        out["wealth.mmd"] = _mmd_chart("Wealth (EUR, month end)", [p["to"] for p in months],
                                       [f"{Decimal(p['end_value'] or 0):.2f}" for p in months], "line", "EUR")
        out["performance.mmd"] = _mmd_chart("Monthly TWR (%), unavailable months show 0 in this chart only", [p["to"][:7] for p in months],
                                            [f"{Decimal(p['twr'] or 0) * 100:.2f}" for p in months], "bar", "%")
        out["cashflows.mmd"] = _mmd_chart("Net flows (EUR)", [p["to"][:7] for p in months], [f"{Decimal(p['net_flows']):.2f}" for p in months], "bar", "EUR")
    pie = [(a["account"], Decimal(a["value_eur"])) for a in pf["accounts"] if a["value_eur"] is not None]
    if pie:
        out["allocation.mmd"] = "\n".join(["pie showData", '    title "Wealth by account (EUR, latest valuations)"',
                                           *[f'    "{k}" : {v:.2f}' for k, v in pie], ""])
    bridge = _bridge(analysis)
    if bridge:
        out["wealth-bridge.mmd"] = _mmd_chart("Wealth bridge since inception (EUR)", [k for k, _ in bridge], [f"{v:.2f}" for _, v in bridge], "bar", "EUR")
    return out


def render(analysis: dict, unresolved: list, known: list) -> dict:
    """Return {relative path: text} for every report and graph."""
    files = {
        "reports/portfolio.md": portfolio_report(analysis, unresolved),
        "reports/monthly.md": periodic_report(analysis, unresolved, "Monthly report", lambda x: x.startswith("month ")),
        "reports/yearly.md": periodic_report(analysis, unresolved, "Yearly report", lambda x: x.startswith(("year", "ytd", "inception"))),
        "reports/assets.md": assets_report(analysis, unresolved),
        "reports/banks.md": banks_report(analysis, unresolved),
    }
    if known:
        files["reports/markets.md"] = markets_report(analysis, unresolved, known)
    files.update({f"graphs/{k}": v for k, v in graphs(analysis).items()})
    return files


def summary(analysis: dict, unresolved: list, written: int, root: str) -> list:
    """Short script-generated summary for the agent to relay (kept under 150 words)."""
    pf = analysis["portfolio"]
    lines = [f"Wrote {written} report/graph file(s). Unresolved records: {len(unresolved)}."]
    if pf:
        inc = next((p for p in pf["periods"] if p["label"] == "inception"), None)
        lines.append(f"Wealth {money(pf['value_eur'])} EUR on {pf['common_date']}" + (f"; TWR since inception {pct(inc['twr'], inc['twr_status'])}." if inc else "."))
    c = analysis["check_counts"]
    lines.append(f"Checks: {c['ok']} ok, {c['warn']} warn, {c['fail']} fail. Reports in {root}reports/.")
    return lines
