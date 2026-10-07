# PROJECT SESSION HANDOFF

Updated: 2026-10-07

## 1. Project identity

Project:
Multi-Sensor Stabilized Security Tracking Platform

Repository historical name:
he_thong_RCWS

The active project is a security / observation tracking platform.

Core scope does NOT include:
- firing mechanism
- trigger logic
- ballistic computation
- autonomous engagement

PC owns:
capture -> perception -> tracking -> target management ->
reacquisition -> high-level pan/tilt command -> GUI / telemetry

ESP32 owns:
command reception -> validation -> failsafe ->
real-time actuator timing -> STEP/DIR output

---

## 2. Current working branch

Current development branch:

feat/gui-v1

Vision and Control software baselines were completed before GUI work.

Current GUI work may contain local changes not yet committed,
so always inspect:

git status
git log -1 --oneline

before continuing.

---

## 3. Vision V1 status

Status:
FROZEN / SOFTWARE COMPLETE

Pipeline:

Camera
-> LatestFrameStream
-> YOLO
-> ByteTrack
-> operator target selection
-> TargetManager
-> Smart Reacquire
-> TargetObservation
-> TrackingErrorFilter
-> TrackingController
-> Vision command

Completed:

- YOLO detection
- ByteTrack multi-object tracking
- mouse / GUI target selection
- IDLE / LOCKED / LOST states
- LastTargetMemory
- Smart Reacquire
- geometry gating
- candidate scoring
- ambiguity rejection
- multi-frame confirmation
- timeout handling
- normalized tracking error
- dead zone
- tracking error filtering
- proportional tracking controller
- live telemetry
- failure -> safe output STOP
- replay evaluation
- ground-truth evaluation
- live robustness evaluation
- performance acceptance

Frozen Smart Reacquire baseline:

center distance norm = 1.0
scale ratio          = 2.5
aspect ratio ratio   = 1.8
score margin         = 0.10
confirmation         = 2 frames
lost timeout         = 90 frames

Do not change these values without new evaluation evidence.

Current timeout policy:

short loss
-> LOST
-> Smart Reacquire may recover target

long loss / timeout
-> IDLE
-> operator must currently select target again

---

## 4. Vision performance baseline

Camera:
1280 x 720
30 FPS
DirectShow

Detector:
yolo26n.pt
imgsz 640
confidence 0.25
max_det 100

Observed software performance:

camera FPS              ~30
live pipeline FPS       ~30
offline pipeline p95    20.74 ms
offline pipeline p99    25.51 ms
detector p95            ~15.63 ms
tracker p95             ~0.48 ms

GUI + AI startup currently takes approximately:

6-8 seconds total

After SYSTEM READY the live pipeline is stable.

Camera startup corruption was reduced by discarding initial frames
before showing the first stable frame.

---

## 5. Control V1 status

Status:
SOFTWARE COMPLETE

Control modes:

MANUAL_GAMEPAD
AUTO_VISION

Gamepad:

Xbox-compatible controller
Left Stick X -> Pan
Left Stick Y -> Tilt
RB -> mode toggle

Control pipeline:

Gamepad ----------------------+
                              |
Vision Tracking Command ------+-> CommandArbiter
                                  -> SlewRateLimiter
                                  -> CommandWatchdog
                                  -> NULL / SERIAL output

Safety behavior:

MANUAL disconnect
-> STOP

AUTO entry without valid Vision target
-> rejected

target loss in AUTO
-> inactive / safe tracking command

mode transition
-> safe arbitration

Current default output:

NULL

Physical actuator integration is still pending.

---

## 6. GUI architecture

GUI framework:

PySide6 / Qt

Entry point:

python -m app.gui_main

Main pages:

0 OPERATE
1 DIAGNOSTICS
2 SETUP
3 TUNING

Runtime architecture:

VisionRuntimeWorker
        |
        +-> frame_ready
        |
        +-> snapshot_ready
        |
        +-> notice / error
        |
        v
OperatePage
        |
        +-> RuntimeSnapshot
        |
        +-> snapshot_updated
        +-> runtime_event
                |
                v
        DiagnosticsPage

VisionRuntimeWorker runs outside the Qt UI thread.

Heavy YOLO import is lazy-loaded inside the worker so the GUI can
appear before Torch / Ultralytics initialization.

---

## 7. GUI completed work

G1 GUI shell
DONE

- PySide6 main window
- dark theme
- sidebar navigation
- OPERATE / DIAGNOSTICS / SETUP / TUNING structure

G2A OPERATE layout
DONE

G2B Qt camera preview
DONE

- live camera
- aspect ratio preservation
- safe camera shutdown

G2C GUI coordinate mapping
DONE

- Qt display coordinate -> source frame coordinate
- letterbox handling
- left-click target selection
- right-click target clear

G3A RuntimeSnapshot
DONE

G3B.1 Vision runtime integration
DONE

- camera
- YOLO
- ByteTrack
- TargetManager
- Smart Reacquire
- telemetry
- Qt live overlay

G3B.2 Control integration
DONE

- physical gamepad
- MANUAL_GAMEPAD
- AUTO_VISION
- RB switching
- CommandArbiter
- SlewRateLimiter
- Watchdog
- NULL / SERIAL output abstraction

---

## 8. OPERATE page current state

OPERATE is functionally live.

Displays:

SYSTEM
CONTROL MODE
TARGET
TARGET ID
SEARCH STATE
PAN COMMAND
TILT COMMAND

CAMERA FPS
PIPELINE FPS
FRAME AGE P95
GAMEPAD
OUTPUT

Video displays real:

- detector boxes
- tracker IDs
- selected target
- crosshair

Operator interaction:

left click
-> select tracked object

right click
-> clear target

RB
-> MANUAL / AUTO toggle

