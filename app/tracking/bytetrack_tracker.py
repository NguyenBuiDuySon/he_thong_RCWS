from __future__ import annotations

from time import perf_counter_ns

import numpy as np
import supervision as sv
from trackers import ByteTrackTracker

from app.capture.camera import FramePacket
from app.config import TrackerConfig
from app.detection.types import DetectionBatch
from app.tracking.base import Tracker
from app.tracking.types import Track, TrackBatch


class ByteTrackAdapter(Tracker):
    def __init__(
        self,
        config: TrackerConfig,
        *,
        frame_rate: float,
    ) -> None:
        if frame_rate <= 0:
            raise ValueError("frame_rate must be > 0")

        self._tracker = ByteTrackTracker(
            lost_track_buffer=(config.lost_track_buffer),
            frame_rate=float(frame_rate),
            track_activation_threshold=(config.track_activation_threshold),
            minimum_consecutive_frames=(config.minimum_consecutive_frames),
            minimum_iou_threshold=(config.minimum_iou_threshold),
            high_conf_det_threshold=(config.high_conf_det_threshold),
        )

    def update(
        self,
        packet: FramePacket,
        detections: DetectionBatch,
    ) -> TrackBatch:
        if detections.frame_id != packet.frame_id:
            raise ValueError(
                "DetectionBatch frame_id does not match FramePacket frame_id."
            )

        started_ns = perf_counter_ns()

        sv_detections = self._to_supervision(detections)

        timestamp_s = packet.received_at_ns / 1_000_000_000

        tracked = self._tracker.update(
            sv_detections,
            timestamp=timestamp_s,
        )

        tracks, unconfirmed_count = self._from_supervision(
            tracked,
            detections,
        )

        tracking_ms = (perf_counter_ns() - started_ns) / 1_000_000

        return TrackBatch(
            frame_id=packet.frame_id,
            tracking_ms=tracking_ms,
            tracks=tracks,
            unconfirmed_count=(unconfirmed_count),
        )

    def reset(self) -> None:
        self._tracker.reset()

    @staticmethod
    def _to_supervision(
        batch: DetectionBatch,
    ) -> sv.Detections:
        if not batch.detections:
            return sv.Detections(
                xyxy=np.empty(
                    (0, 4),
                    dtype=np.float32,
                ),
                confidence=np.empty(
                    (0,),
                    dtype=np.float32,
                ),
                class_id=np.empty(
                    (0,),
                    dtype=np.int32,
                ),
            )

        xyxy = np.asarray(
            [
                (
                    detection.x1,
                    detection.y1,
                    detection.x2,
                    detection.y2,
                )
                for detection in batch.detections
            ],
            dtype=np.float32,
        )

        confidence = np.asarray(
            [detection.confidence for detection in batch.detections],
            dtype=np.float32,
        )

        class_id = np.asarray(
            [detection.class_id for detection in batch.detections],
            dtype=np.int32,
        )

        return sv.Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=class_id,
        )

    @staticmethod
    def _from_supervision(
        tracked: sv.Detections,
        source: DetectionBatch,
    ) -> tuple[tuple[Track, ...], int]:
        if len(tracked) == 0:
            return (), 0

        tracker_ids = tracked.tracker_id

        if tracker_ids is None:
            return (), len(tracked)

        class_names = {
            detection.class_id: detection.class_name for detection in source.detections
        }

        tracks: list[Track] = []
        unconfirmed_count = 0

        for index in range(len(tracked)):
            track_id = int(tracker_ids[index])

            if track_id < 0:
                unconfirmed_count += 1
                continue

            x1, y1, x2, y2 = tracked.xyxy[index]

            class_id = -1

            if tracked.class_id is not None:
                class_id = int(tracked.class_id[index])

            confidence = 0.0

            if tracked.confidence is not None:
                confidence = float(tracked.confidence[index])

            tracks.append(
                Track(
                    track_id=track_id,
                    class_id=class_id,
                    class_name=(
                        class_names.get(
                            class_id,
                            "unknown",
                        )
                    ),
                    confidence=confidence,
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                )
            )

        return (
            tuple(tracks),
            unconfirmed_count,
        )
