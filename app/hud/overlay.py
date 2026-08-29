from __future__ import annotations
from app.detection.types import DetectionBatch

import cv2
import numpy as np


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
    fps: float,
    frame_age_ms: float,
    backend: str,
    dropped_frames: int,
    show_crosshair: bool,
    inference_ms: float,
    model_inference_ms: float,
    detector_total_ms: float,
    detection_count: int,
    detector_device: str,
    detector_precision: str,
) -> None:
    if show_crosshair:
        draw_crosshair(image)

    height, width = image.shape[:2]

    lines = (
        "MODE: VIDEO",
        f"FRAME: {frame_id}",
        f"FPS: {fps:.1f}",
        f"AGE: {frame_age_ms:.2f} ms",
        f"RES: {width}x{height}",
        f"BACKEND: {backend}",
        f"DROPPED: {dropped_frames}",
        f"DETECTIONS: {detection_count}",
        f"INFERENCE: {inference_ms:.2f} ms",
        f"MODEL: {model_inference_ms:.2f} ms",
        f"DET TOTAL: {detector_total_ms:.2f} ms",
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

        label = (
            f"{detection.class_name} "
            f"{detection.confidence:.2f}"
        )

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