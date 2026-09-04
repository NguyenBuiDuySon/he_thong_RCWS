from __future__ import annotations

from app.control.types import PanTiltCommand


def _clamp(value: float, limit: float) -> float:
    return max(
        -limit,
        min(limit, value),
    )


class TrackingController:
    def __init__(
        self,
        *,
        kp_pan: float = 1.0,
        kp_tilt: float = 1.0,
        max_pan_command: float = 1.0,
        max_tilt_command: float = 1.0,
    ) -> None:
        if kp_pan < 0.0:
            raise ValueError("kp_pan must be >= 0")

        if kp_tilt < 0.0:
            raise ValueError("kp_tilt must be >= 0")

        if max_pan_command <= 0.0:
            raise ValueError("max_pan_command must be > 0")

        if max_tilt_command <= 0.0:
            raise ValueError("max_tilt_command must be > 0")

        self._kp_pan = kp_pan
        self._kp_tilt = kp_tilt
        self._max_pan_command = max_pan_command
        self._max_tilt_command = max_tilt_command

    def update(
        self,
        *,
        error_x: float | None,
        error_y: float | None,
        active: bool,
    ) -> PanTiltCommand:
        if not active or error_x is None or error_y is None:
            return PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=0.0,
                active=False,
            )

        pan = _clamp(
            self._kp_pan * error_x,
            self._max_pan_command,
        )

        tilt = _clamp(
            self._kp_tilt * error_y,
            self._max_tilt_command,
        )

        return PanTiltCommand(
            pan_norm=pan,
            tilt_norm=tilt,
            active=True,
        )
