import pytest

from app.targeting.observation import (
    _apply_dead_zone,
)


def test_center_target_has_zero_error() -> None: ...


def test_target_right_and_above_center() -> None: ...


def test_returns_none_when_target_not_locked() -> None: ...


def test_dead_zone_zeroes_small_error() -> None:
    result = _apply_dead_zone(
        0.04,
        0.05,
    )

    assert result == 0.0


def test_dead_zone_zeroes_threshold() -> None:
    result = _apply_dead_zone(
        0.05,
        0.05,
    )

    assert result == 0.0


def test_dead_zone_preserves_direction() -> None:
    positive = _apply_dead_zone(
        0.20,
        0.05,
    )
    negative = _apply_dead_zone(
        -0.20,
        0.05,
    )

    assert positive > 0.0
    assert negative < 0.0
    assert abs(positive) == abs(negative)


def test_dead_zone_preserves_full_scale() -> None:
    assert (
        _apply_dead_zone(
            1.0,
            0.05,
        )
        == 1.0
    )

    assert (
        _apply_dead_zone(
            -1.0,
            0.05,
        )
        == -1.0
    )


def test_rejects_invalid_dead_zone() -> None:
    with pytest.raises(ValueError):
        _apply_dead_zone(
            0.5,
            1.0,
        )
