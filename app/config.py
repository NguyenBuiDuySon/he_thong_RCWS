from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True, slots=True)
class CameraConfig:
    source: int | str
    width: int
    height: int
    fps: int
    backend: str


@dataclass(frozen=True, slots=True)
class DetectorConfig:
    model: str
    device: str
    precision: str
    imgsz: int
    confidence: float
    max_det: int
    warmup_iterations: int


@dataclass(frozen=True, slots=True)
class TrackerConfig:
    algorithm: str

    lost_track_buffer: int
    track_activation_threshold: float
    minimum_consecutive_frames: int
    minimum_iou_threshold: float
    high_conf_det_threshold: float


@dataclass(frozen=True, slots=True)
class TelemetryConfig:
    rolling_window_frames: int


@dataclass(frozen=True, slots=True)
class DisplayConfig:
    window_name: str
    show_crosshair: bool


@dataclass(frozen=True, slots=True)
class AppConfig:
    camera: CameraConfig
    detector: DetectorConfig
    tracker: TrackerConfig
    telemetry: TelemetryConfig
    display: DisplayConfig


def load_config(
    path: str | Path,
) -> AppConfig:
    config_path = Path(path)

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw = yaml.safe_load(file)

    camera = raw["camera"]
    detector = raw["detector"]
    tracker = raw["tracker"]
    telemetry = raw["telemetry"]
    display = raw["display"]

    return AppConfig(
        camera=CameraConfig(
            source=camera["source"],
            width=int(camera["width"]),
            height=int(camera["height"]),
            fps=int(camera["fps"]),
            backend=str(
                camera.get(
                    "backend",
                    "auto",
                )
            ).lower(),
        ),
        detector=DetectorConfig(
            model=str(detector["model"]),
            device=str(
                detector.get(
                    "device",
                    "auto",
                )
            ).lower(),
            precision=str(
                detector.get(
                    "precision",
                    "auto",
                )
            ).lower(),
            imgsz=int(
                detector.get(
                    "imgsz",
                    640,
                )
            ),
            confidence=float(
                detector.get(
                    "confidence",
                    0.25,
                )
            ),
            max_det=int(
                detector.get(
                    "max_det",
                    100,
                )
            ),
            warmup_iterations=max(
                0,
                int(
                    detector.get(
                        "warmup_iterations",
                        10,
                    )
                ),
            ),
        ),
        tracker=TrackerConfig(
            algorithm=str(
                tracker.get(
                    "algorithm",
                    "bytetrack",
                )
            ).lower(),
            lost_track_buffer=max(
                0,
                int(
                    tracker.get(
                        "lost_track_buffer",
                        30,
                    )
                ),
            ),
            track_activation_threshold=float(
                tracker.get(
                    "track_activation_threshold",
                    0.70,
                )
            ),
            minimum_consecutive_frames=max(
                1,
                int(
                    tracker.get(
                        "minimum_consecutive_frames",
                        2,
                    )
                ),
            ),
            minimum_iou_threshold=float(
                tracker.get(
                    "minimum_iou_threshold",
                    0.10,
                )
            ),
            high_conf_det_threshold=float(
                tracker.get(
                    "high_conf_det_threshold",
                    0.60,
                )
            ),
        ),
        telemetry=TelemetryConfig(
            rolling_window_frames=max(
                10,
                int(
                    telemetry.get(
                        "rolling_window_frames",
                        120,
                    )
                ),
            ),
        ),
        display=DisplayConfig(
            window_name=str(display["window_name"]),
            show_crosshair=bool(
                display.get(
                    "show_crosshair",
                    True,
                )
            ),
        ),
    )
