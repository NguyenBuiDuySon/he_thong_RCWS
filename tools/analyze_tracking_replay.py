from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from app.telemetry.stats import MetricSeries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze tracking replay diagnostics.")

    parser.add_argument(
        "csv_path",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/tracking_summary.json"),
    )

    parser.add_argument(
        "--events-output",
        type=Path,
        default=Path("data/benchmarks/tracking_events.csv"),
    )

    return parser.parse_args()


def optional_int(
    value: str,
) -> int | None:
    if value == "":
        return None

    return int(value)


def main() -> None:
    args = parse_args()

    if not args.csv_path.exists():
        raise FileNotFoundError(args.csv_path)

    with args.csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as input_file:
        rows = list(csv.DictReader(input_file))

    if not rows:
        raise RuntimeError("Tracking replay CSV contains no data rows.")

    status_counts = {
        "idle": 0,
        "locked": 0,
        "lost": 0,
    }

    detector_ms = MetricSeries()
    tracking_ms = MetricSeries()
    pipeline_ms = MetricSeries()

    id_switch_count = 0
    recovery_count = 0
    same_id_recovery_count = 0
    new_id_reacquire_count = 0
    timeout_count = 0

    events: list[dict[str, object]] = []

    lost_start_frame: int | None = None
    lost_start_time_s: float | None = None

    previous_status: str | None = None
    previous_selected_id: int | None = None

    for row in rows:
        frame_id = int(row["frame_id"])
        source_time_s = float(row["source_time_s"])

        status = row["target_status"]

        selected_id = optional_int(row["selected_track_id"])

        if status in status_counts:
            status_counts[status] += 1

        detector_ms.add(float(row["detector_ms"]))

        tracking_ms.add(float(row["tracking_ms"]))

        pipeline_ms.add(float(row["pipeline_ms"]))

        if (
            previous_selected_id is not None
            and selected_id is not None
            and selected_id != previous_selected_id
        ):
            id_switch_count += 1

        if status == "lost" and previous_status != "lost":
            lost_start_frame = frame_id
            lost_start_time_s = source_time_s

        if (
            previous_status == "lost"
            and status == "locked"
            and lost_start_frame is not None
            and lost_start_time_s is not None
        ):
            recovery_count += 1

            lost_frames = frame_id - lost_start_frame

            elapsed_s = source_time_s - lost_start_time_s

            old_id = previous_selected_id

            if old_id == selected_id:
                event_type = "same_id_recovery"
                same_id_recovery_count += 1
            else:
                event_type = "new_id_reacquire"
                new_id_reacquire_count += 1

            events.append(
                {
                    "event": event_type,
                    "frame_id": frame_id,
                    "time_s": source_time_s,
                    "old_track_id": old_id,
                    "new_track_id": selected_id,
                    "lost_start_frame": (lost_start_frame),
                    "lost_status_frames": (lost_frames),
                    "missing_updates": (lost_frames),
                    "elapsed_s": elapsed_s,
                }
            )

            lost_start_frame = None
            lost_start_time_s = None

        if (
            previous_status == "lost"
            and status == "idle"
            and lost_start_frame is not None
            and lost_start_time_s is not None
        ):
            timeout_count += 1

            lost_frames = frame_id - lost_start_frame

            events.append(
                {
                    "event": "timeout",
                    "frame_id": frame_id,
                    "time_s": source_time_s,
                    "old_track_id": (previous_selected_id),
                    "new_track_id": None,
                    "lost_start_frame": (lost_start_frame),
                    "lost_status_frames": (lost_frames),
                    "missing_updates": (lost_frames + 1),
                    "elapsed_s": (source_time_s - lost_start_time_s),
                }
            )

            lost_start_frame = None
            lost_start_time_s = None

        previous_status = status

        if selected_id is not None:
            previous_selected_id = selected_id

    total_frames = len(rows)

    result = {
        "frames": {
            "total": total_frames,
            "idle": status_counts["idle"],
            "locked": status_counts["locked"],
            "lost": status_counts["lost"],
            "locked_ratio": (status_counts["locked"] / total_frames),
            "lost_ratio": (status_counts["lost"] / total_frames),
        },
        "events": {
            "id_switch_count": id_switch_count,
            "recovery_count": recovery_count,
            "same_id_recovery_count": (same_id_recovery_count),
            "new_id_reacquire_count": (new_id_reacquire_count),
            "timeout_count": timeout_count,
        },
        "metrics_ms": {
            "detector": (detector_ms.summarize().to_dict()),
            "tracking": (tracking_ms.summarize().to_dict()),
            "pipeline": (pipeline_ms.summarize().to_dict()),
        },
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.events_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    event_fieldnames = (
        "event",
        "frame_id",
        "time_s",
        "old_track_id",
        "new_track_id",
        "lost_start_frame",
        "lost_status_frames",
        "missing_updates",
        "elapsed_s",
    )

    with args.events_output.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as event_file:
        writer = csv.DictWriter(
            event_file,
            fieldnames=event_fieldnames,
        )

        writer.writeheader()
        writer.writerows(events)

    print("========== TRACKING SUMMARY ==========")
    print(f"Frames          : {total_frames}")
    print(f"Locked          : {status_counts['locked']}")
    print(f"Lost            : {status_counts['lost']}")
    print(f"Recoveries      : {recovery_count}")
    print(f"Same-ID recovery: {same_id_recovery_count}")
    print(f"New-ID reacquire: {new_id_reacquire_count}")
    print(f"ID switches     : {id_switch_count}")
    print(f"Timeouts        : {timeout_count}")
    print(f"Summary         : {args.output}")
    print(f"Events          : {args.events_output}")


if __name__ == "__main__":
    main()
