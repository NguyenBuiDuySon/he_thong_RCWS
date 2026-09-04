from time import perf_counter_ns

import cv2

from app.capture.camera import Camera
from app.capture.latest_frame import LatestFrameStream
from app.config import load_config
from app.control.tracking_controller import TrackingController
from app.detection.yolo_detector import YoloDetector
from app.hud.overlay import (
    draw_status,
    draw_tracks,
)
from app.targeting.filter import TrackingErrorFilter
from app.targeting.manager import TargetManager
from app.targeting.mouse import (
    MouseActionType,
    MouseTargetInput,
)
from app.targeting.observation import build_target_observation
from app.targeting.selection import (
    pick_track_at_point,
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
    target_manager = TargetManager(
        lost_timeout_frames=(config.targeting.lost_timeout_frames)
    )

    error_filter = TrackingErrorFilter(tau_ms=(config.targeting.control_filter_tau_ms))

    tracking_controller = TrackingController(
        kp_pan=1.0,
        kp_tilt=1.0,
    )

    mouse_input = MouseTargetInput()

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

    cv2.namedWindow(
        config.display.window_name,
        cv2.WINDOW_AUTOSIZE,
    )

    cv2.setMouseCallback(
        config.display.window_name,
        mouse_input.callback,
    )

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

            mouse_action = mouse_input.consume()

            if mouse_action is not None:
                if mouse_action.action is MouseActionType.CLEAR:
                    target_manager.clear()

                elif (
                    mouse_action.action is MouseActionType.SELECT
                    and mouse_action.x is not None
                    and mouse_action.y is not None
                ):
                    selected = pick_track_at_point(
                        track_batch,
                        mouse_action.x,
                        mouse_action.y,
                    )

                    if selected is not None:
                        target_manager.select(
                            selected.track_id,
                            selected.class_id,
                        )

            target = target_manager.update(track_batch)

            frame_height, frame_width = packet.image.shape[:2]

            observation = build_target_observation(
                target,
                frame_width=frame_width,
                frame_height=frame_height,
                dead_zone_x_norm=(config.targeting.dead_zone_x_norm),
                dead_zone_y_norm=(config.targeting.dead_zone_y_norm),
            )

            filtered_error = None
            if observation is not None and target.track is not None:
                filtered_error = error_filter.update(
                    target_id=target.track.track_id,
                    x=(observation.control_error_x_norm),
                    y=(observation.control_error_y_norm),
                    timestamp_ns=(packet.received_at_ns),
                )
            else:
                error_filter.reset()

            command = tracking_controller.update(
                error_x=(filtered_error.x if filtered_error is not None else None),
                error_y=(filtered_error.y if filtered_error is not None else None),
                active=filtered_error is not None,
            )

            if filtered_error is not None:
                cv2.putText(
                    packet.image,
                    (f"FILT X:{filtered_error.x:+.3f} Y:{filtered_error.y:+.3f}"),
                    (
                        16,
                        packet.image.shape[0] - 18,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

            command_state = "ON" if command.active else "OFF"

            cv2.putText(
                packet.image,
                (
                    f"CMD "
                    f"P:{command.pan_norm:+.3f} "
                    f"T:{command.tilt_norm:+.3f} "
                    f"{command_state}"
                ),
                (
                    16,
                    packet.image.shape[0] - 90,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
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
                target,
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
                target=target,
            )

            if observation is not None:
                state = "IN" if observation.inside_dead_zone else "OUT"

                cv2.putText(
                    packet.image,
                    (
                        f"ERR N "
                        f"X:{observation.error_x_norm:+.3f} "
                        f"Y:{observation.error_y_norm:+.3f}"
                    ),
                    (
                        16,
                        packet.image.shape[0] - 66,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

                cv2.putText(
                    packet.image,
                    (
                        f"CTRL "
                        f"X:{observation.control_error_x_norm:+.3f} "
                        f"Y:{observation.control_error_y_norm:+.3f} "
                        f"DZ:{state}"
                    ),
                    (
                        16,
                        packet.image.shape[0] - 42,
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.50,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
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
            if key in (
                ord("c"),
                ord("C"),
            ):
                target_manager.clear()

    finally:
        tracker.reset()
        stream.stop()
        camera.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
