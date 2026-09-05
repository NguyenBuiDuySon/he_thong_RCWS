from time import perf_counter_ns

from app.control.types import PanTiltCommand
from app.output.base import CommandOutput


class CommandWatchdog:
    def __init__(
        self,
        output: CommandOutput,
        timeout_s: float = 0.25,
    ) -> None:
        if timeout_s <= 0:
            raise ValueError("timeout_s must be > 0")

        self._output = output
        self._timeout_ns = int(timeout_s * 1_000_000_000)

        self._last_command_ns: int | None = None
        self._stopped = True
        self._closed = False

    def send(
        self,
        command: PanTiltCommand,
        now_ns: int | None = None,
    ) -> None:
        self._ensure_open()

        timestamp_ns = perf_counter_ns() if now_ns is None else now_ns

        if command.active:
            self._output.send(command)
            self._last_command_ns = timestamp_ns
            self._stopped = False
        else:
            self.stop()

    def update(self, now_ns: int | None = None) -> None:
        self._ensure_open()

        if self._last_command_ns is None or self._stopped:
            return

        timestamp_ns = perf_counter_ns() if now_ns is None else now_ns

        if timestamp_ns - self._last_command_ns >= self._timeout_ns:
            self.stop()

    def stop(self) -> None:
        self._ensure_open()

        if not self._stopped:
            self._output.stop()
            self._stopped = True

        self._last_command_ns = None

    def close(self) -> None:
        if self._closed:
            return

        if not self._stopped:
            self._output.stop()

        self._output.close()

        self._last_command_ns = None
        self._stopped = True
        self._closed = True

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("command watchdog is closed")
