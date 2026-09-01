from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.tracking.types import Track


class TargetStatus(StrEnum):
    IDLE = "idle"
    LOCKED = "locked"
    LOST = "lost"


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
