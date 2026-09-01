from time import perf_counter_ns

import cv2

from app.capture.camera import Camera
from app.capture.latest_frame import LatestFrameStream
from app.config import load_config
from app.detection.yolo_detector import YoloDetector
from app.hud.overlay import (
    draw_status,
    draw_tracks,
)
from app.telemetry.live import LiveTelemetry
from app.tracking.bytetrack_tracker import (
    ByteTrackAdapter,
)


def main() -> None:
    config = load_config("configs/default.yaml")

    camera = Camera(config.camera)

    detector = YoloDetector(config.detector)

    warmup_packet = camera.read()

    if warmup_packet is None:
        raise RuntimeError("Cannot read detector warm-up frame.")

    print(f"Detector warm-up: {config.detector.warmup_iterations} iterations...")

    detector.warmup(
        warmup_packet,
        config.detector.warmup_iterations,
    )

    print("Detector warm-up complete.")

    stream = LatestFrameStream(
        camera,
        rate_window_frames=(config.telemetry.rolling_window_frames),
    )

    tracker_frame_rate = (
        camera.actual_fps if camera.actual_fps > 0 else float(config.camera.fps)
    )

    if config.tracker.algorithm != "bytetrack":
        raise ValueError("Only 'bytetrack' is supported at this stage.")

    tracker = ByteTrackAdapter(
        config.tracker,
        frame_rate=tracker_frame_rate,
    )

    print("\nCamera ready")

    print(f"Backend : {camera.backend_name}")

    print(f"Video   : {camera.actual_width}x{camera.actual_height}")

    print(f"FPS cam : {camera.actual_fps:.2f}")

    print("\nCapture thread starting...\n")

    print(f"Detector : {config.detector.model}")

    print(f"Device   : {detector.device}")

    print(f"Precision: {detector.precision}")

    live_telemetry = LiveTelemetry(window_size=(config.telemetry.rolling_window_frames))

    stream.start()

    try:
        while True:
            packet = stream.read(timeout=1.0)

            if packet is None:
                print("Camera frame timeout")
                break

            batch = detector.detect(packet)

            track_batch = tracker.update(
                packet,
                batch,
            )

            frame_age_ms = (perf_counter_ns() - packet.received_at_ns) / 1_000_000

            telemetry = live_telemetry.update(
                model_inference_ms=(batch.inference_ms),
                detector_total_ms=(batch.total_ms),
                tracking_ms=(track_batch.tracking_ms),
                frame_age_ms=(frame_age_ms),
            )

            stream_stats = stream.stats

            # draw_detections(
            #     packet.image,
            #     batch,
            # )

            draw_tracks(
                packet.image,
                track_batch,
            )

            draw_status(
                packet.image,
                frame_id=packet.frame_id,
                backend=camera.backend_name,
                stream_stats=stream_stats,
                telemetry=telemetry,
                detection_count=len(batch.detections),
                track_count=len(track_batch.tracks),
                unconfirmed_count=(track_batch.unconfirmed_count),
                detector_device=(detector.device),
                detector_precision=(detector.precision),
                show_crosshair=(config.display.show_crosshair),
            )

            cv2.imshow(
                config.display.window_name,
                packet.image,
            )

            key = cv2.waitKey(1) & 0xFF

            if key in (
                ord("q"),
                27,
            ):
                break

    finally:
        tracker.reset()
        stream.stop()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
