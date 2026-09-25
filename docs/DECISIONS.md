# DECISIONS

This file records architectural decisions that should not be casually reversed.

---
Update: 2026-09-25
## D021 — Control V1 software baseline frozen

Decision:

Control V1 software is frozen after successful MANUAL_GAMEPAD /
AUTO_VISION integration and acceptance testing.

Validated policy:

- MANUAL_GAMEPAD owns output in manual mode
- AUTO_VISION owns output in auto mode
- mode changes insert an inactive STOP command
- manual gamepad disconnect stops output
- auto mode may continue after gamepad disconnect
- loss of a valid Vision target stops auto output
- AUTO_VISION entry requires an active Vision command

Further changes to the control baseline require:

- reproduced software failure, or
- physical hardware evidence.

Update: 2026-09-20

## D020 — Control V1 mode switching

Decision:

System V1 uses RB on the gamepad to toggle:

MANUAL_GAMEPAD <-> AUTO_VISION

The button is processed using rising-edge detection so one physical
press causes exactly one mode transition.

Every successful mode change inserts an inactive STOP command before
the newly selected source becomes active.


update 17/09/2026{

## D017 — System V1 scope

Decision:

System V1 for the course project contains two command modes:

1. MANUAL_GAMEPAD
2. AUTO_VISION

Vision V1 is the existing detector-based pipeline:

YOLO -> ByteTrack -> TargetManager -> Smart Reacquire

Manual ROI, Head/Gaze and radar tracking are not required for
System V1 completion.

Reason:

Prefer a small number of fully integrated and validated functions
over many partially implemented modes before the course deadline.

---

## D018 — Separate target source from command source

Decision:

Target acquisition/tracking and actuator command source are separate concepts.

Examples:

- YOLO / Manual ROI are target sources
- Gamepad is a direct manual command source
- Head/Gaze is an operator pointing command source
- radar may later become a sensor-driven tracking source

All actuator command sources must pass through a single arbitration
boundary before the output / watchdog / ESP32 path.

---

## D019 — Vision version roadmap

Decision:

Vision development is versioned as:

- Vision V1: Detector Target
- Vision V2: Manual ROI
- Vision V3: Detector + Manual ROI hybrid

Manual ROI does not replace the validated Detector Target pipeline.

The Vision V2/V3 design may be implemented after System V1 is stable.


}
## D001 — Project scope

Decision:

The project is a **Multi-Sensor Stabilized Security Tracking Platform**.

It is not defined as a complete RCWS.

No firing mechanism, trigger logic or ballistic fire-control belongs to the core architecture.

---

## D002 — Keep current Vision architecture

Decision:

Keep:

`Camera -> YOLO -> ByteTrack -> TargetManager -> control`

Reason:

Real tests show the current detection and ordinary tracking baseline is already stable enough to continue from it.

ORCAS does not replace this stack.

---

## D003 — ORCAS usage

Decision:

Use ORCAS as a benchmark for:

- mechanics;
- electrical integration;
- modular sensor packaging;
- calibration;
- subsystem bring-up;
- documentation;
- HMI concepts.

Do not clone its entire design.

---

## D004 — PC / MCU separation

Decision:

PC handles perception and high-level control.

ESP32 handles deterministic hardware timing and failsafe behavior.

Reason:

Keeps AI and real-time motor execution independently testable.

---

## D005 — Smart Reacquire strategy

Decision:

Do not reacquire merely because another track has the same class.

Reacquisition should evolve through:

1. memory;
2. spatial / geometry gate;
3. motion scoring;
4. ambiguity rejection;
5. multi-frame confirmation;
6. optional appearance / ReID.

Priority:

False reacquisition is worse than remaining LOST temporarily.

---

## D006 — ReID timing

Decision:

Do not introduce ReID before basic Smart Reacquire is evaluated on recorded data.

Reason:

Avoid unnecessary complexity and maintain measurable improvements.

---

## D007 — Prediction terminology

Decision:

Future-position prediction is for **camera tracking / latency compensation**.

It predicts where the tracked object will be when the camera responds.

---

## D008 — 3D requirement

Decision:

Do not claim metric 3D tracking from monocular RGB bbox data alone.

Metric 3D requires real range/depth information.

---

## D009 — Physical motor stage

Decision:

Do not continue motor calibration until physical DM542 / motor hardware is available.

Current firmware remains checkpointed until then.

---

## D010 — ORCAS mechanics

Decision:

Study ORCAS pan mechanics, belt reduction, modular sensor head and calibration workflow before final mechanical design.

Do not automatically copy its motor driver or printed structure.

---

## D011 — Mechanical material direction

Tentative direction:

- load-bearing pan/tilt structure: metal / bearing / shaft where practical;
- 3D printed parts: sensor housing, brackets, covers and low-load geometry.

This remains an engineering choice to validate against final mass and budget.

---

## D012 — Development method

Decision:

Implement one small stage at a time.

For algorithm changes:

`test -> RED -> minimal implementation -> GREEN -> regression test`

For hardware:

`power -> MCU -> driver -> one axis -> second axis -> sensors -> full integration`

## D013 — Reacquire baseline

Keep the current baseline while P2 is active:

- score margin: 0.10
- confirmation: 2 frames
- center gate: 1.0
- scale gate: 2.5
- aspect gate: 1.8

Do not tune from intuition. Change one parameter only when recorded diagnostics justify it.

## D014 — Tune / validation separation

Thresholds are selected only from `tune` scenarios.

Validation scenarios remain held out until a candidate configuration has been selected.

Do not use validation results to repeatedly retune thresholds.

## D015 — Generated evaluation artifacts

Replay CSV, analyzer JSON and sweep outputs are reproducible runtime artifacts and are not committed.

Scenario definitions and human ground-truth annotations are committed.

## D016 — ReID remains evidence-gated

P3 ReID stays deferred until recorded validation demonstrates false reacquisition that geometry + temporal confirmation cannot control acceptably.