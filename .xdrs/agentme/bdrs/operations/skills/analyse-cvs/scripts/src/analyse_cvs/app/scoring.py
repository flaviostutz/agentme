"""Exact score arithmetic: Overall and scenario dry-run (agentme-edr-105, no float anywhere)."""

import json
from decimal import Decimal
from fractions import Fraction
from typing import Any

from analyse_cvs.shared.constants import (
    ASPECT_LIMIT,
    CREDIBILITY_SPAN,
    INVITE_ABOVE,
    NEUTRAL_CREDIBILITY,
    SCALE_MAX,
    SCALE_MIN,
    SCENARIO_LIMIT,
    SCENARIOS,
    WEIGHT_TOTAL,
)
from analyse_cvs.shared.decimals import (
    clamp,
    decimal_places,
    parse_decimal,
    round_one,
    round_one_fraction,
    show,
    show_exact,
)

Adjustments = dict[str, dict[str, Decimal]]


def _to_decimal(value: object) -> Decimal:
    if isinstance(value, str):
        return parse_decimal(value)
    if isinstance(value, Decimal) or (isinstance(value, int) and not isinstance(value, bool)):
        return Decimal(value)
    msg = f"adjustment must be a number or a string, got {value!r}"
    raise ValueError(msg)


def parse_adjustments(text: str) -> Adjustments:
    """Parse {"S2": {"<aspect>": "-0.5"}} JSON into exact decimals, reading JSON numbers as Decimal."""
    try:
        data = json.loads(text, parse_float=Decimal)
    except json.JSONDecodeError as err:
        msg = f"adjustments are not valid JSON: {err}"
        raise ValueError(msg) from err
    if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
        msg = 'adjustments must look like {"S1": {"<aspect>": "+0.5"}}'
        raise ValueError(msg)
    return {s: {a: _to_decimal(v) for a, v in per_aspect.items()} for s, per_aspect in data.items()}


def overall_exact(base: Decimal, credibility: Decimal) -> Fraction:
    """Return Base + (Credibility - 5.5) / 4.5 clamped to 1.0-10.0, as an exact fraction."""
    raw = Fraction(base) + (Fraction(credibility) - Fraction(NEUTRAL_CREDIBILITY)) / Fraction(CREDIBILITY_SPAN)
    return min(max(raw, Fraction(SCALE_MIN)), Fraction(SCALE_MAX))


def is_invited(exact: Fraction) -> bool:
    """Invite when the unrounded Overall is above 5.0."""
    return exact > Fraction(INVITE_ABOVE)


def overall(base: Decimal, credibility: Decimal) -> dict[str, Any]:
    """Return the Overall as exact value, one-decimal text and invite flag."""
    exact = overall_exact(base, credibility)
    return {
        "overall": show(round_one_fraction(exact)),
        "unrounded": show_exact(exact),
        "invited": is_invited(exact),
    }


def validate_adjustments(adjustments: Adjustments, aspects: set[str]) -> None:
    """Raise ValueError when scenarios, aspects or adjustment sizes break the limits."""
    totals: dict[str, Decimal] = {}
    for scenario, per_aspect in adjustments.items():
        if scenario not in SCENARIOS:
            msg = f"unknown scenario {scenario!r}; use {', '.join(SCENARIOS)}"
            raise ValueError(msg)
        for aspect, adj in per_aspect.items():
            if aspect not in aspects:
                msg = f"{scenario}: unknown aspect {aspect!r}"
                raise ValueError(msg)
            if abs(adj) > SCENARIO_LIMIT or decimal_places(adj) > 1:
                msg = f"{scenario} {aspect}: adjustment {adj} must be within +-{SCENARIO_LIMIT} with one decimal"
                raise ValueError(msg)
            totals[aspect] = totals.get(aspect, Decimal(0)) + adj
    for aspect, total in totals.items():
        if abs(total) > ASPECT_LIMIT:
            msg = f"{aspect}: total adjustment {total} exceeds +-{ASPECT_LIMIT} across S1-S3"
            raise ValueError(msg)


def dry_run(
    scores: dict[str, Decimal],
    base: Decimal,
    weights: dict[str, Decimal],
    adjustments: Adjustments,
) -> dict[str, Any]:
    """Apply scenario adjustments to the aspect scores and shift Base by their weighted sum."""
    validate_adjustments(adjustments, set(weights))
    new_scores = dict(scores)
    shift = Decimal(0)
    for scenario in SCENARIOS:
        for aspect, adj in adjustments.get(scenario, {}).items():
            new_scores[aspect] = clamp(new_scores[aspect] + adj)
            shift += adj * weights[aspect] / WEIGHT_TOTAL
    return {
        "aspects": {aspect: show(round_one(score)) for aspect, score in new_scores.items()},
        "base": show(round_one(clamp(base + shift))),
        "shift": show(shift),
    }
