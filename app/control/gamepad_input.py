from __future__ import annotations

import pygame

from app.control.gamepad import GamepadState


class PygameGamepadInput:
    def __init__(
        self,
        *,
        joystick_index: int = 0,
        pan_axis_index: int = 0,
        tilt_axis_index: int = 1,
        mode_button_index: int = 5,
    ) -> None:
        if joystick_index < 0:
            raise ValueError("joystick_index must be >= 0")

        if pan_axis_index < 0:
            raise ValueError("pan_axis_index must be >= 0")

        if tilt_axis_index < 0:
            raise ValueError("tilt_axis_index must be >= 0")

        if mode_button_index < 0:
            raise ValueError("mode_button_index must be >= 0")

        self._joystick_index = joystick_index
        self._pan_axis_index = pan_axis_index
        self._tilt_axis_index = tilt_axis_index
        self._mode_button_index = mode_button_index
        self._joystick: pygame.joystick.JoystickType | None = None
        self._instance_id: int | None = None

        pygame.init()
        pygame.joystick.init()

        self._connect_if_available()

    @property
    def connected(self) -> bool:
        return self._joystick is not None

    @property
    def name(self) -> str | None:
        if self._joystick is None:
            return None

        return self._joystick.get_name()

    def _disconnect(self) -> None:
        if self._joystick is not None:
            self._joystick.quit()

        self._joystick = None
        self._instance_id = None

    def _connect_if_available(self) -> None:
        if self._joystick is not None:
            return

        count = pygame.joystick.get_count()

        if self._joystick_index >= count:
            return

        joystick = pygame.joystick.Joystick(self._joystick_index)
        joystick.init()

        required_axis = max(
            self._pan_axis_index,
            self._tilt_axis_index,
        )

        if joystick.get_numaxes() <= required_axis:
            joystick.quit()

            raise RuntimeError(
                f"Gamepad does not expose the required axis {required_axis}."
            )

        if joystick.get_numbuttons() <= self._mode_button_index:
            joystick.quit()

            raise RuntimeError(
                "Gamepad does not expose the "
                f"required button "
                f"{self._mode_button_index}."
            )

        self._joystick = joystick
        self._instance_id = joystick.get_instance_id()

    def _process_device_events(self) -> None:
        events = pygame.event.get(
            [
                pygame.JOYDEVICEADDED,
                pygame.JOYDEVICEREMOVED,
            ]
        )

        for event in events:
            if event.type == pygame.JOYDEVICEREMOVED:
                if (
                    self._instance_id is not None
                    and event.instance_id == self._instance_id
                ):
                    self._disconnect()

            elif event.type == pygame.JOYDEVICEADDED and self._joystick is None:
                self._connect_if_available()

    def poll(self) -> GamepadState:
        pygame.event.pump()

        self._process_device_events()

        if self._joystick is None:
            self._connect_if_available()

        if self._joystick is None:
            return GamepadState(
                connected=False,
                pan_axis=0.0,
                tilt_axis=0.0,
                mode_button_pressed=False,
            )

        try:
            pan_axis = self._joystick.get_axis(self._pan_axis_index)

            tilt_axis = self._joystick.get_axis(self._tilt_axis_index)

            mode_button_pressed = bool(
                self._joystick.get_button(self._mode_button_index)
            )

        except pygame.error:
            self._disconnect()

            return GamepadState(
                connected=False,
                pan_axis=0.0,
                tilt_axis=0.0,
                mode_button_pressed=False,
            )

        return GamepadState(
            connected=True,
            pan_axis=float(pan_axis),
            tilt_axis=float(tilt_axis),
            mode_button_pressed=mode_button_pressed,
        )

    def close(self) -> None:
        self._disconnect()

        pygame.joystick.quit()
        pygame.quit()
