from __future__ import annotations

import argparse
import json
import platform
import sys

from datetime import datetime
from pathlib import Path
from time import perf_counter, perf_counter_ns

import cv2
import torch
import ultralytics

from app.capture.camera import FramePacket
from app.config import load_config
from app.detection.yolo_detector import YoloDetector
from app.telemetry.stats import MetricSeries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark detector "
            "on a fixed video."
        )
    )

    parser.add_argument(
        "video",
        type=Path,
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "configs/default.yaml"
        ),
    )

    parser.add_argument(
        "--warmup",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help=(
            "Maximum benchmark frames. "
            "0 means all frames."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/benchmarks/"
            "detector_baseline.json"
        ),
    )

    return parser.parse_args()


def warmup_detector(
    detector: YoloDetector,
    frame,
    iterations: int,
) -> None:
    print(
        f"Warm-up: {iterations} iterations"
    )

    for index in range(iterations):
        packet = FramePacket(
            frame_id=-(index + 1),
            received_at_ns=perf_counter_ns(),
            image=frame,
        )

        detector.detect(
            packet
        )


def main() -> None:
    args = parse_args()

    if not args.video.exists():
        raise FileNotFoundError(
            args.video
        )

    config = load_config(
        args.config
    )

    detector = YoloDetector(
        config.detector
    )

    capture = cv2.VideoCapture(
        str(args.video)
    )

    if not capture.isOpened():
        raise RuntimeError(
            f"Cannot open video: "
            f"{args.video}"
        )

    source_width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    source_height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    source_fps = float(
        capture.get(
            cv2.CAP_PROP_FPS
        )
    )

    source_frames = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    ok, warmup_frame = capture.read()

    if not ok:
        capture.release()
        raise RuntimeError(
            "Cannot read warm-up frame."
        )

    warmup_detector(
        detector,
        warmup_frame,
        max(
            0,
            args.warmup,
        ),
    )

    capture.set(
        cv2.CAP_PROP_POS_FRAMES,
        0,
    )

    decode_stats = MetricSeries()
    preprocess_stats = MetricSeries()
    inference_stats = MetricSeries()
    postprocess_stats = MetricSeries()
    detector_total_stats = MetricSeries()
    frame_age_stats = MetricSeries()
    detection_count_stats = MetricSeries()

    processed_frames = 0

    benchmark_started = perf_counter()

    try:
        while True:
            if (
                args.limit > 0
                and processed_frames
                >= args.limit
            ):
                break

            decode_started_ns = (
                perf_counter_ns()
            )

            ok, frame = capture.read()

            decode_finished_ns = (
                perf_counter_ns()
            )

            if not ok:
                break

            decode_ms = (
                decode_finished_ns
                - decode_started_ns
            ) / 1_000_000

            packet = FramePacket(
                frame_id=processed_frames,
                received_at_ns=(
                    decode_finished_ns
                ),
                image=frame,
            )

            batch = detector.detect(
                packet
            )

            finished_ns = (
                perf_counter_ns()
            )

            frame_age_ms = (
                finished_ns
                - packet.received_at_ns
            ) / 1_000_000

            decode_stats.add(
                decode_ms
            )

            preprocess_stats.add(
                batch.preprocess_ms
            )

            inference_stats.add(
                batch.inference_ms
            )

            postprocess_stats.add(
                batch.postprocess_ms
            )

            detector_total_stats.add(
                batch.total_ms
            )

            frame_age_stats.add(
                frame_age_ms
            )

            detection_count_stats.add(
                len(
                    batch.detections
                )
            )

            processed_frames += 1

            if (
                processed_frames % 100
                == 0
            ):
                print(
                    f"Processed "
                    f"{processed_frames} frames"
                )

    finally:
        capture.release()

    benchmark_elapsed_s = (
        perf_counter()
        - benchmark_started
    )

    pipeline_fps = (
        processed_frames
        / benchmark_elapsed_s
        if benchmark_elapsed_s > 0
        else 0.0
    )

    realtime_factor = (
        pipeline_fps / source_fps
        if source_fps > 0
        else 0.0
    )

    gpu_name = None

    if torch.cuda.is_available():
        gpu_name = (
            torch.cuda.get_device_name(0)
        )

    result = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "ultralytics": (
                ultralytics.__version__
            ),
            "gpu": gpu_name,
        },
        "detector": {
            "model": config.detector.model,
            "device": detector.device,
            "precision": (
                detector.precision
            ),
            "imgsz": (
                config.detector.imgsz
            ),
            "confidence": (
                config
                .detector
                .confidence
            ),
            "max_det": (
                config.detector.max_det
            ),
        },
        "source": {
            "path": str(
                args.video.resolve()
            ),
            "width": source_width,
            "height": source_height,
            "fps": source_fps,
            "frames": source_frames,
        },
        "benchmark": {
            "warmup_iterations": (
                args.warmup
            ),
            "processed_frames": (
                processed_frames
            ),
            "elapsed_s": (
                benchmark_elapsed_s
            ),
            "pipeline_fps": (
                pipeline_fps
            ),
            "realtime_factor": (
                realtime_factor
            ),
        },
        "metrics_ms": {
            "decode": (
                decode_stats
                .summarize()
                .to_dict()
            ),
            "preprocess": (
                preprocess_stats
                .summarize()
                .to_dict()
            ),
            "inference": (
                inference_stats
                .summarize()
                .to_dict()
            ),
            "postprocess": (
                postprocess_stats
                .summarize()
                .to_dict()
            ),
            "detector_total": (
                detector_total_stats
                .summarize()
                .to_dict()
            ),
            "frame_age": (
                frame_age_stats
                .summarize()
                .to_dict()
            ),
        },
        "detections_per_frame": (
            detection_count_stats
            .summarize()
            .to_dict()
        ),
    }

    args.output.parent.mkdir(
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

    inference = (
        inference_stats.summarize()
    )

    detector_total = (
        detector_total_stats.summarize()
    )

    frame_age = (
        frame_age_stats.summarize()
    )

    print()
    print(
        "========== DETECTOR BENCHMARK =========="
    )

    print(
        f"Model      : "
        f"{config.detector.model}"
    )

    print(
        f"Device     : "
        f"{detector.device}"
    )

    print(
        f"Precision  : "
        f"{detector.precision}"
    )

    print(
        f"Frames     : "
        f"{processed_frames}"
    )

    print(
        f"Throughput : "
        f"{pipeline_fps:.2f} FPS"
    )

    print(
        f"Realtime x : "
        f"{realtime_factor:.2f}x"
    )

    print()

    print(
        "MODEL INFERENCE"
    )

    print(
        f"mean : "
        f"{inference.mean:.2f} ms"
    )

    print(
        f"p50  : "
        f"{inference.p50:.2f} ms"
    )

    print(
        f"p95  : "
        f"{inference.p95:.2f} ms"
    )

    print(
        f"p99  : "
        f"{inference.p99:.2f} ms"
    )

    print()

    print(
        "DETECTOR TOTAL"
    )

    print(
        f"mean : "
        f"{detector_total.mean:.2f} ms"
    )

    print(
        f"p95  : "
        f"{detector_total.p95:.2f} ms"
    )

    print(
        f"p99  : "
        f"{detector_total.p99:.2f} ms"
    )

    print()

    print(
        "FRAME AGE"
    )

    print(
        f"mean : "
        f"{frame_age.mean:.2f} ms"
    )

    print(
        f"p95  : "
        f"{frame_age.p95:.2f} ms"
    )

    print(
        f"p99  : "
        f"{frame_age.p99:.2f} ms"
    )

    print()

    print(
        f"Saved: {args.output}"
    )


if __name__ == "__main__":
    main()