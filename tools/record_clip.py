from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2


WIDTH = 1280
HEIGHT = 720
FPS = 30

OUTPUT_DIR = Path("data/recordings")


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = OUTPUT_DIR / (
        f"test_{timestamp}.avi"
    )

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW,
    )

    if not camera.isOpened():
        raise RuntimeError(
            "Cannot open camera"
        )

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        WIDTH,
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        HEIGHT,
    )

    camera.set(
        cv2.CAP_PROP_FPS,
        FPS,
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"MJPG"
    )

    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        FPS,
        (WIDTH, HEIGHT),
    )

    if not writer.isOpened():
        camera.release()

        raise RuntimeError(
            "Cannot open VideoWriter"
        )

    frame_count = 0

    print(
        f"Recording to: {output_path}"
    )

    print(
        "Press Q or ESC to stop."
    )

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print(
                    "Camera read failed"
                )
                break

            writer.write(frame)

            frame_count += 1

            display = frame.copy()

            cv2.putText(
                display,
                "REC",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.putText(
                display,
                f"FRAME: {frame_count}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow(
                "Record Test Clip",
                display,
            )

            key = cv2.waitKey(1) & 0xFF

            if key in (
                ord("q"),
                27,
            ):
                break

    finally:
        camera.release()
        writer.release()

        cv2.destroyAllWindows()

    print(
        f"Saved: {output_path}"
    )

    print(
        f"Frames: {frame_count}"
    )


if __name__ == "__main__":
    main()