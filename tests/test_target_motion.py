from app.targeting.motion import (
    TargetMotionMemory,
)
from app.tracking.types import Track


def _track(
    *,
    center_x: float,
    center_y: float,
) -> Track:
    width = 100.0
    height = 200.0

    return Track(
        track_id=1,
        class_id=0,
        class_name="person",
        confidence=0.9,
        x1=center_x - width / 2.0,
        y1=center_y - height / 2.0,
        x2=center_x + width / 2.0,
        y2=center_y + height / 2.0,
    )


def test_first_sample_has_no_motion() -> None:
    memory = TargetMotionMemory()

    estimate = memory.update(
        frame_id=1,
        track=_track(
            center_x=500,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert estimate.direction_x == 0
    assert estimate.direction_y == 0
    assert estimate.sample_count == 0


def test_detects_right_motion() -> None:
    memory = TargetMotionMemory(
        alpha=1.0,
        direction_deadband=0.0,
    )

    memory.update(
        frame_id=1,
        track=_track(
            center_x=400,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    estimate = memory.update(
        frame_id=2,
        track=_track(
            center_x=420,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert estimate.direction_x == 1
    assert estimate.direction_y == 0


def test_detects_left_motion() -> None:
    memory = TargetMotionMemory(
        alpha=1.0,
        direction_deadband=0.0,
    )

    memory.update(
        frame_id=1,
        track=_track(
            center_x=500,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    estimate = memory.update(
        frame_id=2,
        track=_track(
            center_x=470,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert estimate.direction_x == -1


def test_detects_upward_motion() -> None:
    memory = TargetMotionMemory(
        alpha=1.0,
        direction_deadband=0.0,
    )

    memory.update(
        frame_id=1,
        track=_track(
            center_x=500,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    estimate = memory.update(
        frame_id=2,
        track=_track(
            center_x=500,
            center_y=270,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert estimate.direction_y == -1


def test_deadband_rejects_small_jitter() -> None:
    memory = TargetMotionMemory(
        alpha=1.0,
        direction_deadband=0.01,
    )

    memory.update(
        frame_id=1,
        track=_track(
            center_x=500,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    estimate = memory.update(
        frame_id=2,
        track=_track(
            center_x=505,
            center_y=302,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert estimate.direction_x == 0
    assert estimate.direction_y == 0


def test_motion_is_normalized_by_frame_gap() -> None:
    memory = TargetMotionMemory(
        alpha=1.0,
        direction_deadband=0.0,
    )

    memory.update(
        frame_id=10,
        track=_track(
            center_x=400,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    estimate = memory.update(
        frame_id=12,
        track=_track(
            center_x=440,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert abs(estimate.dx_norm_per_frame - 0.02) < 1e-9


def test_rebase_preserves_motion_estimate() -> None:
    memory = TargetMotionMemory(
        alpha=1.0,
        direction_deadband=0.0,
    )

    memory.update(
        frame_id=1,
        track=_track(
            center_x=400,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    before = memory.update(
        frame_id=2,
        track=_track(
            center_x=430,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    after = memory.rebase(
        frame_id=20,
        track=_track(
            center_x=700,
            center_y=300,
        ),
        frame_width=1000,
        frame_height=600,
    )

    assert after == before
    assert after.direction_x == 1
    assert after.sample_count == 1
