from __future__ import annotations

from dataclasses import dataclass
from math import copysign

from app.targeting.types import TargetSnapshot


@dataclass(frozen=True, slots=True)
class TargetObservation:
    target_x: float
    target_y: float

    center_x: float
    center_y: float

    error_x_px: float
    error_y_px: float

    error_x_norm: float
    error_y_norm: float

    control_error_x_norm: float
    control_error_y_norm: float

    inside_dead_zone: bool


def _apply_dead_zone(
    value: float,
    threshold: float,
) -> float:
    if not 0.0 <= threshold < 1.0:
        raise ValueError("dead-zone threshold must satisfy 0 <= threshold < 1")

    value = max(
        -1.0,
        min(
            1.0,
            value,
        ),
    )

    magnitude = abs(value)

    if magnitude <= threshold:
        return 0.0

    scaled = (magnitude - threshold) / (1.0 - threshold)

    return copysign(
        scaled,
        value,
    )


def build_target_observation(
    target: TargetSnapshot,
    *,
    frame_width: int,
    frame_height: int,
    dead_zone_x_norm: float = 0.0,
    dead_zone_y_norm: float = 0.0,
) -> TargetObservation | None:
    if not target.is_locked or target.track is None:
        return None

    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("frame dimensions must be > 0")

    if not 0.0 <= dead_zone_x_norm < 1.0:
        raise ValueError("dead_zone_x_norm must satisfy 0 <= value < 1")

    if not 0.0 <= dead_zone_y_norm < 1.0:
        raise ValueError("dead_zone_y_norm must satisfy 0 <= value < 1")

    center_x = frame_width * 0.5
    center_y = frame_height * 0.5

    error_x_px = target.track.center_x - center_x
    error_y_px = target.track.center_y - center_y

    error_x_norm = error_x_px / center_x
    error_y_norm = error_y_px / center_y

    control_error_x_norm = _apply_dead_zone(
        error_x_norm,
        dead_zone_x_norm,
    )
    control_error_y_norm = _apply_dead_zone(
        error_y_norm,
        dead_zone_y_norm,
    )

    inside_dead_zone = control_error_x_norm == 0.0 and control_error_y_norm == 0.0

    return TargetObservation(
        target_x=target.track.center_x,
        target_y=target.track.center_y,
        center_x=center_x,
        center_y=center_y,
        error_x_px=error_x_px,
        error_y_px=error_y_px,
        error_x_norm=error_x_norm,
        error_y_norm=error_y_norm,
        control_error_x_norm=control_error_x_norm,
        control_error_y_norm=control_error_y_norm,
        inside_dead_zone=inside_dead_zone,
    )
