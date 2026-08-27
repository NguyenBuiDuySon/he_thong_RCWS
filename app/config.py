from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True, slots=True)
class CameraConfig:
    source: int
    width: int
    height: int
    fps: int
    backend: str


def load_camera_config(
    path: str | Path,
) -> CameraConfig:

    config_path = Path(path)

    with config_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw = yaml.safe_load(file)

    camera = raw["camera"]

    return CameraConfig(
        source=int(camera["source"]),
        width=int(camera["width"]),
        height=int(camera["height"]),
        fps=int(camera["fps"]),
        backend=str(
            camera.get("backend", "auto")
        ).lower(),
    )