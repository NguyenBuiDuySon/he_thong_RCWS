from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.control.mode import ControlMode
from app.targeting.types import TargetStatus


class SearchState(StrEnum):
    INACTIVE = "inactive"
    COAST = "coast"
    REACQUIRE = "reacquire"
    SEARCHING = "searching"
    LOST = "lost"


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    frame_id: int

    control_mode: ControlMode

    target_status: TargetStatus
    target_id: int | None

    search_state: SearchState

    camera_fps: float
    pipeline_fps: float

    model_inference_ms: float
    model_inference_p95_ms: float

    detector_total_ms: float
    detector_total_p95_ms: float

    tracking_ms: float
    tracking_p95_ms: float

    frame_age_ms: float
    frame_age_p95_ms: float

    detection_count: int
    track_count: int

    target_class: str | None
    target_confidence: float | None
    target_bbox: tuple[float, float, float, float] | None
    target_center: tuple[float, float] | None
    target_missing_frames: int

    gamepad_connected: bool
    gamepad_pan_axis: float
    gamepad_tilt_axis: float

    manual_pan_command: float
    manual_tilt_command: float

    vision_pan_command: float
    vision_tilt_command: float

    selected_pan_command: float
    selected_tilt_command: float

    output_mode: str

    pan_command: float
    tilt_command: float
