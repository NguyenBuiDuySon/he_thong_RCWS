from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import fmean, median

_VALID_LABELS = {
    "correct_reacquire",
    "false_reacquire",
    "uncertain",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Aggregate reacquire ground truth across the baseline dataset.")
    )

    parser.add_argument(
        "baseline_summary",
        type=Path,
    )

    parser.add_argument(
        "--annotations-dir",
        type=Path,
        default=Path("data/annotations"),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/reacquire_dataset_summary.json"),
    )

    parser.add_argument(
        "--per-scenario-output",
        type=Path,
        default=Path("data/benchmarks/reacquire_dataset_by_scenario.csv"),
    )

    return parser.parse_args()


def load_csv(
    path: Path,
) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def optional_mean(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return fmean(values)


def optional_median(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return median(values)


def optional_max(
    values: list[float],
) -> float | None:
    if not values:
        return None

    return max(values)


def summarize_annotations(
    *,
    expected_events: int,
    rows: list[dict[str, str]],
) -> dict[str, object]:
    counts = {
        "correct_reacquire": 0,
        "false_reacquire": 0,
        "uncertain": 0,
    }

    correct_lost_frames: list[float] = []
    correct_elapsed_s: list[float] = []

    for row in rows:
        label = row["label"]

        if label not in _VALID_LABELS:
            raise ValueError(f"Unsupported annotation label: {label}")

        counts[label] += 1

        if label == "correct_reacquire":
            correct_lost_frames.append(float(row["lost_status_frames"]))
            correct_elapsed_s.append(float(row["elapsed_s"]))

    annotated = len(rows)

    correct = counts["correct_reacquire"]
    false = counts["false_reacquire"]
    uncertain = counts["uncertain"]

    evaluated = correct + false

    return {
        "expected_events": expected_events,
        "annotated_events": annotated,
        "evaluated_events": evaluated,
        "correct_reacquire": correct,
        "false_reacquire": false,
        "uncertain": uncertain,
        "annotation_completion": (
            annotated / expected_events if expected_events > 0 else 1.0
        ),
        "evaluated_coverage": (
            evaluated / expected_events if expected_events > 0 else 1.0
        ),
        "success_rate": (correct / evaluated if evaluated > 0 else None),
        "false_reacquire_rate": (false / evaluated if evaluated > 0 else None),
        "uncertain_rate": (uncertain / annotated if annotated > 0 else 0.0),
        "correct_reacquire_timing": {
            "mean_lost_status_frames": (optional_mean(correct_lost_frames)),
            "median_lost_status_frames": (optional_median(correct_lost_frames)),
            "max_lost_status_frames": (optional_max(correct_lost_frames)),
            "mean_elapsed_s": (optional_mean(correct_elapsed_s)),
            "median_elapsed_s": (optional_median(correct_elapsed_s)),
            "max_elapsed_s": (optional_max(correct_elapsed_s)),
        },
    }


def main() -> None:
    args = parse_args()

    baseline_rows = load_csv(args.baseline_summary)

    if not baseline_rows:
        raise RuntimeError("Baseline summary contains no scenarios.")

    seen_ids: set[str] = set()

    all_annotations: list[dict[str, str]] = []

    split_annotations: dict[
        str,
        list[dict[str, str]],
    ] = defaultdict(list)

    split_expected: dict[str, int] = defaultdict(int)
    split_scenario_count: dict[str, int] = defaultdict(int)

    overall_expected = 0

    scenario_results: list[dict[str, object]] = []

    for baseline in baseline_rows:
        scenario_id = baseline["scenario_id"]

        if scenario_id in seen_ids:
            raise RuntimeError(
                f"Duplicate scenario_id in baseline summary: {scenario_id}"
            )

        seen_ids.add(scenario_id)

        split = baseline["split"]
        scenario = baseline["scenario"]

        expected_events = int(baseline["new_id_reacquire_count"])

        annotation_path = args.annotations_dir / (
            f"{scenario_id}_reacquire_ground_truth.csv"
        )

        if annotation_path.exists():
            annotations = load_csv(annotation_path)
        elif expected_events == 0:
            annotations = []
        else:
            raise FileNotFoundError(
                f"Missing ground truth for {scenario_id}: {annotation_path}"
            )

        if len(annotations) != expected_events:
            raise RuntimeError(
                f"{scenario_id}: baseline expects "
                f"{expected_events} new-ID events "
                f"but ground truth contains "
                f"{len(annotations)} annotations."
            )

        summary = summarize_annotations(
            expected_events=expected_events,
            rows=annotations,
        )

        scenario_results.append(
            {
                "scenario_id": scenario_id,
                "split": split,
                "scenario": scenario,
                **summary,
            }
        )

        overall_expected += expected_events
        all_annotations.extend(annotations)

        split_expected[split] += expected_events
        split_scenario_count[split] += 1
        split_annotations[split].extend(annotations)

    overall = summarize_annotations(
        expected_events=overall_expected,
        rows=all_annotations,
    )
    overall["scenario_count"] = len(baseline_rows)

    split_results: dict[
        str,
        dict[str, object],
    ] = {}

    for split in sorted(split_scenario_count):
        split_summary = summarize_annotations(
            expected_events=(split_expected[split]),
            rows=split_annotations[split],
        )

        split_summary["scenario_count"] = split_scenario_count[split]

        split_results[split] = split_summary

    result = {
        "dataset": overall,
        "splits": split_results,
        "scenarios": scenario_results,
    }

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    args.output.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    args.per_scenario_output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = (
        "scenario_id",
        "split",
        "scenario",
        "expected_events",
        "annotated_events",
        "evaluated_events",
        "correct_reacquire",
        "false_reacquire",
        "uncertain",
        "annotation_completion",
        "evaluated_coverage",
        "success_rate",
        "false_reacquire_rate",
        "uncertain_rate",
    )

    with args.per_scenario_output.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(scenario_results)

    print("======= REACQUIRE DATASET =======")
    print(f"Scenarios : {overall['scenario_count']}")
    print(f"Expected  : {overall['expected_events']}")
    print(f"Annotated : {overall['annotated_events']}")
    print(f"Evaluated : {overall['evaluated_events']}")
    print(f"Correct   : {overall['correct_reacquire']}")
    print(f"False     : {overall['false_reacquire']}")
    print(f"Uncertain : {overall['uncertain']}")

    success_rate = overall["success_rate"]

    false_rate = overall["false_reacquire_rate"]

    if success_rate is not None:
        print(f"Success   : {success_rate * 100:.2f}%")
        print(f"False rate: {false_rate * 100:.2f}%")

    print(f"JSON      : {args.output}")
    print(f"Scenario  : {args.per_scenario_output}")


if __name__ == "__main__":
    main()
