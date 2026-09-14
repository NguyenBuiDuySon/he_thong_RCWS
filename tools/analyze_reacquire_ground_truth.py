from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import fmean

_VALID_LABELS = {
    "correct_reacquire",
    "false_reacquire",
    "uncertain",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze reacquire ground-truth annotations."
    )

    parser.add_argument(
        "ground_truth_csv",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/reacquire_ground_truth_summary.json"),
    )

    return parser.parse_args()


def optional_mean(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return fmean(values)


def summarize_ground_truth(
    rows: list[dict[str, str]],
) -> dict[str, object]:
    if not rows:
        raise ValueError("Ground-truth CSV contains no annotations.")

    counts = {
        "correct_reacquire": 0,
        "false_reacquire": 0,
        "uncertain": 0,
    }

    correct_lost_frames: list[float] = []
    correct_elapsed_s: list[float] = []

    false_lost_frames: list[float] = []
    false_elapsed_s: list[float] = []

    for row in rows:
        label = row["label"]

        if label not in _VALID_LABELS:
            raise ValueError(f"Unsupported annotation label: {label}")

        counts[label] += 1

        lost_frames = float(row["lost_status_frames"])

        elapsed_s = float(row["elapsed_s"])

        if label == "correct_reacquire":
            correct_lost_frames.append(lost_frames)

            correct_elapsed_s.append(elapsed_s)

        elif label == "false_reacquire":
            false_lost_frames.append(lost_frames)

            false_elapsed_s.append(elapsed_s)

    total = len(rows)

    correct = counts["correct_reacquire"]
    false = counts["false_reacquire"]
    uncertain = counts["uncertain"]

    evaluated = correct + false

    success_rate = correct / evaluated if evaluated > 0 else None

    false_rate = false / evaluated if evaluated > 0 else None

    return {
        "annotations": {
            "total": total,
            "evaluated": evaluated,
            "correct_reacquire": correct,
            "false_reacquire": false,
            "uncertain": uncertain,
        },
        "rates": {
            "success_rate": success_rate,
            "false_reacquire_rate": false_rate,
            "uncertain_rate": (uncertain / total),
            "annotation_coverage": (evaluated / total),
        },
        "correct_reacquire": {
            "mean_lost_status_frames": (optional_mean(correct_lost_frames)),
            "max_lost_status_frames": (
                max(correct_lost_frames) if correct_lost_frames else None
            ),
            "mean_elapsed_s": (optional_mean(correct_elapsed_s)),
            "max_elapsed_s": (max(correct_elapsed_s) if correct_elapsed_s else None),
        },
        "false_reacquire": {
            "mean_lost_status_frames": (optional_mean(false_lost_frames)),
            "max_lost_status_frames": (
                max(false_lost_frames) if false_lost_frames else None
            ),
            "mean_elapsed_s": (optional_mean(false_elapsed_s)),
            "max_elapsed_s": (max(false_elapsed_s) if false_elapsed_s else None),
        },
    }


def main() -> None:
    args = parse_args()

    if not args.ground_truth_csv.exists():
        raise FileNotFoundError(args.ground_truth_csv)

    with args.ground_truth_csv.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    summary = summarize_ground_truth(rows)

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    annotations = summary["annotations"]
    rates = summary["rates"]

    print("======= REACQUIRE GROUND TRUTH =======")
    print(f"Annotations : {annotations['total']}")
    print(f"Correct     : {annotations['correct_reacquire']}")
    print(f"False       : {annotations['false_reacquire']}")
    print(f"Uncertain   : {annotations['uncertain']}")

    success_rate = rates["success_rate"]
    false_rate = rates["false_reacquire_rate"]

    if success_rate is None:
        print("Success rate: N/A")
        print("False rate  : N/A")
    else:
        print(f"Success rate: {success_rate * 100:.2f}%")
        print(f"False rate  : {false_rate * 100:.2f}%")

    print(f"Output      : {args.output}")


if __name__ == "__main__":
    main()
