import pytest

from app.control.gamepad import (
    GamepadCommandMapper,
    GamepadState,
)


def test_disconnected_gamepad_is_inactive() -> None:
    mapper = GamepadCommandMapper()

    command = mapper.update(
        GamepadState(
            connected=False,
            pan_axis=1.0,
            tilt_axis=1.0,
        )
    )

    assert not command.active
    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_centered_gamepad_commands_zero() -> None:
    mapper = GamepadCommandMapper()

    command = mapper.update(
        GamepadState(
            connected=True,
            pan_axis=0.0,
            tilt_axis=0.0,
        )
    )

    assert command.active
    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_dead_zone_removes_small_input() -> None:
    mapper = GamepadCommandMapper(
        dead_zone=0.10,
    )

    command = mapper.update(
        GamepadState(
            connected=True,
            pan_axis=0.05,
            tilt_axis=-0.08,
        )
    )

    assert command.pan_norm == 0.0
    assert command.tilt_norm == 0.0


def test_full_pan_axis_maps_to_full_command() -> None:
    mapper = GamepadCommandMapper()

    command = mapper.update(
        GamepadState(
            connected=True,
            pan_axis=1.0,
            tilt_axis=0.0,
        )
    )

    assert command.pan_norm == pytest.approx(1.0)


def test_tilt_axis_is_inverted_by_default() -> None:
    mapper = GamepadCommandMapper()

    command = mapper.update(
        GamepadState(
            connected=True,
            pan_axis=0.0,
            tilt_axis=-1.0,
        )
    )

    assert command.tilt_norm == pytest.approx(1.0)


def test_command_limit_scales_output() -> None:
    mapper = GamepadCommandMapper(
        max_pan_command=0.5,
        max_tilt_command=0.25,
    )

    command = mapper.update(
        GamepadState(
            connected=True,
            pan_axis=1.0,
            tilt_axis=-1.0,
        )
    )

    assert command.pan_norm == pytest.approx(0.5)

    assert command.tilt_norm == pytest.approx(0.25)


def test_axis_values_are_clamped() -> None:
    mapper = GamepadCommandMapper()

    command = mapper.update(
        GamepadState(
            connected=True,
            pan_axis=2.0,
            tilt_axis=-2.0,
        )
    )

    assert command.pan_norm == pytest.approx(1.0)

    assert command.tilt_norm == pytest.approx(1.0)
