from __future__ import annotations

from app.tracking.types import Track, TrackBatch


def pick_track_at_point(
    batch: TrackBatch,
    x: int,
    y: int,
) -> Track | None:
    candidates = [
        track
        for track in batch.tracks
        if (track.x1 <= x <= track.x2 and track.y1 <= y <= track.y2)
    ]

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda track: track.width * track.height,
    )
