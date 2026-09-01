from __future__ import annotations

import cv2
import numpy as np

from app.capture.latest_frame import StreamStats
from app.detection.types import DetectionBatch
from app.telemetry.live import LiveTelemetrySnapshot
from app.tracking.types import TrackBatch

GREEN = (0, 255, 0)
WHITE = (230, 230, 230)


def draw_crosshair(
    image: np.ndarray,
) -> None:
    height, width = image.shape[:2]

    cx = width // 2
    cy = height // 2

    arm = 18
    gap = 5

    cv2.line(
        image,
        (cx - arm, cy),
        (cx - gap, cy),
        GREEN,
        1,
    )

    cv2.line(
        image,
        (cx + gap, cy),
        (cx + arm, cy),
        GREEN,
        1,
    )

    cv2.line(
        image,
        (cx, cy - arm),
        (cx, cy - gap),
        GREEN,
        1,
    )

    cv2.line(
        image,
        (cx, cy + gap),
        (cx, cy + arm),
        GREEN,
        1,
    )


def draw_status(
    image: np.ndarray,
    *,
    frame_id: int,
    backend: str,
    stream_stats: StreamStats,
    telemetry: LiveTelemetrySnapshot,
    detection_count: int,
    detector_device: str,
    detector_precision: str,
    show_crosshair: bool,
    track_count: int,
    unconfirmed_count: int,
) -> None:
    if show_crosshair:
        draw_crosshair(image)

    height, width = image.shape[:2]

    lines = (
        "MODE: VIDEO",
        f"FRAME: {frame_id}",
        (f"CAP FPS: {stream_stats.captured_fps:.1f}"),
        (f"PIPE FPS: {telemetry.pipeline_fps:.1f}"),
        (f"AGE: {telemetry.frame_age_ms:.1f} ms P95 {telemetry.frame_age_p95_ms:.1f}"),
        f"RES: {width}x{height}",
        f"BACKEND: {backend}",
        (f"DROP: {stream_stats.dropped_frames} ({stream_stats.drop_rate_pct:.2f}%)"),
        f"TRACKS: {track_count}",
        f"UNCONFIRMED: {unconfirmed_count}",
        f"DETECTIONS: {detection_count}",
        (
            f"MODEL: "
            f"{telemetry.model_inference_ms:.1f} ms "
            f"P95 "
            f"{telemetry.model_inference_p95_ms:.1f}"
        ),
        (
            f"DET TOTAL: "
            f"{telemetry.detector_total_ms:.1f} ms "
            f"P95 "
            f"{telemetry.detector_total_p95_ms:.1f}"
        ),
        (
            f"TRACKER: "
            f"{telemetry.tracking_ms:.2f} ms "
            f"P95 {telemetry.tracking_p95_ms:.2f}"
        ),
        f"DEVICE: {detector_device}",
        f"PRECISION: {detector_precision}",
    )

    y = 28

    for text in lines:
        cv2.putText(
            image,
            text,
            (16, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            GREEN,
            1,
            cv2.LINE_AA,
        )

        y += 24


def draw_detections(
    image: np.ndarray,
    batch: DetectionBatch,
) -> None:
    for detection in batch.detections:
        x1 = int(detection.x1)
        y1 = int(detection.y1)
        x2 = int(detection.x2)
        y2 = int(detection.y2)

        cx = int(detection.center_x)
        cy = int(detection.center_y)

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            GREEN,
            1,
        )

        label = f"{detection.class_name} {detection.confidence:.2f}"

        cv2.putText(
            image,
            label,
            (x1, max(20, y1 - 7)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            GREEN,
            1,
            cv2.LINE_AA,
        )

        cv2.circle(
            image,
            (cx, cy),
            3,
            GREEN,
            -1,
        )


def draw_tracks(
    image: np.ndarray,
    batch: TrackBatch,
) -> None:
    for track in batch.tracks:
        x1 = int(track.x1)
        y1 = int(track.y1)
        x2 = int(track.x2)
        y2 = int(track.y2)

        cx = int(track.center_x)
        cy = int(track.center_y)

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            GREEN,
            2,
        )

        label = f"ID {track.track_id} | {track.class_name} {track.confidence:.2f}"

        cv2.putText(
            image,
            label,
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            GREEN,
            1,
            cv2.LINE_AA,
        )

        cv2.circle(
            image,
            (cx, cy),
            4,
            GREEN,
            -1,
        )
