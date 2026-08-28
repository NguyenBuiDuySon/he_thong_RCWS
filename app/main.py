from time import perf_counter_ns

import cv2

from app.capture.camera import Camera
from app.capture.latest_frame import LatestFrameStream
from app.config import load_config
from app.hud.overlay import draw_status
from app.telemetry.fps import FpsMeter

from time import sleep

def main() -> None:
    config = load_config(
        "configs/default.yaml"
    )

    camera = Camera(
        config.camera
    )

    stream = LatestFrameStream(
        camera
    )

    fps_meter = FpsMeter(
        alpha=0.10
    )

    print(
        "\nCamera ready"
    )

    print(
        f"Backend : "
        f"{camera.backend_name}"
    )

    print(
        f"Video   : "
        f"{camera.actual_width}x"
        f"{camera.actual_height}"
    )

    print(
        f"FPS cam : "
        f"{camera.actual_fps:.2f}"
    )

    print(
        "\nCapture thread starting...\n"
    )

    stream.start()

    try:
        while True:
            packet = stream.read(
                timeout=1.0
            )

            if packet is None:
                print(
                    "Camera frame timeout"
                )
                break

            fps = fps_meter.tick()

            frame_age_ms = (
                perf_counter_ns()
                - packet.received_at_ns
            ) / 1_000_000
            #sleep(0.1)
            draw_status(
                packet.image,
                frame_id=packet.frame_id,
                fps=fps,
                frame_age_ms=frame_age_ms,
                backend=camera.backend_name,
                dropped_frames=(
                    stream.dropped_frames
                ),
                show_crosshair=(
                    config
                    .display
                    .show_crosshair
                ),
            )

            cv2.imshow(
                config.display.window_name,
                packet.image,
            )

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key in (
                ord("q"),
                27,
            ):
                break

    finally:
        stream.stop()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()