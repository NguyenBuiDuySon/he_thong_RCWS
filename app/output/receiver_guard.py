from __future__ import annotations

from app.output.protocol import WireCommand, is_newer_sequence


class ReceiverCommandGuard:
    def __init__(self, timeout_s: float = 0.25) -> None:
        if timeout_s <= 0:
            raise ValueError("timeout_s must be > 0")

        self._timeout_ns = int(timeout_s * 1_000_000_000)

        self._last_sequence: int | None = None
        self._last_valid_ns: int | None = None
        self._active = False

    def accept(
        self,
        command: WireCommand,
        *,
        now_ns: int,
    ) -> bool:
        if self._session_expired(now_ns):
            self._reset_session()

        if self._last_sequence is not None and not is_newer_sequence(
            command.sequence,
            self._last_sequence,
        ):
            return False

        self._last_sequence = command.sequence
        self._last_valid_ns = now_ns
        self._active = command.active

        return True

    def should_stop(self, *, now_ns: int) -> bool:
        if self._last_valid_ns is None:
            return True

        if self._session_expired(now_ns):
            return True

        return not self._active

    def _session_expired(self, now_ns: int) -> bool:
        if self._last_valid_ns is None:
            return False

        return now_ns - self._last_valid_ns >= self._timeout_ns

    def _reset_session(self) -> None:
        self._last_sequence = None
        self._last_valid_ns = None
        self._active = False
