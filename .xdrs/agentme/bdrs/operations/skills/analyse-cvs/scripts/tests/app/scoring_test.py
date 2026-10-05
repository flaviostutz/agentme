# Python 3.11+ pytest suite; run with: make test
from decimal import Decimal

import pytest

from analyse_cvs.app.scoring import (
    dry_run,
    is_invited,
    overall,
    overall_exact,
    parse_adjustments,
    validate_adjustments,
)

D = Decimal
WEIGHTS = {"Delivery": D(30), "Collaboration": D(40), "Domain": D(30)}
SCORES = {"Delivery": D("7.0"), "Collaboration": D("7.0"), "Domain": D("7.0")}


def test_overall_rounds_half_up():
    assert overall(D("7.0"), D("7.0")) == {"overall": "7.3", "unrounded": "7.3333", "invited": True}


def test_threshold_uses_the_unrounded_value():
    assert overall(D("5.0"), D("5.5"))["invited"] is False
    just_above = overall(D("5.0"), D("5.6"))
    assert just_above["overall"] == "5.0"
    assert just_above["invited"] is True


def test_overall_is_clamped():
    assert overall(D("10.0"), D("10.0"))["overall"] == "10.0"
    assert overall(D("1.0"), D("1.0"))["overall"] == "1.0"
    assert not is_invited(overall_exact(D("1.0"), D("1.0")))


def test_dry_run_shifts_base_by_weighted_adjustment():
    result = dry_run(SCORES, D("7.0"), WEIGHTS, {"S2": {"Collaboration": D("-0.5")}})
    assert result == {
        "aspects": {"Delivery": "7.0", "Collaboration": "6.5", "Domain": "7.0"},
        "base": "6.8",
        "shift": "-0.2",
    }


def test_dry_run_without_adjustments_changes_nothing():
    result = dry_run(SCORES, D("7.0"), WEIGHTS, {})
    assert result["base"] == "7.0"
    assert result["aspects"] == {"Delivery": "7.0", "Collaboration": "7.0", "Domain": "7.0"}


def test_dry_run_clamps_scores():
    result = dry_run({**SCORES, "Domain": D("10.0")}, D("10.0"), WEIGHTS, {"S1": {"Domain": D("1.0")}})
    assert result["aspects"]["Domain"] == "10.0"
    assert result["base"] == "10.0"


@pytest.mark.parametrize(
    ("adjustments", "message"),
    [
        ({"S4": {"Domain": D("0.5")}}, "unknown scenario"),
        ({"S1": {"Speed": D("0.5")}}, "unknown aspect"),
        ({"S1": {"Domain": D("1.5")}}, "within"),
        ({"S1": {"Domain": D("0.55")}}, "one decimal"),
        ({"S1": {"Domain": D("1.0")}, "S2": {"Domain": D("1.0")}, "S3": {"Domain": D("1.0")}}, "exceeds"),
    ],
)
def test_validate_adjustments_rejects(adjustments, message):
    with pytest.raises(ValueError, match=message):
        validate_adjustments(adjustments, set(WEIGHTS))


def test_validate_adjustments_accepts_limits():
    validate_adjustments(
        {"S1": {"Domain": D("1.0")}, "S2": {"Domain": D("1.0")}, "S3": {"Domain": D("-1.0")}}, set(WEIGHTS)
    )


def test_parse_adjustments_reads_exact_decimals():
    parsed = parse_adjustments('{"S1": {"Domain": 0.1, "Delivery": "-0.5", "Collaboration": 1}}')
    assert parsed == {"S1": {"Domain": D("0.1"), "Delivery": D("-0.5"), "Collaboration": D(1)}}


@pytest.mark.parametrize("text", ["{", "[]", '{"S1": 1}', '{"S1": {"Domain": true}}', '{"S1": {"Domain": null}}'])
def test_parse_adjustments_rejects(text):
    with pytest.raises(ValueError, match="adjustment"):
        parse_adjustments(text)
