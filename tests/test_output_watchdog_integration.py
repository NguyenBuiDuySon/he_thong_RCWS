from app.control.types import PanTiltCommand
from app.control.watchdog import CommandWatchdog
from app.output.null import NullCommandOutput


def test_watchdog_and_null_output_integrate() -> None:
    raw_output = NullCommandOutput()
    output = CommandWatchdog(
        raw_output,
        timeout_s=0.25,
    )

    output.send(
        PanTiltCommand(
            pan_norm=0.25,
            tilt_norm=-0.10,
            active=True,
        ),
        now_ns=1_000_000_000,
    )

    output.send(
        PanTiltCommand(
            pan_norm=0.0,
            tilt_norm=0.0,
            active=False,
        ),
        now_ns=1_100_000_000,
    )

    output.close()
