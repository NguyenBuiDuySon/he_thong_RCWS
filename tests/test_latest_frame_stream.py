from __future__ import annotations

from collections import deque

import numpy as np

from app.capture.camera import FramePacket
from app.capture.latest_frame import (
    LatestFrameStream,
)


class FakeCamera:
    def __init__(
        self,
        packets: list[FramePacket | None],
    ) -> None:
        self._packets = deque(packets)

    def read(self) -> FramePacket | None:
        if not self._packets:
            return None

        return self._packets.popleft()


def make_packet(
    frame_id: int,
) -> FramePacket:
    return FramePacket(
        frame_id=frame_id,
        received_at_ns=(1_000_000_000 + frame_id),
        image=np.zeros(
            (8, 8, 3),
            dtype=np.uint8,
        ),
    )


def test_stream_marks_stopped_after_camera_failure() -> None:
    camera = FakeCamera(
        [
            make_packet(0),
            None,
        ]
    )

    stream = LatestFrameStream(
        camera,  # type: ignore[arg-type]
    )

    stream.start()

    packet = stream.read(timeout=0.5)

    assert packet is not None

    stream.stop()

    assert stream.stopped


def test_stream_starts_not_stopped() -> None:
    camera = FakeCamera(
        [
            make_packet(0),
        ]
    )

    stream = LatestFrameStream(
        camera,  # type: ignore[arg-type]
    )

    assert not stream.stopped
