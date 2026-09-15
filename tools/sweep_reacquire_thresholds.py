from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sweep reacquire thresholds across evaluation scenarios."
    )

    parser.add_argument(
        "scenarios",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/benchmarks/threshold_sweep.csv"),
    )

    parser.add_argument(
        "--split",
        choices=(
            "tune",
            "validation",
            "all",
        ),
        default="tune",
    )

    return parser.parse_args()

def run_command(
    command: list[str],
) -> None:
    subprocess.run(
        command,
        check=True,
    )


def main() -> None:
    args = parse_args()

    if not args.scenarios.exists():
        raise FileNotFoundError(args.scenarios)

    with args.scenarios.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        scenarios = list(csv.DictReader(file))

    if args.split != "all":
        scenarios = [
            scenario
            for scenario in scenarios
            if scenario["split"] == args.split
        ]

    if not scenarios:
        raise RuntimeError("Scenario matrix contains no rows.")

    score_margins = (
        0.05,
        0.10,
        0.15,
    )

    confirm_frames_values = (
        1,
        2,
        3,
    )

    results: list[dict[str, object]] = []

    work_dir = Path("data/benchmarks/p26")

    work_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]

        video_path = scenario["video_path"]

        select_frame = scenario["select_frame"]

        select_x = scenario["select_x"]

        select_y = scenario["select_y"]

        for score_margin in score_margins:
            for confirm_frames in confirm_frames_values:
                run_name = f"{scenario_id}_m{score_margin:.2f}_c{confirm_frames}"

                replay_path = work_dir / f"{run_name}_replay.csv"

                summary_path = work_dir / f"{run_name}_summary.json"

                events_path = work_dir / f"{run_name}_events.csv"

                print(f"\n=== {run_name} ===")

                run_command(
                    [
                        sys.executable,
                        "-m",
                        "tools.evaluate_tracking",
                        video_path,
                        "--select-frame",
                        select_frame,
                        "--select-x",
                        select_x,
                        "--select-y",
                        select_y,
                        "--min-reacquire-score-margin",
                        str(score_margin),
                        "--reacquire-confirm-frames",
                        str(confirm_frames),
                        "--output",
                        str(replay_path),
                    ]
                )

                run_command(
                    [
                        sys.executable,
                        "-m",
                        "tools.analyze_tracking_replay",
                        str(replay_path),
                        "--output",
                        str(summary_path),
                        "--events-output",
                        str(events_path),
                    ]
                )

                summary = json.loads(summary_path.read_text(encoding="utf-8"))

                frames = summary["frames"]
                events = summary["events"]

                results.append(
                    {
                        "scenario_id": (scenario_id),
                        "split": (scenario["split"]),
                        "scenario": (scenario["scenario"]),
                        "score_margin": (score_margin),
                        "confirm_frames": (confirm_frames),
                        "locked_ratio": (frames["locked_ratio"]),
                        "lost_ratio": (frames["lost_ratio"]),
                        "id_switch_count": (events["id_switch_count"]),
                        "same_id_recovery_count": (events["same_id_recovery_count"]),
                        "new_id_reacquire_count": (events["new_id_reacquire_count"]),
                        "timeout_count": (events["timeout_count"]),
                        "pipeline_p95_ms": (summary["metrics_ms"]["pipeline"]["p95"]),
                    }
                )

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = (
        "scenario_id",
        "split",
        "scenario",
        "score_margin",
        "confirm_frames",
        "locked_ratio",
        "lost_ratio",
        "id_switch_count",
        "same_id_recovery_count",
        "new_id_reacquire_count",
        "timeout_count",
        "pipeline_p95_ms",
    )

    with args.output.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nThreshold sweep complete.")
    print(f"Runs   : {len(results)}")
    print(f"Output : {args.output}")


if __name__ == "__main__":
    main()
