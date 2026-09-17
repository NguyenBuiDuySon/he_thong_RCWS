import pytest

from tools.aggregate_reacquire_ground_truth import (
    summarize_annotations,
)


def make_row(
    label: str,
    *,
    lost_frames: int = 1,
    elapsed_s: float = 0.03,
) -> dict[str, str]:
    return {
        "label": label,
        "lost_status_frames": str(lost_frames),
        "elapsed_s": str(elapsed_s),
    }


def test_summarizes_dataset_annotations() -> None:
    summary = summarize_annotations(
        expected_events=3,
        rows=[
            make_row(
                "correct_reacquire",
                lost_frames=1,
                elapsed_s=0.03,
            ),
            make_row(
                "correct_reacquire",
                lost_frames=3,
                elapsed_s=0.10,
            ),
            make_row(
                "uncertain",
                lost_frames=2,
                elapsed_s=0.07,
            ),
        ],
    )

    assert summary["annotated_events"] == 3

    assert summary["evaluated_events"] == 2

    assert summary["correct_reacquire"] == 2

    assert summary["false_reacquire"] == 0

    assert summary["uncertain"] == 1

    assert summary["annotation_completion"] == pytest.approx(1.0)

    assert summary["evaluated_coverage"] == pytest.approx(2 / 3)

    assert summary["success_rate"] == pytest.approx(1.0)


def test_zero_event_scenario_is_complete() -> None:
    summary = summarize_annotations(
        expected_events=0,
        rows=[],
    )

    assert summary["annotation_completion"] == 1.0

    assert summary["evaluated_coverage"] == 1.0

    assert summary["success_rate"] is None
