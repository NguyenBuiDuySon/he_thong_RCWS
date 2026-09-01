from __future__ import annotations

from abc import ABC, abstractmethod

from app.capture.camera import FramePacket
from app.detection.types import DetectionBatch
from app.tracking.types import TrackBatch


class Tracker(ABC):
    @abstractmethod
    def update(
        self,
        packet: FramePacket,
        detections: DetectionBatch,
    ) -> TrackBatch:
        """Update tracker state for one frame."""

    @abstractmethod
    def reset(self) -> None:
        """Clear all tracker state."""
