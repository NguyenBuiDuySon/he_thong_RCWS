import pytest

from app.targeting.motion import (
    MotionEstimate,
)
from app.targeting.search import SearchState
from app.targeting.search_command import (
    SearchCommandGenerator,
)


def test_inactive_returns_stop() -> None:
    generator = SearchCommandGenerator()

    command = generator.update(
        state=SearchState.INACTIVE,
        motion=MotionEstimate(),
    )

    assert command.active is False
    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_reacquire_holds_camera() -> None:
    generator = SearchCommandGenerator()

    command = generator.update(
        state=SearchState.REACQUIRE,
        motion=MotionEstimate(
            direction_x=1,
            sample_count=10,
        ),
    )

    assert command.active is False
    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_coast_follows_loss_direction() -> None:
    generator = SearchCommandGenerator(
        coast_command=0.2,
    )

    command = generator.update(
        state=SearchState.COAST,
        motion=MotionEstimate(
            direction_x=-1,
            direction_y=1,
            sample_count=20,
        ),
    )

    assert command.active is True
    assert command.pan_norm == pytest.approx(-0.2)
    assert command.tilt_norm == pytest.approx(0.2)


def test_coast_without_motion_stops() -> None:
    generator = SearchCommandGenerator()

    command = generator.update(
        state=SearchState.COAST,
        motion=MotionEstimate(),
    )

    assert command.active is False


def test_search_starts_in_loss_direction() -> None:
    generator = SearchCommandGenerator(
        search_command=0.25,
        sweep_leg_frames=10,
    )

    command = generator.update(
        state=SearchState.SEARCHING,
        motion=MotionEstimate(
            dx_norm_per_frame=-0.02,
            direction_x=-1,
            sample_count=20,
        ),
        search_age_frames=0,
    )

    assert command.active is True
    assert command.pan_norm == pytest.approx(-0.25)
    assert command.tilt_norm == 0.0


def test_search_reverses_after_one_leg() -> None:
    generator = SearchCommandGenerator(
        search_command=0.25,
        sweep_leg_frames=10,
    )

    command = generator.update(
        state=SearchState.SEARCHING,
        motion=MotionEstimate(
            dx_norm_per_frame=-0.02,
            direction_x=-1,
            sample_count=20,
        ),
        search_age_frames=10,
    )

    assert command.pan_norm == pytest.approx(0.25)


def test_vertical_motion_uses_tilt_sweep() -> None:
    generator = SearchCommandGenerator(
        search_command=0.2,
    )

    command = generator.update(
        state=SearchState.SEARCHING,
        motion=MotionEstimate(
            dx_norm_per_frame=0.0,
            dy_norm_per_frame=-0.02,
            direction_x=0,
            direction_y=-1,
            sample_count=20,
        ),
    )

    assert command.pan_norm == 0.0
    assert command.tilt_norm == pytest.approx(-0.2)


def test_lost_returns_stop() -> None:
    generator = SearchCommandGenerator()

    command = generator.update(
        state=SearchState.LOST,
        motion=MotionEstimate(
            direction_x=1,
            sample_count=20,
        ),
    )

    assert command.active is False


def test_search_prefers_pan_when_both_axes_move() -> None:
    generator = SearchCommandGenerator(
        search_command=0.2,
    )

    command = generator.update(
        state=SearchState.SEARCHING,
        motion=MotionEstimate(
            dx_norm_per_frame=-0.003,
            dy_norm_per_frame=0.03,
            direction_x=-1,
            direction_y=1,
            sample_count=100,
        ),
    )

    assert command.pan_norm == pytest.approx(-0.2)
    assert command.tilt_norm == 0.0
