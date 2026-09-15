# CHECKPOINT

Updated: 2026-09-15

## Current branch

feat/vision-p2-evaluation

Known HEAD after P2 evaluation assets:

ba48547

## Current phase

P2 — Full Tracking Evaluation

Status: ACTIVE

## Verification checkpoint

PC Vision:

- `uv run ruff check .` — PASS
- `uv run pytest -q` — 105 passed

Focused Smart Reacquire:

- P1 implementation — DONE
- geometry diagnostics unit tests — PASS

## P1 — Smart Reacquire

Status: DONE

Implemented:

- LastTargetMemory
- same-class gating
- normalized center-distance gate
- bbox scale gate
- aspect-ratio gate
- candidate scoring
- ambiguity rejection
- multi-frame confirmation
- per-frame reacquire diagnostics
- geometry rejection diagnostics

Current baseline:

- max center distance norm: 1.0
- max scale ratio: 2.5
- max aspect-ratio ratio: 1.8
- min reacquire score margin: 0.10
- reacquire confirmation: 2 frames
- lost timeout: 90 frames

Do not change these thresholds without recorded evaluation evidence.

## P2 — Tracking Evaluation

Completed infrastructure:

- recorded full-pipeline replay
- replay CSV export
- target bbox export
- recovery / timeout event analysis
- same-ID vs new-ID reacquire classification
- human ground-truth annotation tool
- ground-truth metric analyzer
- tune / validation scenario matrix
- automated threshold sweep
- ambiguity score-gap diagnostics
- geometry-gate rejection diagnostics

Dataset definition:

- tune: test1, test3, test5, test6
- validation: test2, test4, test7

Recorded videos are local and intentionally not tracked by Git.

Human ground truth currently committed:

- test1
- 3 new-ID reacquire events
- 3 correct
- 0 false
- 0 uncertain

## P2.6 observations so far

Threshold sweep:

- score margins 0.05 / 0.10 / 0.15 produced no meaningful behavioral difference on current tune data
- confirm=3 increased LOST time without demonstrated benefit
- confirm=1 can produce direct LOCKED-ID switches
- baseline confirm=2 remains preferred

Current baseline remains:

- score margin = 0.10
- confirm frames = 2

Ambiguity diagnostic on test6:

- reacquire attempt frames: 4
- multi-candidate frames: 0
- ambiguous rejection frames: 0
- score gap: unavailable because no frame had >=2 valid candidates

Interpretation:

geometry gating currently removes competing candidates before ambiguity scoring.

## Current substage

P2.6F — Geometry gate diagnostics

Implementation: DONE
Unit tests: PASS
Real-video evaluation: PENDING

Immediate next action:

1. regenerate test6 replay using current geometry diagnostics
2. analyze rejection totals
3. inspect center / scale / aspect rejection distribution
4. only then decide whether any geometry threshold needs tuning

Do not widen geometry gates without evidence.

## ReID

Status: DEFERRED

Do not implement P3 ReID yet.

Reason:

current data has not demonstrated a persistent false-reacquire problem that requires appearance embeddings.

## ESP32 / Hardware

Branch:

feat/esp32-actuator-output

Status:

software actuator path checkpointed.

Pending:

physical STEP / DIR / ENABLE verification with real ESP32-S3 + DM542 + motor hardware.

Do not perform final motor calibration before physical verification.

## Resume instructions

For a new session:

1. read PROJECT_CHARTER.md
2. read ARCHITECTURE.md
3. read ROADMAP.md
4. read DECISIONS.md
5. read this CHECKPOINT.md
6. verify current Git branch / HEAD
7. run `uv run ruff check .`
8. run `uv run pytest -q`
9. continue only from "Immediate next action"