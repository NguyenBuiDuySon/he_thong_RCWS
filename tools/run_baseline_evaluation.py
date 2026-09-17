from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

_BASELINE_SCORE_MARGIN = 0.10
_BASELINE_CONFIRM_FRAMES = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the fixed tracking baseline across evaluation scenarios."
    )

    parser.add_argument(
        "scenarios",
        type=Path,
    )

    parser.add_argument(
        "--split",
        choices=("all", "tune", "validation"),
        default="all",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/benchmarks/baseline"),
    )

    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("data/benchmarks/baseline_summary.csv"),
    )

    return parser.parse_args()


def run_command(
    command: list[str],
) -> None:
    subprocess.run(
        command,
        check=True,
    )


def load_scenarios(
    path: Path,
    *,
    split: str,
) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        scenarios = list(csv.DictReader(file))

    if split != "all":
        scenarios = [scenario for scenario in scenarios if scenario["split"] == split]

    if not scenarios:
        raise RuntimeError("Scenario matrix contains no matching rows.")

    scenario_ids = [scenario["scenario_id"] for scenario in scenarios]

    if len(scenario_ids) != len(set(scenario_ids)):
        raise RuntimeError("Scenario matrix contains duplicate scenario_id values.")

    return scenarios


def main() -> None:
    args = parse_args()

    scenarios = load_scenarios(
        args.scenarios,
        split=args.split,
    )

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results: list[dict[str, object]] = []

    for index, scenario in enumerate(
        scenarios,
        start=1,
    ):
        scenario_id = scenario["scenario_id"]
        video_path = Path(scenario["video_path"])

        if not video_path.exists():
            raise FileNotFoundError(video_path)

        select_frame = scenario["select_frame"]

        select_x = scenario["select_x"]
        select_y = scenario["select_y"]

        replay_path = args.output_dir / f"{scenario_id}_replay.csv"

        analysis_path = args.output_dir / f"{scenario_id}_summary.json"

        events_path = args.output_dir / f"{scenario_id}_events.csv"

        print(f"\n[{index}/{len(scenarios)}] {scenario_id}: {scenario['scenario']}")

        run_command(
            [
                sys.executable,
                "-m",
                "tools.evaluate_tracking",
                str(video_path),
                "--select-frame",
                select_frame,
                "--select-x",
                select_x,
                "--select-y",
                select_y,
                "--min-reacquire-score-margin",
                str(_BASELINE_SCORE_MARGIN),
                "--reacquire-confirm-frames",
                str(_BASELINE_CONFIRM_FRAMES),
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
                str(analysis_path),
                "--events-output",
                str(events_path),
            ]
        )

        summary = json.loads(analysis_path.read_text(encoding="utf-8"))

        frames = summary["frames"]
        events = summary["events"]
        metrics = summary["metrics_ms"]
        diagnostics = summary["reacquire_diagnostics"]
        geometry = diagnostics["geometry_gate"]

        results.append(
            {
                "scenario_id": scenario_id,
                "split": scenario["split"],
                "scenario": (scenario["scenario"]),
                "frames": frames["total"],
                "locked_ratio": (frames["locked_ratio"]),
                "lost_ratio": (frames["lost_ratio"]),
                "same_id_recovery_count": (events["same_id_recovery_count"]),
                "new_id_reacquire_count": (events["new_id_reacquire_count"]),
                "id_switch_count": (events["id_switch_count"]),
                "timeout_count": (events["timeout_count"]),
                "multi_candidate_frames": (diagnostics["multi_candidate_frames"]),
                "ambiguous_rejection_frames": (
                    diagnostics["ambiguous_rejection_frames"]
                ),
                "same_class_tracks": (geometry["same_class_tracks"]),
                "valid_candidates": (geometry["valid_candidates"]),
                "rejected_center": (geometry["rejected_center"]),
                "rejected_scale": (geometry["rejected_scale"]),
                "rejected_aspect": (geometry["rejected_aspect"]),
                "pipeline_p95_ms": (metrics["pipeline"]["p95"]),
            }
        )

    args.summary.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = (
        "scenario_id",
        "split",
        "scenario",
        "frames",
        "locked_ratio",
        "lost_ratio",
        "same_id_recovery_count",
        "new_id_reacquire_count",
        "id_switch_count",
        "timeout_count",
        "multi_candidate_frames",
        "ambiguous_rejection_frames",
        "same_class_tracks",
        "valid_candidates",
        "rejected_center",
        "rejected_scale",
        "rejected_aspect",
        "pipeline_p95_ms",
    )

    with args.summary.open(
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

    print("\n========== BASELINE DATASET ==========")
    print(f"Scenarios : {len(results)}")
    print(f"Margin    : {_BASELINE_SCORE_MARGIN}")
    print(f"Confirm   : {_BASELINE_CONFIRM_FRAMES}")
    print(f"Summary   : {args.summary}")


if __name__ == "__main__":
    main()
