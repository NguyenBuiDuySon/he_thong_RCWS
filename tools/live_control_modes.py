from __future__ import annotations

import time

from app.control.button import RisingEdgeButton
from app.control.gamepad import GamepadCommandMapper
from app.control.gamepad_input import PygameGamepadInput
from app.control.mode import (
    CommandArbiter,
    ControlMode,
)
from app.control.slew_rate_limiter import CommandSlewRateLimiter
from app.control.types import PanTiltCommand


def make_fake_vision_command() -> PanTiltCommand:
    return PanTiltCommand(
        pan_norm=0.80,
        tilt_norm=-0.60,
        active=True,
    )


def main() -> None:
    gamepad = PygameGamepadInput(
        joystick_index=0,
        pan_axis_index=0,
        tilt_axis_index=1,
        mode_button_index=5,
    )

    mapper = GamepadCommandMapper(
        dead_zone=0.10,
        invert_tilt=True,
    )

    arbiter = CommandArbiter(
        initial_mode=ControlMode.MANUAL_GAMEPAD,
    )

    mode_button = RisingEdgeButton()

    limiter = CommandSlewRateLimiter(
        pan_rate_per_s=0.50,
        tilt_rate_per_s=0.50,
    )

    print("======= CONTROL V1 DIAGNOSTIC =======")
    print("Gamepad button 5 = TOGGLE MODE")
    print("AUTO fake target: P=+0.80 T=-0.60")
    print("Diagnostic slew : 0.50 / s")
    print("Ctrl+C = stop")
    print()

    last_selected_active: bool | None = None

    try:
        while True:
            state = gamepad.poll()

            if not state.connected:
                mode_button.reset()

            elif mode_button.update(state.mode_button_pressed):
                next_mode = (
                    ControlMode.AUTO_VISION
                    if arbiter.mode is ControlMode.MANUAL_GAMEPAD
                    else ControlMode.MANUAL_GAMEPAD
                )

                arbiter.set_mode(next_mode)

                print(f"\n\nGAMEPAD MODE SWITCH -> {next_mode.value}")

            manual_command = mapper.update(state)

            vision_command = make_fake_vision_command()

            selected_command = arbiter.select(
                manual_command=manual_command,
                auto_vision_command=vision_command,
            )

            if last_selected_active is not False and not selected_command.active:
                print("\nARBITER -> STOP (transition frame)")

            last_selected_active = selected_command.active

            now_ns = time.perf_counter_ns()

            output_command = limiter.update(
                selected_command,
                timestamp_ns=now_ns,
            )

            source = (
                "MANUAL" if arbiter.mode is ControlMode.MANUAL_GAMEPAD else "VISION"
            )

            output_state = "ACTIVE" if output_command.active else "STOP"

            print(
                (
                    f"\rMODE:{arbiter.mode.value:<15} "
                    f"SRC:{source:<6} | "
                    f"PAD "
                    f"X:{state.pan_axis:+.2f} "
                    f"Y:{state.tilt_axis:+.2f} | "
                    f"MAN "
                    f"P:{manual_command.pan_norm:+.2f} "
                    f"T:{manual_command.tilt_norm:+.2f} | "
                    f"VIS "
                    f"P:{vision_command.pan_norm:+.2f} "
                    f"T:{vision_command.tilt_norm:+.2f} | "
                    f"OUT "
                    f"P:{output_command.pan_norm:+.2f} "
                    f"T:{output_command.tilt_norm:+.2f} "
                    f"{output_state}      "
                ),
                end="",
                flush=True,
            )

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        gamepad.close()


if __name__ == "__main__":
    main()
