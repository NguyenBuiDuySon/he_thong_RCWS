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

@dataclass(frozen=True, slots=True)
class DisplayConfig:
    window_name: str
    show_crosshair: bool


@dataclass(frozen=True, slots=True)
class AppConfig:
    camera: CameraConfig
    detector: DetectorConfig
    display: DisplayConfig


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw = yaml.safe_load(file)

    camera = raw["camera"]
    display = raw["display"]
    detector = raw["detector"]

    return AppConfig(
        camera=CameraConfig(
            source=camera["source"],
            width=int(camera["width"]),
            height=int(camera["height"]),
            fps=int(camera["fps"]),
            backend=str(
                camera.get("backend", "auto")
            ).lower(),
        ),
        detector=DetectorConfig(
            model=str(detector["model"]),
            device=str(
                detector.get("device", "auto")
            ).lower(),
            precision=str(
                detector.get("precision", "auto")
            ).lower(),
            imgsz=int(
                detector.get("imgsz", 640)
            ),
            confidence=float(
                detector.get("confidence", 0.25)
            ),
            max_det=int(
                detector.get("max_det", 100)
            ),
        ),

        display=DisplayConfig(
            window_name=str(
                display["window_name"]
            ),
            show_crosshair=bool(
                display.get(
                    "show_crosshair",
                    True,
                )
            ),
        ),
    )