from __future__ import annotations

from abc import ABC, abstractmethod

from app.capture.camera import FramePacket
from app.detection.types import DetectionBatch


class Detector(ABC):
    @abstractmethod
    def detect(
        self,
        packet: FramePacket,
    ) -> DetectionBatch:
        """Detect objects in one frame."""

    def warmup(
        self,
        packet: FramePacket,
        iterations: int = 10,
    ) -> None:
        for _ in range(
            max(0, iterations)
        ):
            self.detect(packet)