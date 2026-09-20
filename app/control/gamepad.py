from __future__ import annotations

from dataclasses import dataclass

from app.control.types import PanTiltCommand


@dataclass(frozen=True, slots=True)
class GamepadState:
    connected: bool
    pan_axis: float
    tilt_axis: float
    mode_button_pressed: bool = False


def _apply_axis_dead_zone(
    value: float,
    dead_zone: float,
) -> float:
    if not 0.0 <= dead_zone < 1.0:
        raise ValueError("dead_zone must satisfy 0 <= value < 1")

    value = max(
        -1.0,
        min(
            1.0,
            value,
        ),
    )

    magnitude = abs(value)

    if magnitude <= dead_zone:
        return 0.0

    scaled = (magnitude - dead_zone) / (1.0 - dead_zone)

    return scaled if value > 0.0 else -scaled


class GamepadCommandMapper:
    def __init__(
        self,
        *,
        dead_zone: float = 0.10,
        max_pan_command: float = 1.0,
        max_tilt_command: float = 1.0,
        invert_tilt: bool = True,
    ) -> None:
        if not 0.0 <= dead_zone < 1.0:
            raise ValueError("dead_zone must satisfy 0 <= value < 1")

        if not 0.0 < max_pan_command <= 1.0:
            raise ValueError("max_pan_command must satisfy 0 < value <= 1")

        if not 0.0 < max_tilt_command <= 1.0:
            raise ValueError("max_tilt_command must satisfy 0 < value <= 1")

        self._dead_zone = dead_zone
        self._max_pan_command = max_pan_command
        self._max_tilt_command = max_tilt_command
        self._invert_tilt = invert_tilt

    def update(
        self,
        state: GamepadState,
    ) -> PanTiltCommand:
        if not state.connected:
            return PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=0.0,
                active=False,
            )

        pan = _apply_axis_dead_zone(
            state.pan_axis,
            self._dead_zone,
        )

        tilt = _apply_axis_dead_zone(
            state.tilt_axis,
            self._dead_zone,
        )

        if self._invert_tilt:
            tilt = -tilt

        return PanTiltCommand(
            pan_norm=(pan * self._max_pan_command),
            tilt_norm=(tilt * self._max_tilt_command),
            active=True,
        )
