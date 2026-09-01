from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Track:
    track_id: int

    class_id: int
    class_name: str
    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) * 0.5

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) * 0.5

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1


@dataclass(frozen=True, slots=True)
class TrackBatch:
    frame_id: int
    tracking_ms: float

    tracks: tuple[Track, ...]
    unconfirmed_count: int
