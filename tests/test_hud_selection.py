from app.hud.overlay import _is_selected_track
from app.targeting.types import TargetSnapshot, TargetStatus
from app.tracking.types import Track


def make_track(
    track_id: int,
    class_id: int,
    class_name: str = "person",
) -> Track:
    return Track(
        track_id=track_id,
        class_id=class_id,
        class_name=class_name,
        confidence=0.9,
        x1=10.0,
        y1=20.0,
        x2=110.0,
        y2=220.0,
    )


def test_locked_target_is_highlighted() -> None:
    track = make_track(7, 0)

    target = TargetSnapshot(
        frame_id=10,
        status=TargetStatus.LOCKED,
        selected_track_id=7,
        track=track,
        missing_frames=0,
    )

    assert _is_selected_track(track, target)


def test_lost_target_is_not_highlighted() -> None:
    old_track = make_track(7, 0)

    target = TargetSnapshot(
        frame_id=11,
        status=TargetStatus.LOST,
        selected_track_id=7,
        track=None,
        missing_frames=1,
    )

    assert not _is_selected_track(old_track, target)


def test_same_id_different_class_is_not_highlighted() -> None:
    selected = make_track(7, 0, "person")
    other = make_track(7, 56, "chair")

    target = TargetSnapshot(
        frame_id=12,
        status=TargetStatus.LOCKED,
        selected_track_id=7,
        track=selected,
        missing_frames=0,
    )

    assert not _is_selected_track(other, target)
