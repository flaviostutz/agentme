"""Volatility vs CAGR quadrant: thresholds, classification, calibrated chart scales and the reference ranges per asset type."""

from decimal import Decimal
from typing import NamedTuple

VOL_HIGH = Decimal("0.12")
CAGR_HIGH = Decimal("0.08")
# Piecewise scale breakpoints: each segment gets the same share of the axis so the 12 % and 8 % thresholds sit in the middle.
VOL_TICKS = (Decimal(0), Decimal("0.05"), Decimal("0.12"), Decimal("0.20"), Decimal("0.60"))
CAGR_TICKS = (Decimal(0), Decimal("0.04"), Decimal("0.08"), Decimal("0.12"), Decimal("0.20"))


class Quadrant(NamedTuple):
    key: str
    name: str
    profile: str
    description: str
    investor: str


class Reference(NamedTuple):
    """Where an asset type usually sits: volatility and CAGR ranges (the top of an open range is the axis end)."""

    label: str
    vol_from: Decimal
    vol_to: Decimal
    cagr_from: Decimal
    cagr_to: Decimal


QUADRANTS = {
    "holy-grail": Quadrant(
        "holy-grail",
        "The Holy Grail",
        "High CAGR, low volatility",
        "Exceptional returns with smooth growth. Rare in public markets.",
        "Everyone (ideal, but hard to find).",
    ),
    "engine-room": Quadrant(
        "engine-room",
        "The Engine Room",
        "High CAGR, high volatility",
        "Strong long-term growth, but it needs a strong stomach for massive price drops.",
        "Aggressive investors with long time horizons (10+ years).",
    ),
    "safe-haven": Quadrant(
        "safe-haven",
        "The Safe Haven",
        "Low CAGR, low volatility",
        "Capital preservation: it will not make you rich quickly, but you will not lose sleep.",
        "Conservative investors or those needing the cash soon (1-3 years).",
    ),
    "danger-zone": Quadrant(
        "danger-zone",
        "The Danger Zone",
        "Low CAGR, high volatility",
        "The worst combination: high anxiety for little to no long-term reward.",
        "Nobody (avoid or exit these positions).",
    ),
}

REFERENCES = (
    Reference("Cash, short bonds", Decimal(0), Decimal("0.05"), Decimal(0), Decimal("0.04")),
    Reference("Bonds, dividend stocks", Decimal("0.05"), Decimal("0.12"), Decimal("0.04"), Decimal("0.08")),
    Reference("Broad equities", Decimal("0.12"), Decimal("0.20"), Decimal("0.08"), Decimal("0.20")),
    Reference("EM, tech, crypto", Decimal("0.20"), Decimal("0.60"), Decimal("0.08"), Decimal("0.20")),
)


def classify(volatility: Decimal, cagr: Decimal) -> Quadrant:
    """The quadrant for a portfolio; volatility at or above 12 % and CAGR at or above 8 % count as high."""
    high_vol, high_cagr = volatility >= VOL_HIGH, cagr >= CAGR_HIGH
    if high_cagr:
        return QUADRANTS["engine-room" if high_vol else "holy-grail"]
    return QUADRANTS["danger-zone" if high_vol else "safe-haven"]


def position(value: Decimal, ticks: tuple) -> Decimal:
    """Place a value on the piecewise axis: 0 at the first tick, 1 at the last, clamped to that range."""
    if value <= ticks[0]:
        return Decimal(0)
    if value >= ticks[-1]:
        return Decimal(1)
    segments = len(ticks) - 1
    for i in range(segments):
        if value <= ticks[i + 1]:
            return (Decimal(i) + (value - ticks[i]) / (ticks[i + 1] - ticks[i])) / segments
    return Decimal(1)
