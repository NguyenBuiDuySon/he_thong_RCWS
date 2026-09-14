import pytest

from tools.analyze_reacquire_ground_truth import (
    summarize_ground_truth,
)


def make_row(
    label: str,
    *,
    lost_frames: int,
    elapsed_s: float,
) -> dict[str, str]:
    return {
        "label": label,
        "lost_status_frames": str(lost_frames),
        "elapsed_s": str(elapsed_s),
    }


def test_summarizes_reacquire_ground_truth() -> None:
    summary = summarize_ground_truth(
        [
            make_row(
                "correct_reacquire",
                lost_frames=1,
                elapsed_s=0.03,
            ),
            make_row(
                "correct_reacquire",
                lost_frames=31,
                elapsed_s=1.08,
            ),
            make_row(
                "false_reacquire",
                lost_frames=4,
                elapsed_s=0.14,
            ),
            make_row(
                "uncertain",
                lost_frames=2,
                elapsed_s=0.07,
            ),
        ]
    )

    assert summary["annotations"] == {
        "total": 4,
        "evaluated": 3,
        "correct_reacquire": 2,
        "false_reacquire": 1,
        "uncertain": 1,
    }

    assert summary["rates"]["success_rate"] == pytest.approx(2 / 3)

    assert summary["rates"]["false_reacquire_rate"] == pytest.approx(1 / 3)


def test_rejects_unknown_annotation_label() -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported annotation label",
    ):
        summarize_ground_truth(
            [
                make_row(
                    "maybe",
                    lost_frames=1,
                    elapsed_s=0.03,
                )
            ]
        )
