from __future__ import annotations

import pytest

from app.control.tracking_controller import TrackingController


def test_inactive_returns_zero_command() -> None:
    controller = TrackingController()

    command = controller.update(
        error_x=0.5,
        error_y=-0.5,
        active=False,
    )

    assert command.active is False
    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_missing_error_returns_zero_command() -> None:
    controller = TrackingController()

    command = controller.update(
        error_x=None,
        error_y=None,
        active=True,
    )

    assert command.active is False
    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_proportional_command() -> None:
    controller = TrackingController(
        kp_pan=0.5,
        kp_tilt=0.25,
    )

    command = controller.update(
        error_x=0.8,
        error_y=-0.4,
        active=True,
    )

    assert command.active is True
    assert command.pan_norm == pytest.approx(0.4)
    assert command.tilt_norm == pytest.approx(-0.1)


def test_command_is_clamped() -> None:
    controller = TrackingController(
        kp_pan=2.0,
        kp_tilt=2.0,
    )

    command = controller.update(
        error_x=1.0,
        error_y=-1.0,
        active=True,
    )

    assert command.pan_norm == 1.0
    assert command.tilt_norm == -1.0


def test_invalid_limits_are_rejected() -> None:
    with pytest.raises(ValueError):
        TrackingController(
            max_pan_command=0.0,
        )
