from __future__ import annotations

from dataclasses import dataclass

from app.control.types import PanTiltCommand

_PROTOCOL = "RCWS1"
_SCALE = 1000


@dataclass(frozen=True, slots=True)
class WireCommand:
    sequence: int
    active: bool
    pan_milli: int
    tilt_milli: int


def encode_command(
    command: PanTiltCommand,
    *,
    sequence: int,
) -> bytes:
    if not 0 <= sequence <= 65535:
        raise ValueError("sequence must be in range 0..65535")

    pan_milli = round(command.pan_norm * _SCALE)
    tilt_milli = round(command.tilt_norm * _SCALE)

    pan_milli = max(-_SCALE, min(_SCALE, pan_milli))
    tilt_milli = max(-_SCALE, min(_SCALE, tilt_milli))

    active = 1 if command.active else 0

    return (f"{_PROTOCOL},{sequence},{active},{pan_milli},{tilt_milli}\n").encode(
        "ascii"
    )


def decode_command(data: bytes) -> WireCommand:
    try:
        line = data.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise ValueError("command must be ASCII") from exc

    parts = line.split(",")

    if len(parts) != 5:
        raise ValueError("invalid command field count")

    protocol, sequence_text, active_text, pan_text, tilt_text = parts

    if protocol != _PROTOCOL:
        raise ValueError("unsupported command protocol")

    sequence = int(sequence_text)
    active_int = int(active_text)
    pan_milli = int(pan_text)
    tilt_milli = int(tilt_text)

    if not 0 <= sequence <= 65535:
        raise ValueError("invalid sequence")

    if active_int not in (0, 1):
        raise ValueError("invalid active flag")

    if not -_SCALE <= pan_milli <= _SCALE:
        raise ValueError("invalid pan command")

    if not -_SCALE <= tilt_milli <= _SCALE:
        raise ValueError("invalid tilt command")

    return WireCommand(
        sequence=sequence,
        active=bool(active_int),
        pan_milli=pan_milli,
        tilt_milli=tilt_milli,
    )
