from __future__ import annotations


class OperatorNotice:
    def __init__(
        self,
        duration_s: float = 1.5,
    ) -> None:
        if duration_s <= 0.0:
            raise ValueError("duration_s must be > 0")

        self._duration_ns = int(duration_s * 1_000_000_000)

        self._text: str | None = None
        self._expires_at_ns = 0

    def show(
        self,
        text: str,
        *,
        now_ns: int,
    ) -> None:
        text = text.strip()

        if not text:
            raise ValueError("notice text must not be empty")

        self._text = text
        self._expires_at_ns = now_ns + self._duration_ns

    def read(
        self,
        *,
        now_ns: int,
    ) -> str | None:
        if self._text is None:
            return None

        if now_ns >= self._expires_at_ns:
            self.clear()
            return None

        return self._text

    def clear(self) -> None:
        self._text = None
        self._expires_at_ns = 0
