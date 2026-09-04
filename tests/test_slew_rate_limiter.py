from __future__ import annotations

import pytest

from app.control.slew_rate_limiter import CommandSlewRateLimiter
from app.control.types import PanTiltCommand


def active_command(
    pan: float,
    tilt: float,
) -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=pan,
        tilt_norm=tilt,
        active=True,
    )


def test_first_active_command_starts_from_zero() -> None:
    limiter = CommandSlewRateLimiter()

    result = limiter.update(
        active_command(1.0, -1.0),
        timestamp_ns=1_000_000_000,
    )

    assert result.active is True
    assert result.pan_norm == 0.0
    assert result.tilt_norm == 0.0


def test_ramps_toward_positive_target() -> None:
    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=1.0,
        tilt_rate_per_s=1.0,
    )

    limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=0,
    )

    result = limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=250_000_000,
    )

    assert result.pan_norm == pytest.approx(0.25)
    assert result.tilt_norm == pytest.approx(0.25)


def test_ramps_toward_negative_target() -> None:
    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=1.0,
        tilt_rate_per_s=1.0,
    )

    limiter.update(
        active_command(-1.0, -1.0),
        timestamp_ns=1_000_000_000,
    )

    result = limiter.update(
        active_command(-1.0, -1.0),
        timestamp_ns=1_500_000_000,
    )

    assert result.pan_norm == pytest.approx(-0.5)
    assert result.tilt_norm == pytest.approx(-0.5)


def test_pan_and_tilt_have_independent_rates() -> None:
    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=1.0,
        tilt_rate_per_s=0.5,
    )

    limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=0,
    )

    result = limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=1_000_000_000,
    )

    assert result.pan_norm == pytest.approx(1.0)
    assert result.tilt_norm == pytest.approx(0.5)


def test_does_not_overshoot_target() -> None:
    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=10.0,
        tilt_rate_per_s=10.0,
    )

    limiter.update(
        active_command(0.2, -0.3),
        timestamp_ns=0,
    )

    result = limiter.update(
        active_command(0.2, -0.3),
        timestamp_ns=100_000_000,
    )

    assert result.pan_norm == pytest.approx(0.2)
    assert result.tilt_norm == pytest.approx(-0.3)


def test_inactive_stops_immediately_and_resets() -> None:
    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=1.0,
        tilt_rate_per_s=1.0,
    )

    limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=0,
    )

    limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=500_000_000,
    )

    stopped = limiter.update(
        PanTiltCommand(
            pan_norm=0.0,
            tilt_norm=0.0,
            active=False,
        ),
        timestamp_ns=600_000_000,
    )

    assert stopped.active is False
    assert stopped.pan_norm == 0.0
    assert stopped.tilt_norm == 0.0

    restarted = limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=1_000_000_000,
    )

    assert restarted.active is True
    assert restarted.pan_norm == 0.0
    assert restarted.tilt_norm == 0.0


def test_rejects_invalid_rate() -> None:
    with pytest.raises(ValueError):
        CommandSlewRateLimiter(
            pan_rate_per_s=0.0,
        )

    with pytest.raises(ValueError):
        CommandSlewRateLimiter(
            tilt_rate_per_s=-1.0,
        )


def test_rejects_non_increasing_timestamp() -> None:
    limiter = CommandSlewRateLimiter()

    limiter.update(
        active_command(1.0, 1.0),
        timestamp_ns=100,
    )

    with pytest.raises(ValueError):
        limiter.update(
            active_command(1.0, 1.0),
            timestamp_ns=100,
        )
