# CHECKPOINT

## GUI OPERATE V2 acceptance
Update: 2026-10-09
Status: PASS
- six-block diagnostic dashboard accepted
- runtime snapshot verified
- input -> control -> output path remains visible
- event log reduced to operational size
- no backend/runtime logic changed
- final V1 OPERATE layout accepted
- live runtime data verified
- target selection verified
- MANUAL/AUTO status verified
- pan/tilt command display verified
- telemetry verified
- GUI initial appearance approximately 0.6–1.0 s

Further visual polish deferred.

## GUI G4 — Diagnostics acceptance
Update: 2026-10-07
Status: DONE

Verified live:
- performance telemetry
- target telemetry
- full MANUAL/AUTO control path
- event transition logging
- LOST -> REACQUIRED
- LOST -> TIMEOUT -> IDLE

Runtime remained near 30 FPS during validation.

Known UX issue:
rapid LOST/REACQUIRED transitions may make the Event Log noisy.
Defer coalescing to GUI polish.

Update: 2026-10-01

## Vision V1 — FROZEN

Status: SOFTWARE COMPLETE

### Pipeline đã chốt

Camera
-> Latest-frame capture
-> YOLO
-> ByteTrack
-> Operator Target Selection
-> TargetManager
-> Smart Reacquire
-> TargetObservation
-> TrackingErrorFilter
-> TrackingController
-> Vision Pan/Tilt Command

### Đã hoàn thiện

- phát hiện đối tượng bằng YOLO
- multi-object tracking bằng ByteTrack
- operator chọn target bằng chuột
- trạng thái IDLE / LOCKED / LOST
- LastTargetMemory
- Smart Reacquire
- geometry gating
- candidate scoring
- ambiguity rejection
- multi-frame confirmation
- lost timeout
- normalized target error
- dead zone
- error filtering
- P tracking controller
- failure -> OUTPUT STOP
- telemetry thời gian thực
- replay evaluation
- human ground-truth evaluation
- live robustness validation
- performance acceptance
- demo workflow stabilization

### Frozen Smart Reacquire baseline

- center distance norm: 1.0
- scale ratio: 2.5
- aspect-ratio ratio: 1.8
- score margin: 0.10
- confirmation: 2 frames
- lost timeout: 90 frames

### Performance checkpoint

- camera: 30 FPS
- live pipeline: 30 FPS
- offline pipeline p95: 20.74 ms
- offline pipeline p99: 25.51 ms

### Giới hạn hiện tại

- sau lost timeout, target chuyển về IDLE và operator phải chọn lại
- ReID chưa được sử dụng
- Manual ROI chưa thuộc Vision V1
- physical pan/tilt còn chờ tích hợp phần cứng

### Quyết định

Vision V1 được freeze.

Từ thời điểm này không thay đổi thuật toán Vision V1 nếu không có:

- lỗi tái hiện được; hoặc
- dữ liệu đánh giá mới chứng minh baseline hiện tại chưa phù hợp.

System V1 vẫn tiếp tục phát triển GUI, hardware pan/tilt và final integration.
Update: 2026-10-01
### VH5 — Demo Workflow Stabilization

Status: DONE

Verified:

- startup feedback
- MANUAL_GAMEPAD startup mode
- AUTO entry protection without active target
- target selection feedback
- MANUAL / AUTO mode switching
- live Vision tracking and reacquire
- return to manual control
- target clear -> IDLE
- Q / ESC safe exit -> OUTPUT STOP

The complete demo workflow has been exercised repeatedly during
Vision V1 hardening and Control V1 integration.
### VH4 — Performance / Latency Acceptance
Status: DONE

Offline detector benchmark:

- throughput: 64.86 FPS
- realtime factor: 2.16x
- inference mean: 9.64 ms
- inference p95: 13.23 ms
- detector total mean: 11.67 ms
- detector total p95: 15.63 ms
- detector total p99: 16.56 ms

Offline full-pipeline benchmark:

- detector mean: 12.08 ms
- detector p95: 16.03 ms
- tracker p95: 0.48 ms
- pipeline mean: 16.49 ms
- pipeline p95: 20.74 ms
- pipeline p99: 25.51 ms

Live acceptance:

- camera FPS: 30.0
- pipeline FPS: 30.0
- observed drop rate: 0.04-0.13%
- observed frame-age p95: 18.5-20.0 ms
- observed detector-total p95: 17.2-18.1 ms
- observed tracker p95: 0.33-0.60 ms

Decision:

Vision V1 meets the current 30 FPS software performance target.
No model, resolution, or precision change is justified by the
current performance measurements.
Update: 2026-09-30
### VH3 — Live Tracking Robustness

Status: DONE

Validated live scenarios:

- stable single target
- fast lateral movement
- large scale change
- partial occlusion
- short full occlusion
- two-person crossing
- exit / re-entry

Observed:

- brief LOST states may occur near frame boundaries or heavy occlusion
- correct reacquisition was observed after short disruptions
- no wrong-person switch was observed in the two-person crossing test
- long disappearance correctly reaches timeout and IDLE
- no current live evidence justifies changing the frozen P2 reacquire baseline

Decision:

Keep the current Vision V1 tracking and reacquire baseline unchanged.
Update: 2026-09-29
### VH2 — Target Selection / Operator UX

Status: DONE

Verified:

- left click selects a tracked target
- selection success shows operator feedback
- click miss shows SELECT MISS
- click miss does not clear an existing target
- selecting another track retargets immediately
- right click / C clears the target
- clear returns TargetManager to IDLE

## Vision V1 Hardening

Status: ACTIVE

### VH1 — Failure handling

Status: DONE

Completed:

