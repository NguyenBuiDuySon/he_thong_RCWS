from __future__ import annotations

from app.targeting.manager import TargetManager
from app.targeting.types import TargetStatus
from app.tracking.types import (
    Track,
    TrackBatch,
)


def make_track(
    track_id: int,
    class_name: str = "object",
    *,
    class_id: int = 0,
    x1: float = 10.0,
    y1: float = 20.0,
    x2: float = 110.0,
    y2: float = 220.0,
) -> Track:
    return Track(
        track_id=track_id,
        class_id=class_id,
        class_name=class_name,
        confidence=0.9,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )


def make_batch(
    frame_id: int,
    *tracks: Track,
) -> TrackBatch:
    return TrackBatch(
        frame_id=frame_id,
        tracking_ms=0.4,
        tracks=tuple(tracks),
        unconfirmed_count=0,
    )


def test_starts_idle() -> None:
    manager = TargetManager()

    snapshot = manager.update(
        make_batch(
            1,
            make_track(1),
        )
    )

    assert snapshot.status is TargetStatus.IDLE

    assert snapshot.selected_track_id is None


def test_locks_selected_track() -> None:
    manager = TargetManager()

    manager.select(9, 0)

    snapshot = manager.update(
        make_batch(
            1,
            make_track(6),
            make_track(8),
            make_track(
                9,
                "person",
            ),
        )
    )

    assert snapshot.status is TargetStatus.LOCKED

    assert snapshot.selected_track_id == 9

    assert snapshot.track is not None

    assert snapshot.track.track_id == 9


def test_does_not_switch_target() -> None:
    manager = TargetManager()

    manager.select(9, 0)

    snapshot = manager.update(
        make_batch(
            2,
            make_track(6),
            make_track(8),
        )
    )

    assert snapshot.status is TargetStatus.LOST

    assert snapshot.selected_track_id == 9

    assert snapshot.track is None

    assert snapshot.missing_frames == 1


def test_recovers_same_track_id() -> None:
    manager = TargetManager(
        lost_timeout_frames=3,
    )

    manager.select(9, 0)

    manager.update(
        make_batch(
            1,
            make_track(6),
        )
    )

    lost = manager.update(
        make_batch(
            2,
            make_track(6),
        )
    )

    recovered = manager.update(
        make_batch(
            3,
            make_track(9),
        )
    )

    assert lost.status is TargetStatus.LOST

    assert recovered.status is TargetStatus.LOCKED

    assert recovered.missing_frames == 0


def test_clear_returns_to_idle() -> None:
    manager = TargetManager()

    manager.select(9, 0)
    manager.clear()

    snapshot = manager.update(
        make_batch(
            1,
            make_track(9),
        )
    )

    assert snapshot.status is TargetStatus.IDLE


