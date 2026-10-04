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
    frame_age_p95_ms: float

    gamepad_connected: bool

    output_mode: str

    pan_command: float
    tilt_command: float
