from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import cv2


class MouseActionType(StrEnum):
    SELECT = "select"
    CLEAR = "clear"


@dataclass(
    frozen=True,
    slots=True,
)
class MouseAction:
    action: MouseActionType
    x: int | None = None
    y: int | None = None


class MouseTargetInput:
    def __init__(self) -> None:
        self._pending: MouseAction | None = None

    def callback(
        self,
        event: int,
        x: int,
        y: int,
        flags: int,
        param: object,
    ) -> None:
        del flags, param

        if event == cv2.EVENT_LBUTTONDOWN:
            self._pending = MouseAction(
                action=MouseActionType.SELECT,
                x=x,
                y=y,
            )

        elif event == cv2.EVENT_RBUTTONDOWN:
            self._pending = MouseAction(
                action=MouseActionType.CLEAR,
            )

    def consume(
        self,
    ) -> MouseAction | None:
        action = self._pending
        self._pending = None
        return action
