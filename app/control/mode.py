from __future__ import annotations

from enum import StrEnum

from app.control.types import PanTiltCommand


class ControlMode(StrEnum):
    MANUAL_GAMEPAD = "manual_gamepad"
    AUTO_VISION = "auto_vision"


def stopped_command() -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=0.0,
        tilt_norm=0.0,
        active=False,
    )


class CommandArbiter:
    def __init__(
        self,
        *,
        initial_mode: ControlMode = ControlMode.AUTO_VISION,
    ) -> None:
        self._mode = initial_mode
        self._stop_pending = False

    @property
    def mode(self) -> ControlMode:
        return self._mode

    def set_mode(
        self,
        mode: ControlMode,
    ) -> bool:
        if mode is self._mode:
            return False

        self._mode = mode
        self._stop_pending = True

        return True

    def select(
        self,
        *,
        manual_command: PanTiltCommand,
        auto_vision_command: PanTiltCommand,
    ) -> PanTiltCommand:
        if self._stop_pending:
            self._stop_pending = False
            return stopped_command()

        if self._mode is ControlMode.MANUAL_GAMEPAD:
            return manual_command

        return auto_vision_command


def can_enter_auto_vision(
    vision_command: PanTiltCommand,
) -> bool:
    return vision_command.active
