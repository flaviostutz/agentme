# Runtime: pytest; period rows and window metrics on a plain in-memory view (no mocks).

from decimal import Decimal

from portfolio_manager.app import analyze


class View:
    """Minimal valuation view: fixed values per date, flows given, EUR so no FX effect applies."""

    ccy = "EUR"

    def __init__(self, values: dict, flows: list | None = None, status: str = "complete") -> None:
        self.values, self._flows, self.status = values, flows or [], status

    def value(self, day: str) -> tuple:
        return (Decimal(self.values[day]), self.status) if day in self.values else (None, "unavailable")

    def flows(self) -> list:
        return self._flows


def labels(rows: list) -> list:
    return [r["label"] for r in rows]


def test_year_to_date_appears_once_labelled_to_date_and_there_is_no_ytd_row():
    rows = analyze.periods("2025-03-15", "2026-03-15")
    assert [r for r in labels(rows) if r.startswith("year")] == ["year 2025", "year 2026 (to date)"]
    assert not [r for r in labels(rows) if r.startswith("ytd")]
    year = next(r for r in rows if r["label"] == "year 2026 (to date)")
    assert year["partial"] is True and year["complete_through"] == "2026-03-15"
    assert next(r for r in rows if r["label"] == "year 2025")["complete_through"] is None


def test_first_day_is_the_day_after_the_opening_value_except_for_inception():
    rows = {r["label"]: r for r in analyze.periods("2025-01-31", "2026-02-10")}
    assert rows["inception"]["first_day"] == "2025-01-31"
    assert (
        rows["year 2026 (to date)"]["from"] == "2025-12-31" and rows["year 2026 (to date)"]["first_day"] == "2026-01-01"
    )
    assert rows["month 2025-02"]["first_day"] == "2025-02-01"


def test_a_month_cut_by_the_last_date_is_partial_but_a_full_month_is_not():
    assert "month 2026-02 (to date)" in labels(analyze.periods("2026-01-01", "2026-02-10"))
    assert "month 2026-02" in labels(analyze.periods("2026-01-01", "2026-02-28"))


def test_every_row_has_its_own_window_so_xirr_covers_exactly_the_row_period():
    rows = {r["label"]: r for r in analyze.periods("2024-01-31", "2026-06-30")}
    assert rows["year 2026 (to date)"]["from"] == "2025-12-31"
    assert rows["month 2026-02"]["from"] == "2026-01-31" and rows["month 2026-02"]["to"] == "2026-02-28"
    assert all("xirr_from" not in r for r in rows.values())


def test_window_labels_show_months():
    assert analyze.window_label(365) == "12mon"
    assert analyze.window_label(97) == "3.2mon"


def test_metrics_report_the_length_of_the_row_period_as_window():
    view = View({"2025-01-01": "100", "2025-07-01": "100", "2026-01-01": "110"})
    year = analyze.metrics(view, "2025-01-01", "2026-01-01")
    assert year["window"] == "12mon" and year["window_days"] == 365 and year["xirr"] is not None
    half = analyze.metrics(view, "2025-07-01", "2026-01-01")
    assert half["window"] == "6mon" and half["window_days"] == 184


def test_february_month_gets_an_xirr_over_its_28_days():
    view = View({"2026-01-31": "100", "2026-02-28": "101"})
    out = analyze.metrics(view, "2026-01-31", "2026-02-28")
    assert out["window_days"] == 28 and out["xirr"] is not None


def test_xirr_under_28_days_is_n_a_with_the_reason_and_still_gives_a_gain():
    view = View({"2025-01-01": "100", "2025-01-12": "101"})
    out = analyze.metrics(view, "2025-01-01", "2025-01-12")
    assert out["xirr"] is None and out["xirr_reason"] == "n/a (<28d)" and out["gain"] == "1"


def test_period_return_status_follows_the_valuation_statuses():
    values = {"2025-01-01": "100", "2025-03-01": "110"}
    assert analyze.metrics(View(values), "2025-01-01", "2025-03-01")["period_return_status"] == "complete"
    assert analyze.metrics(View(values, status="interpolated"), "2025-01-01", "2025-03-01")["period_return_status"] == (
        "interpolated"
    )
