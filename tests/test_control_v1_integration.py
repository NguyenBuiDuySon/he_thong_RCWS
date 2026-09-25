import pytest

from app.control.gamepad import (
    GamepadCommandMapper,
    GamepadState,
)
from app.control.mode import (
    CommandArbiter,
    ControlMode,
)
from app.control.slew_rate_limiter import (
    CommandSlewRateLimiter,
)
from app.control.types import PanTiltCommand

_NS_PER_SECOND = 1_000_000_000


def make_vision_command(
    pan: float,
    tilt: float,
    *,
    active: bool = True,
) -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=pan,
        tilt_norm=tilt,
        active=active,
    )


def make_gamepad_state(
    *,
    connected: bool = True,
    pan: float = 0.0,
    tilt: float = 0.0,
) -> GamepadState:
    return GamepadState(
        connected=connected,
        pan_axis=pan,
        tilt_axis=tilt,
    )


def test_manual_gamepad_reaches_output() -> None:
    mapper = GamepadCommandMapper(
        dead_zone=0.10,
    )

    arbiter = CommandArbiter(
        initial_mode=ControlMode.MANUAL_GAMEPAD,
    )

    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=2.0,
        tilt_rate_per_s=2.0,
    )

    state = make_gamepad_state(
        pan=1.0,
    )

    manual = mapper.update(state)

    vision = make_vision_command(
        -0.5,
        0.5,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert selected == manual

    first = limiter.update(
        selected,
        timestamp_ns=0,
    )

    assert first.active
    assert first.pan_norm == 0.0

    second = limiter.update(
        selected,
        timestamp_ns=(_NS_PER_SECOND // 2),
    )

    assert second.pan_norm == pytest.approx(1.0)
    assert second.tilt_norm == pytest.approx(0.0)


def test_auto_vision_ignores_manual_input() -> None:
    mapper = GamepadCommandMapper()

    arbiter = CommandArbiter(
        initial_mode=ControlMode.AUTO_VISION,
    )

    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=2.0,
        tilt_rate_per_s=2.0,
    )

    manual = mapper.update(
        make_gamepad_state(
            pan=-1.0,
            tilt=-1.0,
        )
    )

    vision = make_vision_command(
        0.4,
        -0.2,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert selected == vision

    limiter.update(
        selected,
        timestamp_ns=0,
    )

    output = limiter.update(
        selected,
        timestamp_ns=(_NS_PER_SECOND // 4),
    )

    assert output.pan_norm == pytest.approx(0.4)
    assert output.tilt_norm == pytest.approx(-0.2)


def test_mode_switch_inserts_stop_and_resets_limiter() -> None:
    mapper = GamepadCommandMapper()

    arbiter = CommandArbiter(
        initial_mode=ControlMode.MANUAL_GAMEPAD,
    )

    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=2.0,
        tilt_rate_per_s=2.0,
    )

    manual = mapper.update(
        make_gamepad_state(
            pan=1.0,
        )
    )

    vision = make_vision_command(
        0.6,
        0.3,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    limiter.update(
        selected,
        timestamp_ns=0,
    )

    moving = limiter.update(
        selected,
        timestamp_ns=(_NS_PER_SECOND // 2),
    )

    assert moving.pan_norm == pytest.approx(1.0)

    changed = arbiter.set_mode(ControlMode.AUTO_VISION)

    assert changed

    transition = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert not transition.active

    stopped = limiter.update(
        transition,
        timestamp_ns=600_000_000,
    )

    assert not stopped.active
    assert stopped.pan_norm == 0.0
    assert stopped.tilt_norm == 0.0

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    restart = limiter.update(
        selected,
        timestamp_ns=700_000_000,
    )

    # Limiter starts again from zero after STOP.
    assert restart.active
    assert restart.pan_norm == 0.0
    assert restart.tilt_norm == 0.0

    output = limiter.update(
        selected,
        timestamp_ns=1_200_000_000,
    )

    assert output.pan_norm == pytest.approx(0.6)
    assert output.tilt_norm == pytest.approx(0.3)


def test_gamepad_disconnect_stops_manual_mode() -> None:
    mapper = GamepadCommandMapper()

    arbiter = CommandArbiter(
        initial_mode=ControlMode.MANUAL_GAMEPAD,
    )

    limiter = CommandSlewRateLimiter()

    manual = mapper.update(
        make_gamepad_state(
            connected=False,
            pan=1.0,
            tilt=-1.0,
        )
    )

    vision = make_vision_command(
        0.5,
        -0.5,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    output = limiter.update(
        selected,
        timestamp_ns=0,
    )

    assert not output.active
    assert output.pan_norm == 0.0
    assert output.tilt_norm == 0.0


def test_gamepad_disconnect_does_not_stop_auto_vision() -> None:
    mapper = GamepadCommandMapper()

    arbiter = CommandArbiter(
        initial_mode=ControlMode.AUTO_VISION,
    )

    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=2.0,
        tilt_rate_per_s=2.0,
    )

    manual = mapper.update(
        make_gamepad_state(
            connected=False,
        )
    )

    vision = make_vision_command(
        0.3,
        -0.2,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    assert selected == vision

    first = limiter.update(
        selected,
        timestamp_ns=0,
    )

    assert first.active

    output = limiter.update(
        selected,
        timestamp_ns=200_000_000,
    )

    assert output.active
    assert output.pan_norm == pytest.approx(0.3)
    assert output.tilt_norm == pytest.approx(-0.2)


def test_target_lost_stops_auto_vision() -> None:
    mapper = GamepadCommandMapper()

    arbiter = CommandArbiter(
        initial_mode=ControlMode.AUTO_VISION,
    )

    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=2.0,
        tilt_rate_per_s=2.0,
    )

    manual = mapper.update(make_gamepad_state())

    vision = make_vision_command(
        0.4,
        0.2,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision,
    )

    limiter.update(
        selected,
        timestamp_ns=0,
    )

    moving = limiter.update(
        selected,
        timestamp_ns=250_000_000,
    )

    assert moving.active
    assert moving.pan_norm == pytest.approx(0.4)

    vision_lost = make_vision_command(
        0.0,
        0.0,
        active=False,
    )

    selected = arbiter.select(
        manual_command=manual,
        auto_vision_command=vision_lost,
    )

    stopped = limiter.update(
        selected,
        timestamp_ns=300_000_000,
    )

    assert not stopped.active
    assert stopped.pan_norm == 0.0
    assert stopped.tilt_norm == 0.0
