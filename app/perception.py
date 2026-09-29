from __future__ import annotations

from collections.abc import Callable

from app.capture.camera import FramePacket
from app.detection.base import Detector
from app.detection.types import DetectionBatch
from app.tracking.base import Tracker
from app.tracking.types import TrackBatch


def process_perception_frame(
    packet: FramePacket,
    detector: Detector,
    tracker: Tracker,
    *,
    on_failure: Callable[[], None],
) -> tuple[
    DetectionBatch,
    TrackBatch,
]:
    try:
        detection_batch = detector.detect(packet)

        track_batch = tracker.update(
            packet,
            detection_batch,
        )

    except Exception:
        on_failure()
        raise

    return (
        detection_batch,
        track_batch,
    )
