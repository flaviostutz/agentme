# Runtime: pytest; volatility vs CAGR quadrant classification, axis scale and SVG chart.
from decimal import Decimal

import pytest

from portfolio_manager.app import quadrant, svgchart

D = Decimal


@pytest.mark.parametrize(
    ("vol", "cagr", "key"),
    [
        ("0.05", "0.12", "holy-grail"),
        ("0.15", "0.12", "engine-room"),
        ("0.05", "0.02", "safe-haven"),
        ("0.15", "0.02", "danger-zone"),
        ("0.12", "0.08", "engine-room"),
        ("0.1199", "0.0799", "safe-haven"),
        ("0", "-0.5", "safe-haven"),
    ],
)
def test_classify_uses_12_percent_volatility_and_8_percent_cagr_as_the_boundaries(vol, cagr, key):
    assert quadrant.classify(D(vol), D(cagr)).key == key


def test_position_is_piecewise_with_the_thresholds_in_the_middle_and_clamped():
    assert quadrant.position(D("0.12"), quadrant.VOL_TICKS) == D("0.5")
    assert quadrant.position(D("0.08"), quadrant.CAGR_TICKS) == D("0.5")
    assert quadrant.position(D("-1"), quadrant.VOL_TICKS) == 0
    assert quadrant.position(D("5"), quadrant.VOL_TICKS) == 1
    assert quadrant.position(D("0.60"), quadrant.VOL_TICKS) == 1


def test_svg_is_deterministic_and_carries_the_real_numbers():
    first = svgchart.quadrant("Volatility vs CAGR", D("0.1534"), D("0.0712"))
    assert first == svgchart.quadrant("Volatility vs CAGR", D("0.1534"), D("0.0712"))
    assert first.startswith("<svg")
    assert "You: CAGR 7.1 %, volatility 15.3 %" in first
    for ref in quadrant.REFERENCES:
        assert ref.label in first


def test_svg_escapes_the_title_and_draws_values_beyond_the_axes_on_the_edge():
    svg = svgchart.quadrant("<b>&", D("3"), D("-2"))
    assert "<b>" not in svg
    assert "&lt;b&gt;&amp;" in svg
    assert "You: CAGR -200.0 %, volatility 300.0 %" in svg
