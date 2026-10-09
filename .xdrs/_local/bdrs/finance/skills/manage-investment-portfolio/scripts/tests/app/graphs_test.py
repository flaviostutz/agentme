# Runtime: pytest; graph files: 12-month window rules, per-scope XIRR charts, account pie and the risk quadrants.
from portfolio_manager.app.reports import graphs


def row(label: str, to: str, xirr: str | None = "0.05", partial: bool = False) -> dict:
    return {
        "label": label,
        "from": "2024-01-31",
        "to": to,
        "partial": partial,
        "xirr": xirr,
        "xirr_status": "complete" if xirr is not None else "unavailable",
        "end_value": "100.00",
        "twr": "0.01",
        "twr_status": "complete",
    }


def months(count: int) -> list:
    return [row(f"month 2024-{m:02d}", f"2024-{m:02d}-28") for m in range(1, count + 1)]


def analysis(**extra) -> dict:
    portfolio = {
        "periods": extra.pop("periods", []),
        "accounts": [
            {"account": "Alpha", "value_eur": "100.00"},
            {"account": "Beta", "value_eur": "-5.00"},
            {"account": "Gamma", "value_eur": None},
        ],
    }
    return {"portfolio": portfolio, "accounts": extra.pop("accounts", {}), **extra}


def trend(status: str = "complete") -> list:
    return [
        {
            "date": f"2024-{m:02d}-28",
            "twr": "0.01",
            "twr_status": status,
            "xirr": "0.02",
            "xirr_status": status,
            "net_flows": str(100 * m),
        }
        for m in range(1, 4)
    ]


def test_twelve_month_charts_need_a_full_window():
    short = graphs.build(analysis(trend=trend(), window={"full": False}))
    assert not [name for name in short if name.endswith("-12m.mmd")]
    full = graphs.build(analysis(trend=trend(), window={"full": True}))
    assert {"twr-12m.mmd", "xirr-12m.mmd", "net-flows-12m.mmd"} <= set(full)
    assert "Cumulative TWR (12 months)" in full["twr-12m.mmd"]
    assert "Cumulative XIRR (12 months)" in full["xirr-12m.mmd"]
    assert "    line [" in full["net-flows-12m.mmd"]
    assert "    bar [" not in full["net-flows-12m.mmd"]


def test_twelve_month_charts_only_use_complete_points():
    out = graphs.build(analysis(trend=trend("approximate"), window={"full": True}))
    assert "twr-12m.mmd" not in out
    assert "xirr-12m.mmd" not in out


def test_account_pie_leaves_out_negative_and_unknown_values():
    pie = graphs.build(analysis())["wealth-by-account.mmd"]
    assert '"Alpha" : 100.00' in pie
    assert "Beta" not in pie
    assert "Gamma" not in pie


def test_monthly_xirr_chart_covers_the_latest_24_month_rows_and_skips_partial_ones():
    rows = [row(f"month {2020 + i // 12}-{i % 12 + 1:02d}", f"{2020 + i // 12}-{i % 12 + 1:02d}-28") for i in range(30)]
    rows.append(row("month 2022-07 (to date)", "2022-07-10", partial=True))
    chart = graphs.build(analysis(periods=rows))["monthly-xirr-portfolio.mmd"]
    assert chart.count('"20') == 23  # 24 latest rows minus the partial one
    assert "2022-07-10" not in chart


def test_xirr_charts_need_two_points_and_skip_unavailable_xirr():
    one = [row("month 2024-01", "2024-01-31"), row("month 2024-02", "2024-02-29", xirr=None)]
    assert "monthly-xirr-portfolio.mmd" not in graphs.build(analysis(periods=one))


def test_yearly_xirr_chart_is_built_per_portfolio_and_account_with_unique_slugs():
    years = [row("year 2023", "2023-12-31"), row("year 2024", "2024-12-31")]
    accounts = {"Rev A/B": {"periods": years}, "rev a b": {"periods": years}, "Portfolio": {"periods": years}}
    out = graphs.build(analysis(periods=years, accounts=accounts))
    names = {n for n in out if n.startswith("yearly-xirr-")}
    assert names == {
        "yearly-xirr-portfolio.mmd",
        "yearly-xirr-portfolio-2.mmd",
        "yearly-xirr-rev-a-b.mmd",
        "yearly-xirr-rev-a-b-2.mmd",
    }
    assert '"2023", "2024"' in out["yearly-xirr-portfolio.mmd"]


def test_risk_charts_need_both_measures_and_two_calendar_years():
    risk = {
        "volatility": "0.15",
        "cagr": "0.09",
        "yearly": [
            {"year": "2023", "twr": "0.1", "status": "complete"},
            {"year": "2024", "twr": "0.2", "status": "complete"},
        ],
        "last_12m": {"available": False, "reason": "n/a"},
    }
    out = graphs.build(analysis(risk=risk))
    assert out["quadrant-inception.svg"].startswith("<svg")
    assert "quadrant-12m.svg" not in out
    assert "CAGR per calendar year" in out["cagr-per-year.mmd"]
    risk["last_12m"] = {"available": True, "volatility": "0.05", "cagr": None}
    risk["yearly"] = risk["yearly"][:1]
    out = graphs.build(analysis(risk=risk))
    assert "quadrant-12m.svg" not in out
    assert "cagr-per-year.mmd" not in out
