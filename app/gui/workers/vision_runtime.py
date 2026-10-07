from __future__ import annotations

from queue import Empty, Queue
from threading import Event
from time import perf_counter_ns

import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

from app.capture.camera import Camera, FramePacket
from app.capture.latest_frame import LatestFrameStream
from app.config import AppConfig
from app.control.button import RisingEdgeButton
from app.control.gamepad import GamepadCommandMapper
from app.control.gamepad_input import PygameGamepadInput
from app.control.mode import (
    CommandArbiter,
    ControlMode,
    can_enter_auto_vision,
)
from app.control.slew_rate_limiter import (
    CommandSlewRateLimiter,
)
from app.control.tracking_controller import TrackingController
from app.control.watchdog import CommandWatchdog
from app.hud.overlay import (
    draw_crosshair,
    draw_tracks,
)
from app.output.factory import build_command_output
from app.perception import process_perception_frame
from app.runtime.snapshot import (
    RuntimeSnapshot,
    SearchState,
)
from app.targeting.filter import TrackingErrorFilter
from app.targeting.manager import TargetManager
from app.targeting.observation import (
    build_target_observation,
)
from app.targeting.selection import pick_track_at_point
from app.targeting.types import TargetStatus
from app.telemetry.live import LiveTelemetry
from app.tracking.bytetrack_tracker import ByteTrackAdapter
from app.tracking.types import TrackBatch


