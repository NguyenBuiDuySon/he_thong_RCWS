from __future__ import annotations

from math import hypot, log

from app.targeting.types import (
    LastTargetMemory,
    ReacquireCandidateEvaluation,
    ReacquireRejectReason,
)
from app.tracking.types import Track

_DEFAULT_MAX_CENTER_DISTANCE_NORM = 1.0
_DEFAULT_MAX_SCALE_RATIO = 2.5
_DEFAULT_MAX_ASPECT_RATIO_RATIO = 1.8


def evaluate_reacquire_candidate(
    memory: LastTargetMemory,
    candidate: Track,
    *,
    max_center_distance_norm: float = _DEFAULT_MAX_CENTER_DISTANCE_NORM,
    max_scale_ratio: float = _DEFAULT_MAX_SCALE_RATIO,
    max_aspect_ratio_ratio: float = _DEFAULT_MAX_ASPECT_RATIO_RATIO,
) -> ReacquireCandidateEvaluation:
    if max_center_distance_norm <= 0.0:
        raise ValueError("max_center_distance_norm must be > 0")

    if max_scale_ratio < 1.0:
        raise ValueError("max_scale_ratio must be >= 1")

    if max_aspect_ratio_ratio < 1.0:
        raise ValueError("max_aspect_ratio_ratio must be >= 1")

    if candidate.class_id != memory.class_id:
        return ReacquireCandidateEvaluation(
            accepted=False,
        )

    if (
        memory.width <= 0.0
        or memory.height <= 0.0
        or candidate.width <= 0.0
        or candidate.height <= 0.0
    ):
        return ReacquireCandidateEvaluation(
            accepted=False,
            reject_reason=(ReacquireRejectReason.INVALID_GEOMETRY),
        )

    dx_norm = (candidate.center_x - memory.center_x) / memory.width

    dy_norm = (candidate.center_y - memory.center_y) / memory.height

    center_distance = hypot(
        dx_norm,
        dy_norm,
    )

    if center_distance > max_center_distance_norm:
        return ReacquireCandidateEvaluation(
            accepted=False,
            reject_reason=ReacquireRejectReason.CENTER,
        )

    memory_area = memory.width * memory.height
    candidate_area = candidate.width * candidate.height

    scale_ratio = candidate_area / memory_area

    if not (1.0 / max_scale_ratio <= scale_ratio <= max_scale_ratio):
        return ReacquireCandidateEvaluation(
            accepted=False,
            reject_reason=ReacquireRejectReason.SCALE,
        )

    memory_aspect_ratio = memory.width / memory.height

    candidate_aspect_ratio = candidate.width / candidate.height

    aspect_ratio_ratio = candidate_aspect_ratio / memory_aspect_ratio

    if not (
        1.0 / max_aspect_ratio_ratio <= aspect_ratio_ratio <= max_aspect_ratio_ratio
    ):
        return ReacquireCandidateEvaluation(
            accepted=False,
            reject_reason=ReacquireRejectReason.ASPECT,
        )

    scale_penalty = abs(log(scale_ratio))

    aspect_penalty = abs(log(aspect_ratio_ratio))

    score = center_distance + 0.5 * scale_penalty + 0.25 * aspect_penalty

    return ReacquireCandidateEvaluation(
        accepted=True,
        score=score,
    )


def is_reacquire_candidate(
    memory: LastTargetMemory,
    candidate: Track,
    *,
    max_center_distance_norm: float = _DEFAULT_MAX_CENTER_DISTANCE_NORM,
    max_scale_ratio: float = _DEFAULT_MAX_SCALE_RATIO,
    max_aspect_ratio_ratio: float = _DEFAULT_MAX_ASPECT_RATIO_RATIO,
) -> bool:
    evaluation = evaluate_reacquire_candidate(
        memory,
        candidate,
        max_center_distance_norm=max_center_distance_norm,
        max_scale_ratio=max_scale_ratio,
        max_aspect_ratio_ratio=max_aspect_ratio_ratio,
    )

    return evaluation.accepted


def score_reacquire_candidate(
    memory: LastTargetMemory,
    candidate: Track,
) -> float | None:
    evaluation = evaluate_reacquire_candidate(
        memory,
        candidate,
    )

    return evaluation.score
