from app.targeting.selection import (
    pick_track_at_point,
)
from app.tracking.types import (
    Track,
    TrackBatch,
)


def make_track(
    track_id: int,
    *,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> Track:
    return Track(
        track_id=track_id,
        class_id=0,
        class_name="object",
        confidence=0.9,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )


def make_batch(
    *tracks: Track,
) -> TrackBatch:
    return TrackBatch(
        frame_id=1,
        tracking_ms=0.4,
        tracks=tuple(tracks),
        unconfirmed_count=0,
    )


def test_selects_track_containing_point() -> None:
    batch = make_batch(
        make_track(
            9,
            x1=100,
            y1=100,
            x2=300,
            y2=400,
        )
    )

    track = pick_track_at_point(
        batch,
        200,
        200,
    )

    assert track is not None
    assert track.track_id == 9


def test_returns_none_outside_tracks() -> None:
    batch = make_batch(
        make_track(
            9,
            x1=100,
            y1=100,
            x2=300,
            y2=400,
        )
    )

    track = pick_track_at_point(
        batch,
        500,
        500,
    )

    assert track is None


def test_prefers_smaller_overlapping_box() -> None:
    batch = make_batch(
        make_track(
            1,
            x1=0,
            y1=0,
            x2=1000,
            y2=700,
        ),
        make_track(
            9,
            x1=100,
            y1=100,
            x2=300,
            y2=400,
        ),
    )

    track = pick_track_at_point(
        batch,
        200,
        200,
    )

    assert track is not None
    assert track.track_id == 9
