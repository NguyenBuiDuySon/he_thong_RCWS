from __future__ import annotations

from app.targeting.reacquire import (
    evaluate_reacquire_candidate,
)
from app.targeting.types import (
    LastTargetMemory,
    ReacquireDiagnostics,
    ReacquireRejectReason,
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
        reacquire_confirm_frames: int = 2,
    ) -> None:
        if lost_timeout_frames < 1:
            raise ValueError("lost_timeout_frames must be >= 1")

        if min_reacquire_score_margin < 0.0:
            raise ValueError("min_reacquire_score_margin must be >= 0")

        if reacquire_confirm_frames < 1:
            raise ValueError("reacquire_confirm_frames must be >= 1")

        self._lost_timeout_frames = lost_timeout_frames
        self._min_reacquire_score_margin = min_reacquire_score_margin
        self._selected_track_id: int | None = None
        self._selected_class_id: int | None = None
        self._missing_frames = 0
        self._last_target_memory: LastTargetMemory | None = None
        self._reacquire_confirm_frames = reacquire_confirm_frames

        self._pending_reacquire_track_id: int | None = None
        self._pending_reacquire_frames = 0

        self._reacquire_diagnostics = ReacquireDiagnostics()

    @property
    def selected_track_id(self) -> int | None:
        return self._selected_track_id

    @property
    def last_target_memory(self) -> LastTargetMemory | None:
        return self._last_target_memory

    @property
    def has_selection(self) -> bool:
        return self._selected_track_id is not None

    @property
    def reacquire_diagnostics(
        self,
    ) -> ReacquireDiagnostics:
        return self._reacquire_diagnostics

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
        self._pending_reacquire_track_id = None
        self._pending_reacquire_frames = 0

    def clear(self) -> None:
        self._selected_track_id = None
        self._selected_class_id = None
        self._missing_frames = 0
        self._last_target_memory = None
        self._pending_reacquire_track_id = None
        self._pending_reacquire_frames = 0

    def update(
        self,
        batch: TrackBatch,
    ) -> TargetSnapshot:

        self._reacquire_diagnostics = ReacquireDiagnostics()

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
            candidate = self._find_reacquire_candidate(batch)

            selected_track = self._confirm_reacquire_candidate(candidate)

            if selected_track is not None:
                self._selected_track_id = selected_track.track_id
        else:
            self._pending_reacquire_track_id = None
            self._pending_reacquire_frames = 0

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

        same_class_tracks = 0
        candidate_count = 0

        rejected_invalid_geometry = 0
        rejected_center = 0
        rejected_scale = 0
        rejected_aspect = 0

        for track in batch.tracks:
            if track.class_id == memory.class_id:
                same_class_tracks += 1

            evaluation = evaluate_reacquire_candidate(
                memory,
                track,
            )

            if not evaluation.accepted:
                if evaluation.reject_reason is ReacquireRejectReason.INVALID_GEOMETRY:
                    rejected_invalid_geometry += 1

                elif evaluation.reject_reason is ReacquireRejectReason.CENTER:
                    rejected_center += 1

                elif evaluation.reject_reason is ReacquireRejectReason.SCALE:
                    rejected_scale += 1

                elif evaluation.reject_reason is ReacquireRejectReason.ASPECT:
                    rejected_aspect += 1

                continue

            score = evaluation.score

            if score is None:
                raise RuntimeError("Accepted reacquire candidate has no score.")

            candidate_count += 1

            if best_score is None or score < best_score:
                second_best_score = best_score
                best_score = score
                best_track = track
                continue

            if second_best_score is None or score < second_best_score:
                second_best_score = score

        score_gap = (
            None
            if best_score is None or second_best_score is None
            else second_best_score - best_score
        )

        rejected_ambiguous = (
            score_gap is not None and score_gap < self._min_reacquire_score_margin
        )

        self._reacquire_diagnostics = ReacquireDiagnostics(
            same_class_tracks=same_class_tracks,
            candidate_count=candidate_count,
            rejected_invalid_geometry=(rejected_invalid_geometry),
            rejected_center=rejected_center,
            rejected_scale=rejected_scale,
            rejected_aspect=rejected_aspect,
            best_score=best_score,
            second_best_score=second_best_score,
            score_gap=score_gap,
            rejected_ambiguous=rejected_ambiguous,
        )

        if best_track is None:
            return None

        if rejected_ambiguous:
            return None

        return best_track

    def _confirm_reacquire_candidate(
        self,
        candidate: Track | None,
    ) -> Track | None:
        if candidate is None:
            self._pending_reacquire_track_id = None
            self._pending_reacquire_frames = 0
            return None

        if candidate.track_id == self._pending_reacquire_track_id:
            self._pending_reacquire_frames += 1
        else:
            self._pending_reacquire_track_id = candidate.track_id
            self._pending_reacquire_frames = 1

        if self._pending_reacquire_frames < self._reacquire_confirm_frames:
            return None

        self._pending_reacquire_track_id = None
        self._pending_reacquire_frames = 0

        return candidate
