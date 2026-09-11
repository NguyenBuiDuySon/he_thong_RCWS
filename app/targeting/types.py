from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.tracking.types import Track


class TargetStatus(StrEnum):
    IDLE = "idle"
    LOCKED = "locked"
    LOST = "lost"


@dataclass(frozen=True, slots=True)
class LastTargetMemory:
    frame_id: int

    track_id: int
    class_id: int
    class_name: str
    confidence: float

    x1: float
    y1: float
    x2: float
    y2: float

    @classmethod
    def from_track(
        cls,
        *,
        frame_id: int,
        track: Track,
    ) -> LastTargetMemory:
        return cls(
            frame_id=frame_id,
            track_id=track.track_id,
            class_id=track.class_id,
            class_name=track.class_name,
            confidence=track.confidence,
            x1=track.x1,
            y1=track.y1,
            x2=track.x2,
            y2=track.y2,
        )

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2.0

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1


@dataclass(frozen=True, slots=True)
class TargetSnapshot:
    frame_id: int

    status: TargetStatus

    selected_track_id: int | None

    track: Track | None

    missing_frames: int

    @property
    def is_locked(self) -> bool:
        return self.status is TargetStatus.LOCKED
