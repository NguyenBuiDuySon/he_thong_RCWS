from __future__ import annotations

import numpy as np
import pytest

from app.capture.camera import FramePacket
from app.detection.base import Detector
from app.detection.types import DetectionBatch
from app.perception import process_perception_frame
from app.tracking.base import Tracker
from app.tracking.types import TrackBatch


def make_packet() -> FramePacket:
    return FramePacket(
        frame_id=7,
        received_at_ns=1_000_000_000,
        image=np.zeros(
            (8, 8, 3),
            dtype=np.uint8,
        ),
    )


def make_detection_batch(
    frame_id: int,
) -> DetectionBatch:
    return DetectionBatch(
        frame_id=frame_id,
        preprocess_ms=0.0,
        inference_ms=0.0,
        postprocess_ms=0.0,
        total_ms=0.0,
        detections=(),
    )


class StaticDetector(Detector):
    def detect(
        self,
        packet: FramePacket,
    ) -> DetectionBatch:
        return make_detection_batch(packet.frame_id)


class FailingDetector(Detector):
    def detect(
        self,
        packet: FramePacket,
    ) -> DetectionBatch:
        raise RuntimeError("detector failed")


class StaticTracker(Tracker):
    def update(
        self,
        packet: FramePacket,
        detections: DetectionBatch,
    ) -> TrackBatch:
        return TrackBatch(
            frame_id=packet.frame_id,
            tracking_ms=0.0,
            tracks=(),
            unconfirmed_count=0,
        )

    def reset(self) -> None:
        pass


class FailingTracker(Tracker):
    def update(
        self,
        packet: FramePacket,
        detections: DetectionBatch,
    ) -> TrackBatch:
        raise RuntimeError("tracker failed")

    def reset(self) -> None:
        pass


def test_success_does_not_trigger_failure_callback() -> None:
    packet = make_packet()
    failure_calls = 0

    def on_failure() -> None:
        nonlocal failure_calls
        failure_calls += 1

    detections, tracks = process_perception_frame(
        packet,
        StaticDetector(),
        StaticTracker(),
        on_failure=on_failure,
    )

    assert detections.frame_id == 7
    assert tracks.frame_id == 7
    assert failure_calls == 0


def test_detector_failure_triggers_callback() -> None:
    packet = make_packet()
    failure_calls = 0

    def on_failure() -> None:
        nonlocal failure_calls
        failure_calls += 1

    with pytest.raises(
        RuntimeError,
        match="detector failed",
    ):
        process_perception_frame(
            packet,
            FailingDetector(),
            StaticTracker(),
            on_failure=on_failure,
        )

    assert failure_calls == 1


def test_tracker_failure_triggers_callback() -> None:
    packet = make_packet()
    failure_calls = 0

    def on_failure() -> None:
        nonlocal failure_calls
        failure_calls += 1

    with pytest.raises(
        RuntimeError,
        match="tracker failed",
    ):
        process_perception_frame(
            packet,
            StaticDetector(),
            FailingTracker(),
            on_failure=on_failure,
        )

    assert failure_calls == 1