---

## 9. DIAGNOSTICS status

G4 — DONE

### G4A
- Diagnostics page connected to RuntimeSnapshot
- live Performance / Target / Control / Output data
- Event Log connected to runtime events

### G4B.1
Performance diagnostics:
- Camera FPS
- Pipeline FPS
- Frame Age / P95
- Frame ID
- Detection count
- Track count
- Inference / P95
- Detector total / P95
- Tracker / P95

Target diagnostics:
- status
- target ID
- search state
- class
- confidence
- bounding box
- center
- missing frames

### G4B.2
Control diagnostics:
- gamepad connection
- raw pan / tilt axes
- manual command
- Vision command
- selected/arbitrated command
- final slew-limited command
- output mode

Verified:
- MANUAL_GAMEPAD selects manual command
- AUTO_VISION selects Vision command
- final command reflects slew-limited selected command

### G4C
Runtime transition events implemented:
- TARGET LOST
- TARGET REACQUIRED
- reacquire with changed track ID
- TARGET TIMEOUT -> IDLE
- TARGET CLEARED remains distinct from timeout

Observed limitation:
rapid tracker loss/reacquisition can create a noisy Event Log.
This is diagnostic evidence of real state transitions, not duplicate
event emission. Event coalescing is deferred to final GUI polish.

Immediate next step:
G5 — SETUP page

## 10. Immediate GUI next step

G4B.2 — Control Diagnostics

Expose separately:

raw gamepad axes
manual command
Vision command
selected/arbitrated command
final slew-limited command

Goal:

make the complete MANUAL / AUTO control path visible in Diagnostics.

Then:

G4C
event-state transition logging / polish

G5
SETUP page

G6
TUNING page

Final GUI polish
and demo acceptance

---

## 11. V1+ expansion requested after teacher review

This is NOT full Vision V2.

It is an extension of System / Vision V1.

Required new behavior:

TRACK
-> target disappears
-> short prediction / COAST
-> Smart Reacquire in current FOV
-> if unsuccessful:
   ACTIVE SEARCH
-> pan/tilt moves toward likely loss direction
-> expanding search region
-> detector/tracker continue running
-> candidate confirmed
-> return to TRACK

If search timeout expires:

-> LOST / IDLE policy

Planned conceptual states:

INACTIVE
COAST
REACQUIRE
SEARCHING
LOST

RuntimeSnapshot already contains SearchState so GUI is prepared for
this extension.

Important:

Smart Reacquire remains responsible for accepting the target.
SearchController only moves the camera/search region.

Do not merge SearchController logic directly into TargetManager.

---

## 12. V2 remains deferred

Do NOT confuse V1+ Active Search with full V2.

Future Vision upgrades include candidates such as:

- Manual ROI tracking
- better motion prediction
- appearance / ReID if evidence justifies it
- BoT-SORT class of tracker upgrades
- camera-motion compensation
- smarter search-sector strategy

These are not required for the current course-project baseline.

---

## 13. Hardware status

PC/ESP32 software boundary exists.

ESP32-side architecture already includes:

serial command reception
protocol validation
sequence/replay guard
timeout failsafe
actuator abstraction
STEP/DIR generation

Pending physical work:

one-axis motor verification
two-axis pan/tilt verification
direction calibration
rate calibration
mechanical soft limits
final hardware integration

Current GUI/software development must not be blocked by missing
pan/tilt hardware.

---

## 14. Current configuration assumptions

configs/default.yaml:

camera source       0
resolution          1280x720
camera FPS          30
backend             dshow

gamepad:
axis 0              pan
axis 1              tilt
button 5            RB mode toggle
dead zone           0.10
invert tilt         true

output:
mode                null

serial:
COM3
115200

detector:
yolo26n.pt
imgsz               640
confidence          0.25
warmup iterations   10

telemetry window:
120 frames

---

## 15. Verification habit

Before every meaningful commit:

uv run ruff check . --fix
uv run ruff format .
uv run ruff check .
uv run pytest -q

Known latest regression baseline during GUI integration:

139 tests passed

Then run:

uv run python -m app.gui_main

and smoke-test the GUI.

---

## 16. Documentation roles

PROJECT_CHARTER.md
= project identity, scope, non-goals and architecture rules.

ARCHITECTURE.md
= PC/ESP32 architecture and current/future pipelines.

DECISIONS.md
= engineering decisions that must not be silently reversed.

ROADMAP.md
= milestones and future direction.

CHECKPOINT.md
= historical checkpoints and verified results.

DEMO_V1.md
= demonstration/preflight procedure.

SESSION_HANDOFF.md
= current operational state and exact resume point.

If old sections conflict with newer sections, use:
PROJECT_CHARTER
+ DECISIONS
+ newest SESSION_HANDOFF / CHECKPOINT
as the authoritative interpretation.

---

## 17. Known documentation cleanup

ROADMAP.md currently contains old duplicated historical sections.

CHECKPOINT.md also contains stale older "Immediate next action" entries.

These do not represent the current state.

Later cleanup should:

- preserve useful historical evidence
- move old material under HISTORY
- keep a single current status block at the top

Do not delete evaluation evidence merely to shorten the files.

---

## 18. Resume instruction for a new ChatGPT conversation

Before changing code, read:

1. docs/PROJECT_CHARTER.md
2. docs/ARCHITECTURE.md
3. docs/DECISIONS.md
4. docs/SESSION_HANDOFF.md
5. docs/CHECKPOINT.md
6. docs/ROADMAP.md

Then inspect:

git status
git branch --show-current
git log -1 --oneline

Current intended resume point:

G4B.2 — Control Diagnostics

Do not restart Vision V1 or redesign the tracking architecture unless
new evidence explicitly requires it.