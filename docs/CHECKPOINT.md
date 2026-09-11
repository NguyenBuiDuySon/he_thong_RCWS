# CHECKPOINT

Last updated: 2026-09-11

## Project

Multi-Sensor Stabilized Security Tracking Platform

## Current active phase

**P1 — Smart Reacquire**

Current substage:

**P1.2 / V12.2B — LastTargetMemory**

---

## Vision status

DONE:

- Camera capture;
- LatestFrameStream;
- YOLO detector;
- ByteTrack;
- target click selection;
- TargetManager;
- IDLE / LOCKED / LOST;
- target observation;
- normalized tracking error;
- dead-zone;
- TrackingErrorFilter;
- P tracking controller;
- slew-rate limiter;
- command output abstraction;
- Null output;
- Serial output;
- RCWS1 protocol;
- HUD / telemetry;
- detector benchmarking tools.

Baseline real-video tests:

- static tracking: PASS;
- normal movement: PASS;
- substantial scale change: generally stable;
- same-ID tracking: stable in ordinary motion;
- tracker may assign a new ID after strong occlusion / leaving frame;
- TargetManager currently cannot automatically reacquire a new ID.

Important observed failure pattern:

`ID 0 LOCKED -> LOST -> same object returns as ID 4 -> TargetManager remains LOST`

Multi-person test confirmed that same-class reacquisition cannot simply choose any visible `person`.

---

## Smart Reacquire test status

Local `tests/test_target_manager.py` has two new expected-failure tests:

1. new nearby ID should be reacquired;
2. when multiple same-class candidates exist, correct nearby candidate should be preferred.

Observed result:

`11 passed, 2 failed`

This is the expected RED state.

Do not modify the test expectation to make the test pass.

Next implementation step:

create target memory / last-known geometry first.

Do not add ReID yet.

---

## ESP32 status

Branch:

`feat/esp32-actuator-output`

Latest known cleanup commit:

`b7142350f760facba72b98b566bddc7dbc5c58ec`

Completed:

- ESP-IDF receiver;
- RCWS1 parsing;
- sequence guard;
- stale/replay rejection;
- timeout failsafe;
- CommandState;
- FreeRTOS handoff;
- ActuatorOutput abstraction;
- StepDirActuatorOutput;
- StepPulseEngine using GPTimer;
- software smoke tests for PAN/TILT directions and STOP.

Pending:

**physical STEP / DIR / ENABLE verification**

Reason:

hardware not currently available.

Do not continue real motor mapping until physical verification is possible.

---

## Hardware direction

Current available / planned core:

- ESP32-S3;
- DM542;
- NEMA17;
- pan/tilt mechanics;
- RGB camera.

Future:

- absolute encoder;
- IMU;
- range/depth;
- radar;
- thermal camera.

ORCAS is the primary current reference for mechanical/electrical integration methodology.

---

## Immediate next action

Continue only:

**P1.2 — LastTargetMemory**

Goal:

store last known target geometry while LOCKED.

At this substage:

- do not score candidates;
- do not switch selected ID;
- do not add ReID;
- do not refactor unrelated modules.

After focused tests are GREEN:

continue to P1.3 spatial/geometry gating.