class VisionRuntimeWorker(QObject):
    frame_ready = Signal(QImage)
    snapshot_ready = Signal(object)
    notice = Signal(str)
    error = Signal(str)
    finished = Signal()

    def __init__(
        self,
        config: AppConfig,
    ) -> None:
        super().__init__()

        self._config = config
        self._stop_event = Event()

        self._requests: Queue[tuple[str, int | None, int | None]] = Queue()

    def _read_stable_camera_frame(
        self,
        camera: Camera,
        *,
        discard_frames: int = 8,
    ) -> FramePacket:
        packet: FramePacket | None = None

        for _ in range(discard_frames):
            candidate = camera.read()

            if candidate is not None:
                packet = candidate

        if packet is None:
            raise RuntimeError("Cannot read stable camera frame.")

        return packet

    def request_select(
        self,
        x: int,
        y: int,
    ) -> None:
        self._requests.put(("select", x, y))

    def request_clear(self) -> None:
        self._requests.put(("clear", None, None))

    def request_stop(self) -> None:
        self._stop_event.set()

    def _process_requests(
        self,
        *,
        track_batch: TrackBatch,
        target_manager: TargetManager,
    ) -> bool:
        cleared_by_operator = False

        while True:
            try:
                action, x, y = self._requests.get_nowait()
            except Empty:
                return cleared_by_operator

            if action == "clear":
                target_manager.clear()

                self.notice.emit("TARGET CLEARED")

                cleared_by_operator = True
                continue

            if action == "select" and x is not None and y is not None:
                selected = pick_track_at_point(
                    track_batch,
                    x,
                    y,
                )

                if selected is None:
                    self.notice.emit("SELECT MISS")
                    continue

                target_manager.select(
                    selected.track_id,
                    selected.class_id,
                )

                self.notice.emit(
                    f"SELECTED ID {selected.track_id} | {selected.class_name}"
                )

    @staticmethod
    def _to_qimage(
        image: np.ndarray,
    ) -> QImage:
        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        height, width, channels = rgb.shape

        return QImage(
            rgb.data,
            width,
            height,
            channels * width,
            QImage.Format.Format_RGB888,
        ).copy()

    @Slot()
    def run(self) -> None:
        camera: Camera | None = None
        stream: LatestFrameStream | None = None
        gamepad: PygameGamepadInput | None = None
        output: CommandWatchdog | None = None

        try:
            camera = Camera(self._config.camera)

            warmup_packet = self._read_stable_camera_frame(camera)

            self.frame_ready.emit(self._to_qimage(warmup_packet.image))

            self.notice.emit("CAMERA READY")

            # Import nặng chỉ bắt đầu ở đây
            self.notice.emit("LOADING DETECTOR")

            from app.detection.yolo_detector import (
                YoloDetector,
            )

            detector = YoloDetector(self._config.detector)

            self.notice.emit("DETECTOR WARMUP")

            detector.warmup(
                warmup_packet,
                self._config.detector.warmup_iterations,
            )

            if self._config.tracker.algorithm != "bytetrack":
                raise ValueError("Only 'bytetrack' is supported.")

            tracker_fps = (
                camera.actual_fps
                if camera.actual_fps > 0
                else float(self._config.camera.fps)
            )

            tracker = ByteTrackAdapter(
                self._config.tracker,
                frame_rate=tracker_fps,
            )

            target_manager = TargetManager(
                lost_timeout_frames=(self._config.targeting.lost_timeout_frames)
            )

            error_filter = TrackingErrorFilter(
                tau_ms=(self._config.targeting.control_filter_tau_ms)
            )

            tracking_controller = TrackingController(
                kp_pan=(self._config.control.kp_pan),
                kp_tilt=(self._config.control.kp_tilt),
                max_pan_command=(self._config.control.max_pan_command),
                max_tilt_command=(self._config.control.max_tilt_command),
            )

            gamepad = PygameGamepadInput(
                joystick_index=(self._config.control.gamepad.joystick_index),
                pan_axis_index=(self._config.control.gamepad.pan_axis_index),
                tilt_axis_index=(self._config.control.gamepad.tilt_axis_index),
                mode_button_index=(self._config.control.gamepad.mode_button_index),
            )

            gamepad_mapper = GamepadCommandMapper(
                dead_zone=(self._config.control.gamepad.dead_zone),
                max_pan_command=(self._config.control.max_pan_command),
                max_tilt_command=(self._config.control.max_tilt_command),
                invert_tilt=(self._config.control.gamepad.invert_tilt),
            )

            arbiter = CommandArbiter(initial_mode=ControlMode.MANUAL_GAMEPAD)

            mode_button = RisingEdgeButton()

            command_limiter = CommandSlewRateLimiter(
                pan_rate_per_s=(self._config.control.pan_rate_per_s),
                tilt_rate_per_s=(self._config.control.tilt_rate_per_s),
            )

            raw_output = build_command_output(self._config.output)

            output = CommandWatchdog(
                raw_output,
                timeout_s=(self._config.control.watchdog_timeout_s),
            )

            telemetry_meter = LiveTelemetry(
                window_size=(self._config.telemetry.rolling_window_frames)
            )

            stream = LatestFrameStream(
                camera,
                rate_window_frames=(self._config.telemetry.rolling_window_frames),
            )

            stream.start()

            self.notice.emit("SYSTEM READY")

            previous_target_status: TargetStatus = TargetStatus.IDLE

            previous_target_id: int | None = None

            while not self._stop_event.is_set():
                packet = stream.read(timeout=1.0)

                if packet is None:
                    output.stop()
                    raise RuntimeError("Camera stream unavailable.")

                batch, track_batch = process_perception_frame(
                    packet,
                    detector,
                    tracker,
                    on_failure=output.stop,
                )

                cleared_by_operator = self._process_requests(
                    track_batch=track_batch,
                    target_manager=target_manager,
                )

                target = target_manager.update(track_batch)

                if (
                    previous_target_status is TargetStatus.LOCKED
                    and target.status is TargetStatus.LOST
                ):
                    self.notice.emit(f"TARGET LOST | ID {previous_target_id}")

                elif (
                    previous_target_status is TargetStatus.LOST
                    and target.status is TargetStatus.LOCKED
                ):
                    if previous_target_id == target.selected_track_id:
                        self.notice.emit(
                            f"TARGET REACQUIRED | ID {target.selected_track_id}"
                        )
                    else:
                        self.notice.emit(
                            "TARGET REACQUIRED | "
                            f"ID {previous_target_id} "
                            f"-> {target.selected_track_id}"
                        )

                elif (
                    previous_target_status is TargetStatus.LOST
                    and target.status is TargetStatus.IDLE
                    and not cleared_by_operator
                ):
                    self.notice.emit("TARGET TIMEOUT -> IDLE")

                frame_height, frame_width = packet.image.shape[:2]

                observation = build_target_observation(
                    target,
                    frame_width=frame_width,
                    frame_height=frame_height,
                    dead_zone_x_norm=(self._config.targeting.dead_zone_x_norm),
                    dead_zone_y_norm=(self._config.targeting.dead_zone_y_norm),
                )

                filtered_error = None

                if observation is not None and target.track is not None:
                    filtered_error = error_filter.update(
                        target_id=(target.track.track_id),
                        x=(observation.control_error_x_norm),
                        y=(observation.control_error_y_norm),
                        timestamp_ns=(packet.received_at_ns),
                    )
                else:
                    error_filter.reset()

                vision_command = tracking_controller.update(
                    error_x=(filtered_error.x if filtered_error is not None else None),
                    error_y=(filtered_error.y if filtered_error is not None else None),
                    active=(filtered_error is not None),
                )

                gamepad_state = gamepad.poll()

                if not gamepad_state.connected:
                    mode_button.reset()

                elif mode_button.update(gamepad_state.mode_button_pressed):
                    if arbiter.mode is ControlMode.MANUAL_GAMEPAD:
                        if can_enter_auto_vision(vision_command):
                            arbiter.set_mode(ControlMode.AUTO_VISION)

                            self.notice.emit("MODE: AUTO_VISION")

                        else:
                            self.notice.emit("AUTO REJECTED: SELECT TARGET")

                    else:
                        arbiter.set_mode(ControlMode.MANUAL_GAMEPAD)

                        self.notice.emit("MODE: MANUAL_GAMEPAD")

                manual_command = gamepad_mapper.update(gamepad_state)

                selected_command = arbiter.select(
                    manual_command=manual_command,
                    auto_vision_command=vision_command,
                )

                command = command_limiter.update(
                    selected_command,
                    timestamp_ns=packet.received_at_ns,
                )

                output.send(command)

                frame_age_ms = (perf_counter_ns() - packet.received_at_ns) / 1_000_000

                telemetry = telemetry_meter.update(
                    model_inference_ms=(batch.inference_ms),
                    detector_total_ms=(batch.total_ms),
                    tracking_ms=(track_batch.tracking_ms),
                    frame_age_ms=(frame_age_ms),
                )

                if self._config.display.show_crosshair:
                    draw_crosshair(packet.image)

                draw_tracks(
                    packet.image,
                    track_batch,
                    target,
                )

                search_state = (
                    SearchState.REACQUIRE
                    if target.status is TargetStatus.LOST
                    else SearchState.INACTIVE
                )

                target_track = target.track
                target_class = (
                    target_track.class_name if target_track is not None else None
                )

                target_confidence = (
                    target_track.confidence if target_track is not None else None
                )

                target_bbox = (
                    (
                        target_track.x1,
                        target_track.y1,
                        target_track.x2,
                        target_track.y2,
                    )
                    if target_track is not None
                    else None
                )

                target_center = (
                    (
                        target_track.center_x,
                        target_track.center_y,
                    )
                    if target_track is not None
                    else None
                )

                snapshot = RuntimeSnapshot(
                    frame_id=packet.frame_id,
                    control_mode=arbiter.mode,
                    target_status=target.status,
                    target_id=target.selected_track_id,
                    search_state=search_state,
                    camera_fps=stream.stats.captured_fps,
                    pipeline_fps=telemetry.pipeline_fps,
                    model_inference_ms=(telemetry.model_inference_ms),
                    model_inference_p95_ms=(telemetry.model_inference_p95_ms),
                    detector_total_ms=(telemetry.detector_total_ms),
                    detector_total_p95_ms=(telemetry.detector_total_p95_ms),
                    tracking_ms=(telemetry.tracking_ms),
                    tracking_p95_ms=(telemetry.tracking_p95_ms),
                    frame_age_ms=(telemetry.frame_age_ms),
                    frame_age_p95_ms=(telemetry.frame_age_p95_ms),
                    detection_count=len(batch.detections),
                    track_count=len(track_batch.tracks),
                    target_class=target_class,
                    target_confidence=target_confidence,
                    target_bbox=target_bbox,
                    target_center=target_center,
                    target_missing_frames=(target.missing_frames),
                    gamepad_connected=(gamepad_state.connected),
                    gamepad_pan_axis=(gamepad_state.pan_axis),
                    gamepad_tilt_axis=(gamepad_state.tilt_axis),
                    manual_pan_command=(manual_command.pan_norm),
                    manual_tilt_command=(manual_command.tilt_norm),
                    vision_pan_command=(vision_command.pan_norm),
                    vision_tilt_command=(vision_command.tilt_norm),
                    selected_pan_command=(selected_command.pan_norm),
                    selected_tilt_command=(selected_command.tilt_norm),
                    output_mode=(self._config.output.mode),
                    pan_command=(command.pan_norm),
                    tilt_command=(command.tilt_norm),
                )

                self.frame_ready.emit(self._to_qimage(packet.image))

                self.snapshot_ready.emit(snapshot)
                previous_target_status = target.status

                if target.selected_track_id is not None:
                    previous_target_id = target.selected_track_id

                elif target.status is TargetStatus.IDLE:
                    previous_target_id = None

        except Exception as exc:  # noqa: BLE001
            self.error.emit(str(exc))

        finally:
            if output is not None:
                output.close()

            if gamepad is not None:
                gamepad.close()

            if stream is not None:
                stream.stop()

            if camera is not None:
                camera.close()

            self.finished.emit()
