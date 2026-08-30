from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from time import perf_counter_ns

# from app.telemetry.fps import FpsMeter
from app.telemetry.stats import RollingMetric


@dataclass(
    frozen=True,
    slots=True,
)
class LiveTelemetrySnapshot:
    pipeline_fps: float

    model_inference_ms: float
    model_inference_p95_ms: float

    detector_total_ms: float
    detector_total_p95_ms: float

    frame_age_ms: float
    frame_age_p95_ms: float


class LiveTelemetry:
    def __init__(
        self,
        window_size: int = 120,
    ) -> None:

        self._pipeline_times_ns: deque[int] = deque(
            maxlen=max(
                2,
                window_size,
            )
        )

        self._model_inference = RollingMetric(window_size)

        self._detector_total = RollingMetric(window_size)

        self._frame_age = RollingMetric(window_size)

    def _pipeline_fps(
        self,
    ) -> float:
        if len(self._pipeline_times_ns) < 2:
            return 0.0

        elapsed_s = (
            self._pipeline_times_ns[-1] - self._pipeline_times_ns[0]
        ) / 1_000_000_000

        if elapsed_s <= 0:
            return 0.0

        return (len(self._pipeline_times_ns) - 1) / elapsed_s

    def update(
        self,
        *,
        model_inference_ms: float,
        detector_total_ms: float,
        frame_age_ms: float,
    ) -> LiveTelemetrySnapshot:

        # pipeline_fps = (
        #     self._fps.tick()
        # )

        self._pipeline_times_ns.append(perf_counter_ns())

        pipeline_fps = self._pipeline_fps()

        self._model_inference.add(model_inference_ms)

        self._detector_total.add(detector_total_ms)

        self._frame_age.add(frame_age_ms)

        return LiveTelemetrySnapshot(
            pipeline_fps=pipeline_fps,
            model_inference_ms=(model_inference_ms),
            model_inference_p95_ms=(self._model_inference.p95),
            detector_total_ms=(detector_total_ms),
            detector_total_p95_ms=(self._detector_total.p95),
            frame_age_ms=(frame_age_ms),
            frame_age_p95_ms=(self._frame_age.p95),
        )
