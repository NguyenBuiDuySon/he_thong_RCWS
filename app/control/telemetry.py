from dataclasses import dataclass

from app.control.types import PanTiltCommand


@dataclass(frozen=True, slots=True)
class ControlTelemetry:
    pan: float
    tilt: float
    active: bool


def build_control_telemetry(command: PanTiltCommand) -> ControlTelemetry:
    return ControlTelemetry(
        pan=command.pan_norm,
        tilt=command.tilt_norm,
        active=command.active,
    )
