from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter_ns
from typing import ClassVar

import cv2
import numpy as np

from app.config import CameraConfig


@dataclass(slots=True)
class FramePacket:
    frame_id: int
    received_at_ns: int
    image: np.ndarray


class Camera:
    _BACKENDS: ClassVar[dict[str, int]] = {
        "auto": cv2.CAP_ANY,
        "dshow": cv2.CAP_DSHOW,
        "msmf": cv2.CAP_MSMF,
    }

    def __init__(
        self,
        config: CameraConfig,
    ) -> None:
        backend = self._BACKENDS.get(config.backend)

        if backend is None:
            raise ValueError(f"Unsupported backend: {config.backend}")

        self._capture = cv2.VideoCapture(
            config.source,
            backend,
        )

        if not self._capture.isOpened():
            raise RuntimeError(f"Cannot open camera: {config.source}")

        self._capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            config.width,
        )

        self._capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            config.height,
        )

        self._capture.set(
            cv2.CAP_PROP_FPS,
            config.fps,
        )

        self._frame_id = 0

    def read(
        self,
    ) -> FramePacket | None:
        ok, image = self._capture.read()

        received_at_ns = perf_counter_ns()

        if not ok or image is None:
            return None

        packet = FramePacket(
            frame_id=self._frame_id,
            received_at_ns=received_at_ns,
            image=image,
        )

        self._frame_id += 1

        return packet

    @property
    def backend_name(self) -> str:
        try:
            return self._capture.getBackendName()
        except cv2.error:
            return "unknown"

    @property
    def actual_width(self) -> int:
        return int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def actual_height(self) -> int:
        return int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def actual_fps(self) -> float:
        return float(self._capture.get(cv2.CAP_PROP_FPS))

    def close(self) -> None:
        self._capture.release()
