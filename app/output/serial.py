from __future__ import annotations

import serial
from serial import SerialBase

from app.control.types import PanTiltCommand
from app.output.protocol import encode_command


class SerialCommandOutput:
    def __init__(
        self,
        port: str,
        *,
        baudrate: int = 115200,
        write_timeout_s: float = 0.10,
    ) -> None:
        if not port:
            raise ValueError("port must not be empty")

        if baudrate <= 0:
            raise ValueError("baudrate must be > 0")

        if write_timeout_s <= 0:
            raise ValueError("write_timeout_s must be > 0")

        self._serial: SerialBase = serial.serial_for_url(
            port,
            baudrate=baudrate,
            timeout=0.1,
            write_timeout=write_timeout_s,
        )

        self._sequence = 0
        self._closed = False

    def send(self, command: PanTiltCommand) -> None:
        self._ensure_open()

        packet = encode_command(
            command,
            sequence=self._sequence,
        )

        written = self._serial.write(packet)

        if written != len(packet):
            raise OSError(f"incomplete serial write: {written}/{len(packet)} bytes")

        self._advance_sequence()

    def stop(self) -> None:
        self._ensure_open()

        self.send(
            PanTiltCommand(
                pan_norm=0.0,
                tilt_norm=0.0,
                active=False,
            )
        )

    def close(self) -> None:
        if self._closed:
            return

        self._serial.close()
        self._closed = True

    def _advance_sequence(self) -> None:
        self._sequence = (self._sequence + 1) & 0xFFFF

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("serial command output is closed")
