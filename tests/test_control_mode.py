from app.control.mode import (
    CommandArbiter,
    ControlMode,
)
from app.control.types import PanTiltCommand


def make_command(
    pan: float,
    tilt: float,
) -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=pan,
        tilt_norm=tilt,
        active=True,
    )


def test_auto_vision_is_initial_mode() -> None:
    arbiter = CommandArbiter()

    manual = make_command(
        0.8,
        -0.3,
    )
    vision = make_command(
        0.2,
        0.4,
    )

    command = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert arbiter.mode is ControlMode.AUTO_VISION
    assert command == vision


def test_manual_mode_selects_manual_command() -> None:
    arbiter = CommandArbiter(
        initial_mode=ControlMode.MANUAL_GAMEPAD,
    )

    manual = make_command(
        0.8,
        -0.3,
    )
    vision = make_command(
        0.2,
        0.4,
    )

    command = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert command == manual


def test_mode_switch_outputs_stop_once() -> None:
    arbiter = CommandArbiter()

    manual = make_command(
        0.8,
        -0.3,
    )
    vision = make_command(
        0.2,
        0.4,
    )

    changed = arbiter.set_mode(ControlMode.MANUAL_GAMEPAD)

    assert changed

    stop = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert not stop.active
    assert stop.pan_norm == 0.0
    assert stop.tilt_norm == 0.0

    next_command = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert next_command == manual


def test_setting_same_mode_does_not_interrupt() -> None:
    arbiter = CommandArbiter()

    changed = arbiter.set_mode(ControlMode.AUTO_VISION)

    assert not changed

    vision = make_command(
        0.2,
        0.4,
    )

    command = arbiter.select(
        manual_command=make_command(
            0.8,
            -0.3,
        ),
        auto_vision_command=vision,
    )

    assert command == vision

def test_auto_mode_ignores_manual_command_changes() -> None:
    arbiter = CommandArbiter(
        initial_mode=ControlMode.AUTO_VISION,
    )

    vision = make_command(
        0.4,
        -0.2,
    )

    first = arbiter.select(
        manual_command=make_command(
            -1.0,
            1.0,
        ),
        auto_vision_command=vision,
    )

    second = arbiter.select(
        manual_command=make_command(
            1.0,
            -1.0,
        ),
        auto_vision_command=vision,
    )

    assert first == vision
    assert second == vision