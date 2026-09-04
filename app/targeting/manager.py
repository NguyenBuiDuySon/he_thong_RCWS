from __future__ import annotations

from app.targeting.types import (
    TargetSnapshot,
    TargetStatus,
)
from app.tracking.types import (
    Track,
    TrackBatch,
)


class TargetManager:
    def __init__(
        self,
        *,
        lost_timeout_frames: int = 90,
    ) -> None:
        if lost_timeout_frames < 1:
            raise ValueError("lost_timeout_frames must be >= 1")

        self._lost_timeout_frames = lost_timeout_frames
        self._selected_track_id: int | None = None
        self._selected_class_id: int | None = None
        self._missing_frames = 0

    @property
    def selected_track_id(self) -> int | None:
        return self._selected_track_id

    @property
    def has_selection(self) -> bool:
        return self._selected_track_id is not None

    def select(
        self,
        track_id: int,
        class_id: int,
    ) -> None:
        if track_id < 0:
            raise ValueError("track_id must be >= 0")

        if class_id < 0:
            raise ValueError("class_id must be >= 0")

        self._selected_track_id = track_id
        self._selected_class_id = class_id
        self._missing_frames = 0

    def clear(self) -> None:
        self._selected_track_id = None
        self._selected_class_id = None
        self._missing_frames = 0

    def update(
        self,
        batch: TrackBatch,
    ) -> TargetSnapshot:
        if self._selected_track_id is None:
            return TargetSnapshot(
                frame_id=batch.frame_id,
                status=TargetStatus.IDLE,
                selected_track_id=None,
                track=None,
                missing_frames=0,
            )

        selected_track = self._find_selected_track(batch)

        if selected_track is not None:
            self._missing_frames = 0

            return TargetSnapshot(
                frame_id=batch.frame_id,
                status=TargetStatus.LOCKED,
                selected_track_id=(self._selected_track_id),
                track=selected_track,
                missing_frames=0,
            )

        self._missing_frames += 1

        if self._missing_frames >= self._lost_timeout_frames:
            self.clear()

            return TargetSnapshot(
                frame_id=batch.frame_id,
                status=TargetStatus.IDLE,
                selected_track_id=None,
                track=None,
                missing_frames=0,
            )

        return TargetSnapshot(
            frame_id=batch.frame_id,
            status=TargetStatus.LOST,
            selected_track_id=self._selected_track_id,
            track=None,
            missing_frames=self._missing_frames,
        )

    def _find_selected_track(
        self,
        batch: TrackBatch,
    ) -> Track | None:
        for track in batch.tracks:
            if (
                track.track_id == self._selected_track_id
                and track.class_id == self._selected_class_id
            ):
                return track

        return None
