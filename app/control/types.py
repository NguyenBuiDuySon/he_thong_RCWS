from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PanTiltCommand:
    pan_norm: float
    tilt_norm: float
    active: bool
