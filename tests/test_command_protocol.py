import pytest

from app.control.types import PanTiltCommand
from app.output.protocol import (
    decode_command,
    encode_command,
    is_newer_sequence,
)


def test_encode_active_command() -> None:
    command = PanTiltCommand(
        pan_norm=-0.325,
        tilt_norm=0.180,
        active=True,
    )

    packet = encode_command(
        command,
        sequence=42,
    )

    assert packet == b"RCWS1,42,1,-325,180\n"


def test_encode_inactive_command() -> None:
    command = PanTiltCommand(
        pan_norm=0.0,
        tilt_norm=0.0,
        active=False,
    )

    packet = encode_command(
        command,
        sequence=10,
    )

    assert packet == b"RCWS1,10,0,0,0\n"


def test_decode_command() -> None:
    command = decode_command(b"RCWS1,42,1,-325,180\n")

    assert command.sequence == 42
    assert command.active
    assert command.pan_milli == -325
    assert command.tilt_milli == 180


def test_rejects_invalid_active_flag() -> None:
    with pytest.raises(ValueError):
        decode_command(b"RCWS1,1,9,0,0\n")


def test_rejects_invalid_protocol() -> None:
    with pytest.raises(ValueError):
        decode_command(b"BAD,1,1,0,0\n")


def test_sequence_ordering() -> None:
    assert is_newer_sequence(11, 10)

    assert not is_newer_sequence(10, 10)
    assert not is_newer_sequence(9, 10)
    assert not is_newer_sequence(32768, 0)


def test_sequence_wraparound() -> None:
    assert is_newer_sequence(0, 65535)
    assert is_newer_sequence(1, 65535)


def test_inactive_encode_forces_zero_motion() -> None:
    packet = encode_command(
        PanTiltCommand(
            pan_norm=1.0,
            tilt_norm=-1.0,
            active=False,
        ),
        sequence=7,
    )

    assert packet == b"RCWS1,7,0,0,0\n"


def test_decode_rejects_nonzero_inactive_command() -> None:
    with pytest.raises(
        ValueError,
        match="inactive command",
    ):
        decode_command(b"RCWS1,7,0,500,-500\n")
