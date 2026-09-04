import pytest

from app.targeting.filter import (
    TrackingErrorFilter,
)


def test_first_sample_passes_through() -> None:
    filter_ = TrackingErrorFilter(tau_ms=70.0)

    result = filter_.update(
        target_id=1,
        x=0.4,
        y=-0.2,
        timestamp_ns=1_000_000_000,
    )

    assert result.x == 0.4
    assert result.y == -0.2


def test_same_direction_is_smoothed() -> None:
    filter_ = TrackingErrorFilter(tau_ms=70.0)

    filter_.update(
        target_id=1,
        x=0.2,
        y=0.0,
        timestamp_ns=1_000_000_000,
    )

    result = filter_.update(
        target_id=1,
        x=0.8,
        y=0.0,
        timestamp_ns=1_033_000_000,
    )

    assert 0.2 < result.x < 0.8


def test_zero_input_stops_axis_immediately() -> None:
    filter_ = TrackingErrorFilter(tau_ms=70.0)

    filter_.update(
        target_id=1,
        x=0.5,
        y=-0.4,
        timestamp_ns=1_000_000_000,
    )

    result = filter_.update(
        target_id=1,
        x=0.0,
        y=0.0,
        timestamp_ns=1_033_000_000,
    )

    assert result.x == 0.0
    assert result.y == 0.0


def test_direction_change_does_not_keep_old_sign() -> None:
    filter_ = TrackingErrorFilter(tau_ms=70.0)

    filter_.update(
        target_id=1,
        x=0.5,
        y=0.0,
        timestamp_ns=1_000_000_000,
    )

    result = filter_.update(
        target_id=1,
        x=-0.5,
        y=0.0,
        timestamp_ns=1_033_000_000,
    )

    assert result.x < 0.0


def test_new_target_resets_filter_history() -> None:
    filter_ = TrackingErrorFilter(tau_ms=70.0)

    filter_.update(
        target_id=1,
        x=0.8,
        y=0.0,
        timestamp_ns=1_000_000_000,
    )

    result = filter_.update(
        target_id=2,
        x=-0.2,
        y=0.3,
        timestamp_ns=1_033_000_000,
    )

    assert result.x == pytest.approx(-0.2)
    assert result.y == pytest.approx(0.3)