def test_rejects_negative_track_id() -> None:
    manager = TargetManager()

    try:
        manager.select(
            -1,
            0,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")


def test_lost_target_times_out_to_idle() -> None:
    manager = TargetManager(
        lost_timeout_frames=3,
    )

    manager.select(9, 0)

    first_missing = manager.update(make_batch(1))

    second_missing = manager.update(make_batch(2))

    timed_out = manager.update(make_batch(3))

    assert first_missing.status is TargetStatus.LOST
    assert first_missing.missing_frames == 1

    assert second_missing.status is TargetStatus.LOST
    assert second_missing.missing_frames == 2

    assert timed_out.status is TargetStatus.IDLE
    assert timed_out.selected_track_id is None
    assert timed_out.track is None
    assert timed_out.missing_frames == 0

    assert manager.selected_track_id is None


def test_does_not_relock_after_timeout() -> None:
    manager = TargetManager(
        lost_timeout_frames=2,
    )

    manager.select(9, 0)

    manager.update(make_batch(1))

    timed_out = manager.update(make_batch(2))

    returned = manager.update(
        make_batch(
            3,
            make_track(
                9,
                "person",
            ),
        )
    )

    assert timed_out.status is TargetStatus.IDLE

    assert returned.status is TargetStatus.IDLE
    assert returned.selected_track_id is None


def test_same_track_id_different_class_is_lost() -> None:
    manager = TargetManager(
        lost_timeout_frames=3,
    )

    manager.select(9, 0)

    locked = manager.update(
        make_batch(
            1,
            make_track(
                9,
                "person",
            ),
        )
    )

    changed_class = Track(
        track_id=9,
        class_id=1,
        class_name="bicycle",
        confidence=0.9,
        x1=10.0,
        y1=20.0,
        x2=110.0,
        y2=220.0,
    )

    lost = manager.update(
        make_batch(
            2,
            changed_class,
        )
    )

    assert locked.status is TargetStatus.LOCKED

    assert lost.status is TargetStatus.LOST
    assert lost.selected_track_id == 9
    assert lost.track is None
    assert lost.missing_frames == 1


def test_recovers_only_same_track_and_class() -> None:
    manager = TargetManager(
        lost_timeout_frames=4,
    )

    manager.select(
        9,
        0,
    )

    wrong_class = Track(
        track_id=9,
        class_id=1,
        class_name="bicycle",
        confidence=0.9,
        x1=10.0,
        y1=20.0,
        x2=110.0,
        y2=220.0,
    )

    lost = manager.update(
        make_batch(
            1,
            wrong_class,
        )
    )

    recovered = manager.update(
        make_batch(
            2,
            make_track(
                9,
                "person",
            ),
        )
    )

    assert lost.status is TargetStatus.LOST
    assert recovered.status is TargetStatus.LOCKED
    assert recovered.track is not None
    assert recovered.track.class_id == 0
    assert recovered.missing_frames == 0


def test_rejects_negative_class_id() -> None:
    manager = TargetManager()

    try:
        manager.select(
            9,
            -1,
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError")

def test_reacquires_new_track_id_near_last_target() -> None:
    manager = TargetManager(
        lost_timeout_frames=10,
    )

    manager.select(
        0,
        0,
    )

    locked = manager.update(
        make_batch(
            100,
            make_track(
                0,
                "person",
                x1=400.0,
                y1=160.0,
                x2=600.0,
                y2=640.0,
            ),
        )
    )

    manager.update(
        make_batch(101)
    )

    manager.update(
        make_batch(102)
    )

    reacquired = manager.update(
        make_batch(
            103,
            make_track(
                4,
                "person",
                x1=420.0,
                y1=170.0,
                x2=620.0,
                y2=650.0,
            ),
        )
    )

    assert locked.status is TargetStatus.LOCKED
    assert locked.selected_track_id == 0

    assert reacquired.status is TargetStatus.LOCKED
    assert reacquired.selected_track_id == 4
    assert reacquired.track is not None
    assert reacquired.track.track_id == 4
    assert reacquired.missing_frames == 0


def test_reacquire_prefers_nearby_same_class_candidate() -> None:
    manager = TargetManager(
        lost_timeout_frames=10,
    )

    manager.select(
        0,
        0,
    )

    manager.update(
        make_batch(
            200,
            make_track(
                0,
                "person",
                x1=400.0,
                y1=160.0,
                x2=600.0,
                y2=640.0,
            ),
        )
    )

    lost = manager.update(
        make_batch(201)
    )

    reacquired = manager.update(
        make_batch(
            202,
            # Person khác, cùng class nhưng ở xa.
            make_track(
                3,
                "person",
                x1=40.0,
                y1=180.0,
                x2=220.0,
                y2=630.0,
            ),
            # Target cũ xuất hiện lại nhưng ByteTrack cấp ID mới.
            make_track(
                4,
                "person",
                x1=415.0,
                y1=165.0,
                x2=615.0,
                y2=645.0,
            ),
        )
    )

    assert lost.status is TargetStatus.LOST
    assert lost.selected_track_id == 0

    assert reacquired.status is TargetStatus.LOCKED
    assert reacquired.selected_track_id == 4
    assert reacquired.track is not None
    assert reacquired.track.track_id == 4
    assert reacquired.missing_frames == 0