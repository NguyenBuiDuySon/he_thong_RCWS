import pytest

from app.control.types import PanTiltCommand
from app.output.serial import SerialCommandOutput


def test_serial_output_sends_encoded_command() -> None:
    output = SerialCommandOutput("loop://")

    try:
        output.send(
            PanTiltCommand(
                pan_norm=-0.325,
                tilt_norm=0.180,
                active=True,
            )
        )

        packet = output._serial.readline()

        assert packet == b"RCWS1,0,1,-325,180\n"
    finally:
        output.close()


def test_serial_output_sequence_increments() -> None:
    output = SerialCommandOutput("loop://")

    try:
        command = PanTiltCommand(
            pan_norm=0.25,
            tilt_norm=-0.10,
            active=True,
        )

        output.send(command)
        output.send(command)

        first = output._serial.readline()
        second = output._serial.readline()

        assert first == b"RCWS1,0,1,250,-100\n"
        assert second == b"RCWS1,1,1,250,-100\n"
    finally:
        output.close()


def test_serial_output_stop_sends_zero_command() -> None:
    output = SerialCommandOutput("loop://")

    try:
        output.stop()

        packet = output._serial.readline()

        assert packet == b"RCWS1,0,0,0,0\n"
    finally:
        output.close()


def test_serial_output_rejects_send_after_close() -> None:
    output = SerialCommandOutput("loop://")

    output.close()

    with pytest.raises(RuntimeError, match="closed"):
        output.send(
            PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=0.0,
                active=False,
            )
        )


def test_serial_output_close_is_idempotent() -> None:
    output = SerialCommandOutput("loop://")

    output.close()
    output.close()
