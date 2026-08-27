from __future__ import annotations

from time import perf_counter_ns


class FpsMeter:
    def __init__(
        self,
        alpha: float = 0.10,
    ) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError(
                "alpha must be in (0, 1]."
            )

        self._alpha = alpha
        self._last_tick_ns: int | None = None
        self._fps = 0.0

    @property
    def value(self) -> float:
        return self._fps

    def tick(self) -> float:
        now_ns = perf_counter_ns()

        if self._last_tick_ns is None:
            self._last_tick_ns = now_ns
            return self._fps

        elapsed_s = (
            now_ns - self._last_tick_ns
        ) / 1_000_000_000

        self._last_tick_ns = now_ns

        if elapsed_s <= 0:
            return self._fps

        instant_fps = 1.0 / elapsed_s

        if self._fps == 0.0:
            self._fps = instant_fps
        else:
            self._fps = (
                (1.0 - self._alpha)
                * self._fps
                + self._alpha
                * instant_fps
            )

        return self._fps