from app.targeting.reacquire import is_reacquire_candidate
from app.targeting.types import LastTargetMemory
from app.tracking.types import Track


def make_memory() -> LastTargetMemory:
    return LastTargetMemory(
        frame_id=100,
        track_id=0,
        class_id=0,
        class_name="person",
        confidence=0.9,
        x1=400.0,
        y1=160.0,
        x2=600.0,
        y2=640.0,
    )


def make_track(
    track_id: int,
    *,
    class_id: int = 0,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> Track:
    return Track(
        track_id=track_id,
        class_id=class_id,
        class_name="person",
        confidence=0.9,
        x1=x1,
        y1=y1,
        x2=x2,
        y2=y2,
    )


def test_accepts_nearby_same_class_candidate() -> None:
    memory = make_memory()

    candidate = make_track(
        4,
        x1=415.0,
        y1=165.0,
        x2=615.0,
        y2=645.0,
    )

    assert is_reacquire_candidate(
        memory,
        candidate,
    )


def test_rejects_different_class_candidate() -> None:
    memory = make_memory()

    candidate = make_track(
        4,
        class_id=1,
        x1=415.0,
        y1=165.0,
        x2=615.0,
        y2=645.0,
    )

    assert not is_reacquire_candidate(
        memory,
        candidate,
    )


def test_rejects_far_same_class_candidate() -> None:
    memory = make_memory()

    candidate = make_track(
        3,
        x1=40.0,
        y1=180.0,
        x2=220.0,
        y2=630.0,
    )

    assert not is_reacquire_candidate(
        memory,
        candidate,
    )