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
class TargetingConfig:
    lost_timeout_frames: int
    dead_zone_x_norm: float
    dead_zone_y_norm: float
    control_filter_tau_ms: float


@dataclass(frozen=True, slots=True)
class ControlConfig:
    kp_pan: float
    kp_tilt: float
    max_pan_command: float
    max_tilt_command: float
    pan_rate_per_s: float
    tilt_rate_per_s: float


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
    targeting: TargetingConfig
    control: ControlConfig
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
    targeting = raw.get("targeting", {})
    control = raw.get("control", {})
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
        targeting=TargetingConfig(
            lost_timeout_frames=max(
                1,
                int(
                    targeting.get(
                        "lost_timeout_frames",
                        90,
                    )
                ),
            ),
            dead_zone_x_norm=float(
                targeting.get(
                    "dead_zone_x_norm",
                    0.05,
                )
            ),
            dead_zone_y_norm=float(
                targeting.get(
                    "dead_zone_y_norm",
                    0.05,
                )
            ),
            control_filter_tau_ms=max(
                0.0,
                float(
                    targeting.get(
                        "control_filter_tau_ms",
                        70.0,
                    )
                ),
            ),
        ),
        control=ControlConfig(
            kp_pan=float(
                control.get(
                    "kp_pan",
                    1.0,
                )
            ),
            kp_tilt=float(
                control.get(
                    "kp_tilt",
                    1.0,
                )
            ),
            max_pan_command=float(
                control.get(
                    "max_pan_command",
                    1.0,
                )
            ),
            max_tilt_command=float(
                control.get(
                    "max_tilt_command",
                    1.0,
                )
            ),
            pan_rate_per_s=float(
                control.get(
                    "pan_rate_per_s",
                    2.0,
                )
            ),
            tilt_rate_per_s=float(
                control.get(
                    "tilt_rate_per_s",
                    2.0,
                )
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
