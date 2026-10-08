"""Cumulative results since the start of a window, sampled at the given dates (month-ends)."""

from collections.abc import Callable


def cumulative(metrics: Callable, view, start: str, days: list) -> list:
    """TWR, XIRR, net flows and wealth from `start` to each day after it; unavailable values stay None, never 0."""
    rows = []
    for day in days:
        if day <= start:
            continue
        m = metrics(view, start, day)
        rows.append(
            {
                "date": day,
                "wealth": m["end_value"],
                "twr": m["twr"],
                "twr_status": m["twr_status"],
                "xirr": m["xirr"],
                "xirr_status": m["xirr_status"],
                "net_flows": m["net_flows"],
            }
        )
    return rows
