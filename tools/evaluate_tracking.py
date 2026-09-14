from __future__ import annotations

import argparse
import csv
from pathlib import Path
from time import perf_counter_ns

import cv2

from app.capture.camera import FramePacket
from app.config import load_config
from app.detection.yolo_detector import YoloDetector
from app.targeting.manager import TargetManager
from app.targeting.selection import pick_track_at_point
from app.tracking.bytetrack_tracker import ByteTrackAdapter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the full tracking pipeline on a recorded video."
    )

    parser.add_argument(
        "video",
        type=Path,
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/default.yaml"),
    )

    parser.add_argument(
        "--select-frame",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--select-x",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--select-y",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/tracking_replay.csv"),
    )

    return parser.parse_args()


def source_timestamp_ns(
    frame_id: int,
    fps: float,
) -> int:
    if frame_id < 0:
        raise ValueError("frame_id must be >= 0")

    if fps <= 0.0:
        raise ValueError("fps must be > 0")

    return round(frame_id * 1_000_000_000 / fps)


def main() -> None:
    args = parse_args()

    if not args.video.exists():
        raise FileNotFoundError(args.video)

    config = load_config(args.config)

    capture = cv2.VideoCapture(str(args.video))

    if not capture.isOpened():
        raise RuntimeError(f"Cannot open video: {args.video}")

    source_fps = float(capture.get(cv2.CAP_PROP_FPS))

    if source_fps <= 0.0:
        source_fps = float(config.camera.fps)

    detector = YoloDetector(config.detector)

    tracker = ByteTrackAdapter(
        config.tracker,
        frame_rate=source_fps,
    )

    target_manager = TargetManager(
        lost_timeout_frames=(config.targeting.lost_timeout_frames)
    )

    ok, warmup_frame = capture.read()

    if not ok:
        capture.release()
        raise RuntimeError("Cannot read warm-up frame.")

    detector.warmup(
        FramePacket(
            frame_id=-1,
            received_at_ns=0,
            image=warmup_frame,
        ),
        config.detector.warmup_iterations,
    )

    capture.set(
        cv2.CAP_PROP_POS_FRAMES,
        0,
    )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = (
        "frame_id",
        "source_time_s",
        "detection_count",
        "track_count",
        "unconfirmed_count",
        "target_status",
        "selected_track_id",
        "active_track_id",
        "target_x1",
        "target_y1",
        "target_x2",
        "target_y2",
        "missing_frames",
        "detector_ms",
        "tracking_ms",
        "pipeline_ms",
    )

    processed_frames = 0

    with args.output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        try:
            while True:
                if args.limit > 0 and processed_frames >= args.limit:
                    break

                started_ns = perf_counter_ns()

                ok, frame = capture.read()

                if not ok:
                    break

                frame_id = processed_frames

                packet = FramePacket(
                    frame_id=frame_id,
                    received_at_ns=source_timestamp_ns(
                        frame_id,
                        source_fps,
                    ),
                    image=frame,
                )

                detections = detector.detect(packet)

                tracks = tracker.update(
                    packet,
                    detections,
                )

                if frame_id == args.select_frame:
                    selected = pick_track_at_point(
                        tracks,
                        args.select_x,
                        args.select_y,
                    )

                    if selected is None:
                        raise RuntimeError(
                            "No track exists at the requested selection point."
                        )

                    target_manager.select(
                        selected.track_id,
                        selected.class_id,
                    )

                target = target_manager.update(tracks)
                target_track = target.track

                pipeline_ms = (perf_counter_ns() - started_ns) / 1_000_000

                writer.writerow(
                    {
                        "frame_id": frame_id,
                        "source_time_s": (frame_id / source_fps),
                        "detection_count": len(detections.detections),
                        "track_count": len(tracks.tracks),
                        "unconfirmed_count": (tracks.unconfirmed_count),
                        "target_status": (target.status.value),
                        "selected_track_id": (
                            ""
                            if target.selected_track_id is None
                            else target.selected_track_id
                        ),
                        "active_track_id": (
                            "" if target.track is None else target.track.track_id
                        ),
                        "target_x1": ("" if target_track is None else target_track.x1),
                        "target_y1": ("" if target_track is None else target_track.y1),
                        "target_x2": ("" if target_track is None else target_track.x2),
                        "target_y2": ("" if target_track is None else target_track.y2),
                        "missing_frames": (target.missing_frames),
                        "detector_ms": (detections.total_ms),
                        "tracking_ms": (tracks.tracking_ms),
                        "pipeline_ms": pipeline_ms,
                    }
                )

                processed_frames += 1

        finally:
            capture.release()

    print(f"Frames : {processed_frames}")
    print(f"FPS    : {source_fps:.2f}")
    print(f"Output : {args.output}")


if __name__ == "__main__":
    main()
