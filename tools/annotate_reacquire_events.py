from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2

_WINDOW_NAME = "Reacquire Ground Truth"
_DISPLAY_FRAME_WIDTH = 640


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Human annotation for new-ID reacquire events.")
    )

    parser.add_argument(
        "video",
        type=Path,
    )

    parser.add_argument(
        "replay_csv",
        type=Path,
    )

    parser.add_argument(
        "events_csv",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/annotations/reacquire_ground_truth.csv"),
    )

    return parser.parse_args()


def load_csv(
    path: Path,
) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def optional_int(
    value: str | None,
) -> int | None:
    if value is None or value == "":
        return None

    return int(value)


def has_target_bbox(
    row: dict[str, str],
) -> bool:
    return all(
        row.get(field, "") != ""
        for field in (
            "target_x1",
            "target_y1",
            "target_x2",
            "target_y2",
        )
    )


def read_frame(
    capture: cv2.VideoCapture,
    frame_id: int,
):
    capture.set(
        cv2.CAP_PROP_POS_FRAMES,
        float(frame_id),
    )

    ok, frame = capture.read()

    if not ok or frame is None:
        raise RuntimeError(f"Cannot read video frame {frame_id}.")

    return frame


def draw_target(
    frame,
    row: dict[str, str],
    title: str,
):
    image = frame.copy()

    if not has_target_bbox(row):
        raise RuntimeError(f"Frame {row['frame_id']} has no target bbox.")

    x1 = round(float(row["target_x1"]))
    y1 = round(float(row["target_y1"]))
    x2 = round(float(row["target_x2"]))
    y2 = round(float(row["target_y2"]))

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        3,
    )

    track_id = row.get(
        "active_track_id",
        "",
    )

    cv2.putText(
        image,
        f"{title} | ID {track_id}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return image


def resize_for_display(
    image,
):
    height, width = image.shape[:2]

    if width <= _DISPLAY_FRAME_WIDTH:
        return image

    scale = _DISPLAY_FRAME_WIDTH / width

    return cv2.resize(
        image,
        (
            _DISPLAY_FRAME_WIDTH,
            round(height * scale),
        ),
    )


def find_reference_row(
    rows_by_frame: dict[int, dict[str, str]],
    *,
    lost_start_frame: int,
    old_track_id: int | None,
) -> tuple[int, dict[str, str]]:
    for frame_id in range(
        lost_start_frame - 1,
        -1,
        -1,
    ):
        row = rows_by_frame.get(frame_id)

        if row is None:
            continue

        if not has_target_bbox(row):
            continue

        active_track_id = optional_int(row.get("active_track_id"))

        if old_track_id is None or active_track_id == old_track_id:
            return frame_id, row

    raise RuntimeError(
        f"Cannot find reference LOCKED frame before frame {lost_start_frame}."
    )


def write_annotations(
    path: Path,
    annotations: list[dict[str, object]],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = (
        "event_frame",
        "event_time_s",
        "lost_start_frame",
        "reference_frame",
        "old_track_id",
        "new_track_id",
        "lost_status_frames",
        "elapsed_s",
        "label",
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(annotations)


def main() -> None:
    args = parse_args()

    replay_rows = load_csv(args.replay_csv)

    event_rows = load_csv(args.events_csv)

    rows_by_frame = {int(row["frame_id"]): row for row in replay_rows}

    reacquire_events = [
        event for event in event_rows if event["event"] == "new_id_reacquire"
    ]

    if not reacquire_events:
        print("No new-ID reacquire events to annotate.")
        return

    if not args.video.exists():
        raise FileNotFoundError(args.video)

    capture = cv2.VideoCapture(str(args.video))

    if not capture.isOpened():
        raise RuntimeError(f"Cannot open video: {args.video}")

    annotations: list[dict[str, object]] = []

    print(f"New-ID events: {len(reacquire_events)}")
    print("Y = correct | N = false | U = uncertain | Q = save and quit")

    try:
        cv2.namedWindow(
            _WINDOW_NAME,
            cv2.WINDOW_NORMAL,
        )

        for index, event in enumerate(
            reacquire_events,
            start=1,
        ):
            event_frame = int(event["frame_id"])

            lost_start_frame = int(event["lost_start_frame"])

            old_track_id = optional_int(event.get("old_track_id"))

            new_track_id = optional_int(event.get("new_track_id"))

            reference_frame, reference_row = find_reference_row(
                rows_by_frame,
                lost_start_frame=(lost_start_frame),
                old_track_id=old_track_id,
            )

            event_row = rows_by_frame.get(event_frame)

            if event_row is None:
                raise RuntimeError(
                    f"Replay CSV does not contain event frame {event_frame}."
                )

            reference_image = read_frame(
                capture,
                reference_frame,
            )

            reacquired_image = read_frame(
                capture,
                event_frame,
            )

            reference_image = draw_target(
                reference_image,
                reference_row,
                "BEFORE LOST",
            )

            reacquired_image = draw_target(
                reacquired_image,
                event_row,
                "REACQUIRED",
            )

            reference_image = resize_for_display(reference_image)

            reacquired_image = resize_for_display(reacquired_image)

            display = cv2.hconcat(
                [
                    reference_image,
                    reacquired_image,
                ]
            )

            cv2.putText(
                display,
                (
                    f"Event {index}/"
                    f"{len(reacquire_events)} | "
                    "Y correct  N false  "
                    "U uncertain  Q quit"
                ),
                (20, display.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow(
                _WINDOW_NAME,
                display,
            )

            label: str | None = None

            while label is None:
                key = cv2.waitKey(0) & 0xFF

                if key in (
                    ord("y"),
                    ord("Y"),
                ):
                    label = "correct_reacquire"

                elif key in (
                    ord("n"),
                    ord("N"),
                ):
                    label = "false_reacquire"

                elif key in (
                    ord("u"),
                    ord("U"),
                ):
                    label = "uncertain"

                elif key in (
                    ord("q"),
                    ord("Q"),
                    27,
                ):
                    write_annotations(
                        args.output,
                        annotations,
                    )

                    print(f"Saved: {args.output}")

                    return

            annotations.append(
                {
                    "event_frame": event_frame,
                    "event_time_s": (event["time_s"]),
                    "lost_start_frame": (lost_start_frame),
                    "reference_frame": (reference_frame),
                    "old_track_id": (old_track_id),
                    "new_track_id": (new_track_id),
                    "lost_status_frames": (event["lost_status_frames"]),
                    "elapsed_s": (event["elapsed_s"]),
                    "label": label,
                }
            )

            print(f"Frame {event_frame}: {label}")

    finally:
        capture.release()
        cv2.destroyAllWindows()

    write_annotations(
        args.output,
        annotations,
    )

    print(f"Annotated: {len(annotations)}")
    print(f"Saved    : {args.output}")


if __name__ == "__main__":
    main()
