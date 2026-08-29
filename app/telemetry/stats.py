from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean, median, quantiles


@dataclass(
    frozen=True,
    slots=True,
)
class MetricSummary:
    count: int
    minimum: float
    maximum: float
    mean: float
    p50: float
    p95: float
    p99: float

    def to_dict(
        self,
    ) -> dict[str, float | int]:
        return {
            "count": self.count,
            "min": self.minimum,
            "max": self.maximum,
            "mean": self.mean,
            "p50": self.p50,
            "p95": self.p95,
            "p99": self.p99,
        }


class MetricSeries:
    def __init__(self) -> None:
        self._values: list[float] = []

    def add(
        self,
        value: float,
    ) -> None:
        self._values.append(
            float(value)
        )

    @property
    def count(self) -> int:
        return len(
            self._values
        )

    def summarize(
        self,
    ) -> MetricSummary:
        if not self._values:
            raise ValueError(
                "Cannot summarize "
                "an empty metric series."
            )

        if len(self._values) == 1:
            value = self._values[0]

            return MetricSummary(
                count=1,
                minimum=value,
                maximum=value,
                mean=value,
                p50=value,
                p95=value,
                p99=value,
            )

        percentile_cuts = quantiles(
            self._values,
            n=100,
            method="inclusive",
        )

        return MetricSummary(
            count=len(
                self._values
            ),
            minimum=min(
                self._values
            ),
            maximum=max(
                self._values
            ),
            mean=fmean(
                self._values
            ),
            p50=median(
                self._values
            ),
            p95=percentile_cuts[94],
            p99=percentile_cuts[98],
        )