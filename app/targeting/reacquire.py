from __future__ import annotations

from math import hypot

from app.targeting.types import LastTargetMemory
from app.tracking.types import Track

_DEFAULT_MAX_CENTER_DISTANCE_NORM = 1.0
_DEFAULT_MAX_SCALE_RATIO = 2.5
_DEFAULT_MAX_ASPECT_RATIO_RATIO = 1.8


def is_reacquire_candidate(
    memory: LastTargetMemory,
    candidate: Track,
    *,
    max_center_distance_norm: float = _DEFAULT_MAX_CENTER_DISTANCE_NORM,
    max_scale_ratio: float = _DEFAULT_MAX_SCALE_RATIO,
    max_aspect_ratio_ratio: float = _DEFAULT_MAX_ASPECT_RATIO_RATIO,
) -> bool:
    if max_center_distance_norm <= 0.0:
        raise ValueError("max_center_distance_norm must be > 0")

    if max_scale_ratio < 1.0:
        raise ValueError("max_scale_ratio must be >= 1")

    if max_aspect_ratio_ratio < 1.0:
        raise ValueError("max_aspect_ratio_ratio must be >= 1")

    if candidate.class_id != memory.class_id:
        return False

    if (
        memory.width <= 0.0
        or memory.height <= 0.0
        or candidate.width <= 0.0
        or candidate.height <= 0.0
    ):
        return False

    dx_norm = (
        candidate.center_x - memory.center_x
    ) / memory.width

    dy_norm = (
        candidate.center_y - memory.center_y
    ) / memory.height

    center_distance_norm = hypot(
        dx_norm,
        dy_norm,
    )

    if center_distance_norm > max_center_distance_norm:
        return False

    memory_area = memory.width * memory.height
    candidate_area = candidate.width * candidate.height

    scale_ratio = candidate_area / memory_area

    if not (
        1.0 / max_scale_ratio
        <= scale_ratio
        <= max_scale_ratio
    ):
        return False

    memory_aspect_ratio = memory.width / memory.height
    candidate_aspect_ratio = candidate.width / candidate.height

    aspect_ratio_ratio = (
        candidate_aspect_ratio
        / memory_aspect_ratio
    )

    return (
        1.0 / max_aspect_ratio_ratio
        <= aspect_ratio_ratio
        <= max_aspect_ratio_ratio
    )