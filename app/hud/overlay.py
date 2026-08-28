from __future__ import annotations

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