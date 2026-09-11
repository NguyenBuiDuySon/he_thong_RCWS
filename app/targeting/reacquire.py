from __future__ import annotations

from math import hypot

from app.targeting.types import LastTargetMemory
from app.tracking.types import Track

_DEFAULT_MAX_CENTER_DISTANCE_NORM = 1.0


def is_reacquire_candidate(
    memory: LastTargetMemory,
    candidate: Track,
    *,
    max_center_distance_norm: float = _DEFAULT_MAX_CENTER_DISTANCE_NORM,
) -> bool:
    if max_center_distance_norm <= 0.0:
        raise ValueError("max_center_distance_norm must be > 0")

    if candidate.class_id != memory.class_id:
        return False

    if memory.width <= 0.0 or memory.height <= 0.0:
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

    return center_distance_norm <= max_center_distance_norm