from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True, slots=True)
class FilteredControlError:
    x: float
    y: float


class TrackingErrorFilter:
    def __init__(
        self,
        *,
        tau_ms: float,
    ) -> None:
        if tau_ms < 0.0:
            raise ValueError("tau_ms must be >= 0")

        self._tau_s = tau_ms / 1000.0

        self.reset()

    def reset(self) -> None:
        self._target_id: int | None = None

        self._x: float | None = None
        self._y: float | None = None

        self._timestamp_ns: int | None = None

    @staticmethod
    def _step(
        previous: float,
        value: float,
        alpha: float,
    ) -> float:
        # Dead-zone must stop this axis immediately.
        if value == 0.0:
            return 0.0

        # Never keep commanding the old direction
        # after the target crosses the center.
        if previous != 0.0 and previous * value < 0.0:
            return value

        return previous + alpha * (value - previous)

    def update(
        self,
        *,
        target_id: int,
        x: float,
        y: float,
        timestamp_ns: int,
    ) -> FilteredControlError:
        if timestamp_ns < 0:
            raise ValueError("timestamp_ns must be >= 0")

        if (
            self._target_id != target_id
            or self._x is None
            or self._y is None
            or self._timestamp_ns is None
        ):
            self._target_id = target_id

            self._x = x
            self._y = y

            self._timestamp_ns = timestamp_ns

            return FilteredControlError(
                x=x,
                y=y,
            )

        if self._tau_s == 0.0:
            alpha = 1.0
        else:
            dt_s = max(
                0.0,
                (timestamp_ns - self._timestamp_ns) / 1_000_000_000,
            )

            alpha = 1.0 - exp(-dt_s / self._tau_s)

        self._x = self._step(
            self._x,
            x,
            alpha,
        )

        self._y = self._step(
            self._y,
            y,
            alpha,
        )

        self._timestamp_ns = timestamp_ns

        return FilteredControlError(
            x=self._x,
            y=self._y,
        )
