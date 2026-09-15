# DECISIONS

This file records architectural decisions that should not be casually reversed.

---

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