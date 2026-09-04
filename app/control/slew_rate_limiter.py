from __future__ import annotations

from app.control.types import PanTiltCommand

_NS_PER_SECOND = 1_000_000_000


def _move_towards(
    current: float,
    target: float,
    max_delta: float,
) -> float:
    delta = target - current

    if abs(delta) <= max_delta:
        return target

    if delta > 0.0:
        return current + max_delta

    return current - max_delta


class CommandSlewRateLimiter:
    def __init__(
        self,
        *,
        pan_rate_per_s: float = 2.0,
        tilt_rate_per_s: float = 2.0,
    ) -> None:
        if pan_rate_per_s <= 0.0:
            raise ValueError("pan_rate_per_s must be > 0")

        if tilt_rate_per_s <= 0.0:
            raise ValueError("tilt_rate_per_s must be > 0")

        self._pan_rate_per_s = pan_rate_per_s
        self._tilt_rate_per_s = tilt_rate_per_s

        self.reset()

    def reset(self) -> None:
        self._last_pan = 0.0
        self._last_tilt = 0.0
        self._last_timestamp_ns: int | None = None

    def update(
        self,
        command: PanTiltCommand,
        *,
        timestamp_ns: int,
    ) -> PanTiltCommand:
        if not command.active:
            self.reset()

            return PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=0.0,
                active=False,
            )

        if self._last_timestamp_ns is None:
            self._last_timestamp_ns = timestamp_ns

            return PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=0.0,
                active=True,
            )

        if timestamp_ns <= self._last_timestamp_ns:
            raise ValueError("timestamp_ns must increase")

        dt_s = (timestamp_ns - self._last_timestamp_ns) / _NS_PER_SECOND

        pan = _move_towards(
            self._last_pan,
            command.pan_norm,
            self._pan_rate_per_s * dt_s,
        )

        tilt = _move_towards(
            self._last_tilt,
            command.tilt_norm,
            self._tilt_rate_per_s * dt_s,
        )

        self._last_pan = pan
        self._last_tilt = tilt
        self._last_timestamp_ns = timestamp_ns

        return PanTiltCommand(
            pan_norm=pan,
            tilt_norm=tilt,
            active=True,
        )
