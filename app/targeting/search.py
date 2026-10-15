from __future__ import annotations

from enum import StrEnum

from app.targeting.types import TargetStatus


class SearchState(StrEnum):
    INACTIVE = "inactive"
    COAST = "coast"
    REACQUIRE = "reacquire"
    SEARCHING = "searching"
    LOST = "lost"


class SearchController:
    def __init__(
        self,
        *,
        coast_frames: int = 6,
        reacquire_frames: int = 24,
    ) -> None:
        if coast_frames < 0:
            raise ValueError("coast_frames must be >= 0")

        if reacquire_frames < 0:
            raise ValueError("reacquire_frames must be >= 0")

        self._coast_frames = coast_frames
        self._reacquire_frames = reacquire_frames

    def update(
        self,
        *,
        target_status: TargetStatus,
        missing_frames: int,
        timed_out: bool = False,
    ) -> SearchState:
        if missing_frames < 0:
            raise ValueError("missing_frames must be >= 0")

        if timed_out:
            return SearchState.LOST

        if target_status is TargetStatus.LOCKED:
            return SearchState.INACTIVE

        if target_status is TargetStatus.IDLE:
            return SearchState.INACTIVE

        if missing_frames <= self._coast_frames:
            return SearchState.COAST

        reacquire_limit = self._coast_frames + self._reacquire_frames

        if missing_frames <= reacquire_limit:
            return SearchState.REACQUIRE

        return SearchState.SEARCHING
