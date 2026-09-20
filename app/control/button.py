from __future__ import annotations


class RisingEdgeButton:
    def __init__(self) -> None:
        self._previous = False

    def update(
        self,
        pressed: bool,
    ) -> bool:
        rising_edge = pressed and not self._previous

        self._previous = pressed

        return rising_edge

    def reset(self) -> None:
        self._previous = False
