from time import perf_counter_ns

import cv2

from app.capture.camera import Camera
from app.capture.latest_frame import LatestFrameStream
from app.config import load_config
from app.hud.overlay import draw_status
from app.telemetry.fps import FpsMeter
from app.detection.yolo_detector import YoloDetector
from app.hud.overlay import (
    draw_detections,
    draw_status,
)


from time import sleep

def main() -> None:
    config = load_config(
        "configs/default.yaml"
    )

    camera = Camera(
        config.camera
    )

    detector = YoloDetector(
    config.detector
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

    print(
    f"Detector : {config.detector.model}"
)

    print(
        f"Device   : {detector.device}"
    )

    print(
        f"Precision: {detector.precision}"
    )
    stream.start()

    try:
        while True:
            packet = stream.read(
                timeout=1.0
            )

            batch = detector.detect(
                packet
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

            draw_detections(
                packet.image,
                batch,
            )

            draw_status(
                 packet.image,
                frame_id=packet.frame_id,
                fps=fps,
                frame_age_ms=frame_age_ms,
                backend=camera.backend_name,
                dropped_frames=(
                    stream.dropped_frames
                ),
                inference_ms=batch.inference_ms,
                detection_count=len(
                    batch.detections
                ),
                detector_device=detector.device,
                detector_precision=detector.precision,
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