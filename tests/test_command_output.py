import pytest

from app.control.types import PanTiltCommand
from app.output.null import NullCommandOutput


def make_command() -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=0.25,
        tilt_norm=-0.10,
        active=True,
    )


def test_null_output_accepts_command() -> None:
    output = NullCommandOutput()

    output.send(make_command())


def test_null_output_closes() -> None:
    output = NullCommandOutput()

    output.close()


def test_null_output_rejects_send_after_close() -> None:
    output = NullCommandOutput()
    output.close()

    with pytest.raises(RuntimeError, match="closed"):
        output.send(make_command())
