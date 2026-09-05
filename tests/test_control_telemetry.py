from app.control.telemetry import build_control_telemetry
from app.control.types import PanTiltCommand


def test_build_control_telemetry() -> None:
    command = PanTiltCommand(
        pan_norm=0.25,
        tilt_norm=-0.10,
        active=True,
    )

    telemetry = build_control_telemetry(command)

    assert telemetry.pan == 0.25
    assert telemetry.tilt == -0.10
    assert telemetry.active is True


def test_build_control_telemetry_inactive() -> None:
    command = PanTiltCommand(
        pan_norm=0.0,
        tilt_norm=0.0,
        active=False,
    )

    telemetry = build_control_telemetry(command)

    assert telemetry.pan == 0.0
    assert telemetry.tilt == 0.0
    assert telemetry.active is False
