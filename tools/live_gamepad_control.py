from __future__ import annotations

import argparse
import time

from app.control.gamepad import (
    GamepadCommandMapper,
)
from app.control.gamepad_input import (
    PygameGamepadInput,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Live gamepad input and PanTiltCommand diagnostic.")
    )

    parser.add_argument(
        "--index",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--dead-zone",
        type=float,
        default=0.10,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    gamepad = PygameGamepadInput(
        joystick_index=args.index,
        pan_axis_index=0,
        tilt_axis_index=1,
    )

    mapper = GamepadCommandMapper(
        dead_zone=args.dead_zone,
        max_pan_command=1.0,
        max_tilt_command=1.0,
        invert_tilt=True,
    )

    print("======= LIVE GAMEPAD =======")
    print(f"Dead zone : {args.dead_zone:.2f}")
    print("Pan axis  : 0")
    print("Tilt axis : 1 (inverted)")
    print("Ctrl+C to stop.")
    print()

    previous_connected: bool | None = None

    try:
        while True:
            state = gamepad.poll()

            command = mapper.update(state)

            if state.connected != previous_connected:
                if state.connected:
                    print(f"\nCONNECTED: {gamepad.name}")
                else:
                    print("\nDISCONNECTED")

                previous_connected = state.connected

            status = "ACTIVE" if command.active else "STOP"

            print(
                (
                    f"\rRAW "
                    f"X:{state.pan_axis:+.3f} "
                    f"Y:{state.tilt_axis:+.3f} | "
                    f"CMD "
                    f"PAN:{command.pan_norm:+.3f} "
                    f"TILT:{command.tilt_norm:+.3f} "
                    f"{status}      "
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
