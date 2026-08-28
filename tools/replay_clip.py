from __future__ import annotations

import sys
from pathlib import Path
from time import perf_counter

import cv2


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: "
            "uv run python -m "
            "tools.replay_clip "
            "<video_path>"
        )

    video_path = Path(
        sys.argv[1]
    )

    if not video_path.exists():
        raise FileNotFoundError(
            video_path
        )

    capture = cv2.VideoCapture(
        str(video_path)
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Cannot open: {video_path}"
        )

    source_fps = capture.get(
        cv2.CAP_PROP_FPS
    )

    frame_count = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    if source_fps <= 0:
        source_fps = 30.0

    frame_period_s = (
        1.0 / source_fps
    )

    print(
        f"Video : {video_path}"
    )

    print(
        f"Size  : {width}x{height}"
    )

    print(
        f"FPS   : {source_fps:.2f}"
    )

    print(
        f"Frames: {frame_count}"
    )

    frame_id = 0

    try:
        while True:
            started_at = perf_counter()

            ok, frame = capture.read()

            if not ok:
                break

            cv2.putText(
                frame,
                f"REPLAY FRAME: {frame_id}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "Replay Test Clip",
                frame,
            )

            elapsed_s = (
                perf_counter()
                - started_at
            )

            remaining_s = (
                frame_period_s
                - elapsed_s
            )

            wait_ms = max(
                1,
                int(
                    remaining_s * 1000
                ),
            )

            key = (
                cv2.waitKey(wait_ms)
                & 0xFF
            )

            if key in (
                ord("q"),
                27,
            ):
                break

            frame_id += 1

    finally:
        capture.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()