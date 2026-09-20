from __future__ import annotations

import argparse
import time

import pygame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect connected gamepad axes, buttons and hats."
    )

    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Gamepad index to inspect.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    pygame.init()
    pygame.joystick.init()

    try:
        count = pygame.joystick.get_count()

        print(f"Detected gamepads: {count}")

        if count == 0:
            raise RuntimeError(
                "No gamepad detected. Connect the controller and run again."
            )

        if not 0 <= args.index < count:
            raise ValueError(
                f"Gamepad index {args.index} is invalid; "
                f"available range: 0..{count - 1}"
            )

        joystick = pygame.joystick.Joystick(args.index)
        joystick.init()

        print()
        print("======= GAMEPAD =======")
        print(f"Index   : {args.index}")
        print(f"Name    : {joystick.get_name()}")
        print(f"GUID    : {joystick.get_guid()}")
        print(f"Axes    : {joystick.get_numaxes()}")
        print(f"Buttons : {joystick.get_numbuttons()}")
        print(f"Hats    : {joystick.get_numhats()}")
        print()
        print("Move sticks / press buttons.")
        print("Ctrl+C to stop.")
        print()

        previous_axes: tuple[float, ...] | None = None
        previous_buttons: tuple[int, ...] | None = None
        previous_hats: tuple[tuple[int, int], ...] | None = None

        while True:
            pygame.event.pump()

            axes = tuple(
                round(
                    joystick.get_axis(index),
                    3,
                )
                for index in range(joystick.get_numaxes())
            )

            buttons = tuple(
                joystick.get_button(index) for index in range(joystick.get_numbuttons())
            )

            hats = tuple(
                joystick.get_hat(index) for index in range(joystick.get_numhats())
            )

            if (
                axes != previous_axes
                or buttons != previous_buttons
                or hats != previous_hats
            ):
                print(f"AXES {axes} | BUTTONS {buttons} | HATS {hats}")

                previous_axes = axes
                previous_buttons = buttons
                previous_hats = hats

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        pygame.joystick.quit()
        pygame.quit()


if __name__ == "__main__":
    main()
