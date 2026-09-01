from __future__ import annotations

import numpy as np

from app.capture.camera import FramePacket
from app.config import TrackerConfig
from app.detection.types import (
    Detection,
    DetectionBatch,
)
from app.tracking.bytetrack_tracker import (
    ByteTrackAdapter,
)


def make_packet(
    frame_id: int,
    timestamp_s: float,
) -> FramePacket:
    return FramePacket(
        frame_id=frame_id,
        received_at_ns=int(timestamp_s * 1_000_000_000),
        image=np.zeros(
            (720, 1280, 3),
            dtype=np.uint8,
        ),
    )


def make_detection_batch(
    frame_id: int,
    x_offset: float = 0.0,
) -> DetectionBatch:
    detection = Detection(
        class_id=0,
        class_name="person",
        confidence=0.95,
        x1=100.0 + x_offset,
        y1=100.0,
        x2=300.0 + x_offset,
        y2=500.0,
    )

    return DetectionBatch(
        frame_id=frame_id,
        preprocess_ms=1.0,
        inference_ms=10.0,
        postprocess_ms=1.0,
        total_ms=12.0,
        detections=(detection,),
    )


def make_tracker() -> ByteTrackAdapter:
    config = TrackerConfig(
        algorithm="bytetrack",
        lost_track_buffer=30,
        track_activation_threshold=0.70,
        minimum_consecutive_frames=2,
        minimum_iou_threshold=0.10,
        high_conf_det_threshold=0.60,
    )

    return ByteTrackAdapter(
        config,
        frame_rate=30.0,
    )


def test_track_id_becomes_confirmed() -> None:
    tracker = make_tracker()

    first = tracker.update(
        make_packet(
            1,
            1.000,
        ),
        make_detection_batch(1),
    )

    second = tracker.update(
        make_packet(
            2,
            1.033,
        ),
        make_detection_batch(
            2,
            x_offset=3.0,
        ),
    )

    assert first.frame_id == 1
    assert second.frame_id == 2

    assert len(second.tracks) == 1

    track = second.tracks[0]

    assert track.track_id >= 0
    assert track.class_name == "person"


def test_track_id_persists() -> None:
    tracker = make_tracker()

    tracker.update(
        make_packet(
            1,
            1.000,
        ),
        make_detection_batch(1),
    )

    second = tracker.update(
        make_packet(
            2,
            1.033,
        ),
        make_detection_batch(
            2,
            x_offset=3.0,
        ),
    )

    third = tracker.update(
        make_packet(
            3,
            1.066,
        ),
        make_detection_batch(
            3,
            x_offset=6.0,
        ),
    )

    assert len(second.tracks) == 1
    assert len(third.tracks) == 1

    assert second.tracks[0].track_id == third.tracks[0].track_id


def test_rejects_mismatched_frame_id() -> None:
    tracker = make_tracker()

    packet = make_packet(
        10,
        1.0,
    )

    detections = make_detection_batch(
        9,
    )

    try:
        tracker.update(
            packet,
            detections,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")
