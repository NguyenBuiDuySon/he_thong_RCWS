from __future__ import annotations

# from app.targeting.reacquire import is_reacquire_candidate
from app.targeting.reacquire import score_reacquire_candidate
from app.targeting.types import (
    LastTargetMemory,
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
        min_reacquire_score_margin: float = 0.10,
    ) -> None:
        if lost_timeout_frames < 1:
            raise ValueError("lost_timeout_frames must be >= 1")

        if min_reacquire_score_margin < 0.0:
            raise ValueError("min_reacquire_score_margin must be >= 0")

        self._lost_timeout_frames = lost_timeout_frames
        self._min_reacquire_score_margin = min_reacquire_score_margin
        self._selected_track_id: int | None = None
        self._selected_class_id: int | None = None
        self._missing_frames = 0
        self._last_target_memory: LastTargetMemory | None = None

    @property
    def selected_track_id(self) -> int | None:
        return self._selected_track_id

    @property
    def last_target_memory(self) -> LastTargetMemory | None:
        return self._last_target_memory

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
        self._last_target_memory = None

    def clear(self) -> None:
        self._selected_track_id = None
        self._selected_class_id = None
        self._missing_frames = 0
        self._last_target_memory = None

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

        if selected_track is None:
            selected_track = self._find_reacquire_candidate(batch)

            if selected_track is not None:
                self._selected_track_id = selected_track.track_id

        if selected_track is not None:
            self._missing_frames = 0

            self._last_target_memory = LastTargetMemory.from_track(
                frame_id=batch.frame_id,
                track=selected_track,
            )

            return TargetSnapshot(
                frame_id=batch.frame_id,
                status=TargetStatus.LOCKED,
                selected_track_id=self._selected_track_id,
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

    def _find_reacquire_candidate(
        self,
        batch: TrackBatch,
    ) -> Track | None:
        memory = self._last_target_memory

        if memory is None:
            return None

        best_track: Track | None = None
        best_score: float | None = None
        second_best_score: float | None = None

        for track in batch.tracks:
            score = score_reacquire_candidate(
                memory,
                track,
            )

            if score is None:
                continue

            if best_score is None or score < best_score:
                second_best_score = best_score
                best_score = score
                best_track = track
                continue

            if second_best_score is None or score < second_best_score:
                second_best_score = score

        if best_track is None or best_score is None:
            return None

        if (
            second_best_score is not None
            and second_best_score - best_score < self._min_reacquire_score_margin
        ):
            return None

        return best_track