- VH1.1 camera stream failure detection
- VH1.2 explicit output STOP on perception failure
- VH1.3 testable detector / tracker failure boundary
- VH1.4 live camera-loss / EOF smoke validation

Verified behavior:

- camera capture failure -> OUTPUT STOP
- camera frame timeout -> OUTPUT STOP
- detector exception -> OUTPUT STOP + exception propagation
- tracker exception -> OUTPUT STOP + exception propagation
- normal perception processing does not trigger false STOP
- video EOF exits cleanly
- physical camera starts normally after restoring live camera config

Immediate next action:

VH2 — Target Selection / Operator UX.
Update: 2026-09-25
## Control V1

Status: SOFTWARE COMPLETE

Completed:

- C1 Command arbitration
- C2 Gamepad input and mapping
- C3 MANUAL / AUTO mode switching
- C4A Vision + Gamepad integration
- C4B safety policy
- C4C HUD / configuration cleanup
- C5A automated integration tests
- C5B live integration validation
- C6 software acceptance

Verified:

- MANUAL_GAMEPAD controls output from gamepad
- AUTO_VISION controls output from Vision
- only one command source owns output at a time
- mode transition inserts STOP
- gamepad disconnect in MANUAL -> STOP
- gamepad disconnect in AUTO -> Vision continues
- target loss in AUTO -> STOP
- AUTO entry requires an active Vision target
- Vision may continue tracking while MANUAL is active

Software verification:

- `uv run ruff check .` — PASS
- `uv run pytest -q` — 130 passed
- live integration acceptance — PASS

Current limitation:

Physical actuator verification is pending hardware arrival.


Update: 2026-09-20
## Control V1

Status: ACTIVE

Completed:

- C1 CommandArbiter
- C2A gamepad command mapping
- C2B physical gamepad input
- C3A MANUAL / AUTO arbitration
- C3B RB mode toggle with rising-edge detection
- safe STOP transition between command sources

Verified:

- Xbox-compatible controller detected through Pygame/SDL
- left stick axis 0 -> pan
- left stick axis 1 -> tilt
- RB -> mode toggle
- gamepad disconnect -> inactive manual command
- focused control tests: PASS
- full regression: 122 tests PASS

Current modes:

- MANUAL_GAMEPAD
- AUTO_VISION

Immediate next action:

C4A — connect the real Vision tracking command to CommandArbiter.
# CHECKPOINT
Updated: 2026-09-17
No false reacquisition was observed among 8 conclusively evaluated new-ID reacquisition events. One validation event remained uncertain. This dataset is too small to claim a general false-reacquisition rate of zero, but it does not currently justify introducing appearance/ReID complexity.

# CHECKPOINT

Updated: 2026-09-17

## Current branch

feat/vision-p2-evaluation

Known implementation checkpoint:

1d8c369 — feat: complete P2 baseline dataset evaluation

## Current release goal

SYSTEM V1 — COURSE PROJECT

Status: ACTIVE

Primary goal:

Deliver a stable pan/tilt tracking prototype with:

1. MANUAL control from gamepad
2. AUTO tracking from Vision V1
3. safe mode switching
4. PC -> ESP32 command path
5. physical pan/tilt integration
6. live demonstration and report

Do not expand V1 scope unless the core system is already stable.

---

## Vision V1 — Detector Target Tracking

Status: DONE

Pipeline:

Camera
-> YOLO
-> ByteTrack
-> operator target selection
-> TargetManager
-> Smart Reacquire
-> TargetObservation
-> filter
-> tracking controller

Implemented:

- detector target selection
- IDLE / LOCKED / LOST
- LastTargetMemory
- geometry gating
- candidate scoring
- ambiguity rejection
- multi-frame reacquire confirmation
- replay evaluation
- human ground truth
- dataset-level evaluation

Frozen reacquire baseline:

- center gate: 1.0
- scale gate: 2.5
- aspect gate: 1.8
- score margin: 0.10
- confirmation: 2 frames
- timeout: 90 frames

P2 evaluation result:

- 7 scenarios
- 9 annotated new-ID events
- 8 conclusively evaluated
- 8 correct reacquires
- 0 observed false reacquires
- 1 uncertain event

This dataset does not prove a general false-reacquisition rate of zero.

P3 ReID remains deferred.

---

## Control V1

Status: NEXT

V1 command sources:

### MANUAL_GAMEPAD

Operator directly commands pan / tilt.

### AUTO_VISION

Vision tracking controller commands pan / tilt.

Both sources must converge through one mode / command arbitration layer.

At most one command source may control the actuator at a time.

Required transition behavior:

- stop current command
- reset relevant filter/controller state
- switch active mode
- then accept commands from the new source

Future sources are not part of V1:

- HEAD
- HEAD_GAZE
- RADAR_TRACK

---

## ESP32 / actuator

Software path:

Status: CHECKPOINTED

Existing:

- serial receiver
- RCWS1 parsing
- sequence guard
- timeout failsafe
- actuator abstraction
- STEP/DIR pulse engine

Physical integration:

Status: PENDING

Required for V1:

- one-axis verification
- two-axis verification
- direction mapping
- safe stop
- usable velocity limits

---

## Vision future releases

### Vision V2 — Manual ROI

Status: PLANNED

Operator drag-selects an arbitrary ROI and a visual tracker follows it.

This does not replace Vision V1.

### Vision V3 — Hybrid Target Sources

Status: PLANNED

Detector Target + Manual ROI coexist behind a common target representation.

---

## Immediate next action

Implement Control V1:

MANUAL_GAMEPAD + AUTO_VISION mode architecture.

First substage:

create the command-source / mode boundary without changing the
existing Vision tracking algorithm.

Do not add:

- Manual ROI
- ReID
- Head/Gaze
- radar tracking

until System V1 core integration is stable.

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