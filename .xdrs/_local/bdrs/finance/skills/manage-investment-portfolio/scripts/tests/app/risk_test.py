# Runtime: pytest; risk measures from inception, over the last 12 calendar months and per calendar year.
import calendar
from datetime import date, timedelta
from decimal import Decimal

from portfolio_manager.app import risk


def month(year: int, m: int, twr: str | None = "0.01", partial: bool = False, first_day: int = 1) -> dict:
    """A month row shaped like analyze.periods output."""
    last = calendar.monthrange(year, m)[1]
    start = date(year, m, 1) - timedelta(days=1)
    return {
        "label": f"month {year}-{m:02d}" + (" (to date)" if partial else ""),
        "from": start.isoformat(),
        "to": date(year, m, last).isoformat(),
        "first_day": date(year, m, first_day).isoformat(),
        "partial": partial,
        "twr": twr,
        "twr_status": "complete",
    }


def year(y: int, twr: str | None = "0.10", partial: bool = False, start: str | None = None) -> dict:
    return {
        "label": f"year {y}" + (" (to date)" if partial else ""),
        "from": start or f"{y - 1}-12-31",
        "to": f"{y}-12-31",
        "first_day": f"{y}-01-01",
        "partial": partial,
        "twr": twr,
        "twr_status": "complete",
    }


def twelve(start_year: int = 2024, start_month: int = 1) -> list:
    rows, y, m = [], start_year, start_month
    for _ in range(12):
        rows.append(month(y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return rows


def test_twelve_consecutive_complete_months_give_the_window_measures():
    out = risk.last_12_months(twelve())
    assert out["available"] is True
    assert (out["from"], out["to"]) == ("2024-01-01", "2024-12-31")
    assert out["months"] == 12
    assert round(float(out["cagr"]), 6) == round(1.01**12 - 1, 6)
    assert Decimal(out["volatility"]) == 0


def test_only_the_latest_twelve_months_count():
    rows = [month(2023, 12, "0.5"), *twelve()]
    out = risk.last_12_months(rows)
    assert out["from"] == "2024-01-01"


def test_a_short_history_is_not_available():
    out = risk.last_12_months(twelve()[:11])
    assert out["available"] is False
    assert "12 complete months" in out["reason"]


def test_a_gap_month_is_not_available():
    rows = twelve()
    del rows[5]
    rows.insert(0, month(2023, 12))
    out = risk.last_12_months(rows)
    assert out["available"] is False
    assert "consecutive" in out["reason"]


def test_a_first_month_that_starts_late_is_not_available():
    rows = twelve()
    rows[0] = month(2024, 1, first_day=15)
    out = risk.last_12_months(rows)
    assert out["available"] is False


def test_a_month_without_twr_is_not_available():
    rows = twelve()
    rows[3] = month(2024, 4, twr=None)
    assert risk.last_12_months(rows) == {"available": False, "reason": "n/a (a month has no TWR)"}


def test_partial_months_never_count():
    rows = [*twelve()[:11], month(2024, 12, partial=True)]
    assert risk.last_12_months(rows)["available"] is False


def test_yearly_returns_keep_only_full_calendar_years():
    rows = [
        year(2022, start="2022-03-10"),  # history starts mid-year
        year(2023),
        year(2024, "0.2"),
        year(2025, partial=True),
        year(2026, None),
    ]
    assert [y["year"] for y in risk.yearly_returns(rows)] == ["2023", "2024"]


def test_measures_expose_inception_window_and_yearly_parts():
    out = risk.measures([*twelve(), year(2024)])
    assert out["last_12m"]["available"] is True
    assert out["yearly"][0]["year"] == "2024"
    assert out["months"] == 12
