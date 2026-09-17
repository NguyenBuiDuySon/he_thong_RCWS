
## `docs/ROADMAP.md`

```md
# ROADMAP
update 17/09/2026(
  # ROADMAP

## Release roadmap

### System V1 — Course Project

Status: ACTIVE

Required:

- [x] Vision V1 detector tracking
- [x] Smart Reacquire
- [x] recorded evaluation / ground truth
- [x] PC command output architecture
- [x] ESP32 receiver / failsafe software
- [ ] gamepad manual command source
- [ ] MANUAL / AUTO_VISION mode manager
- [ ] physical pan/tilt verification
- [ ] integrated live test
- [ ] final demo / report stabilization

### Vision V2 — Manual ROI

Status: PLANNED

- arbitrary ROI designation
- visual ROI tracker
- common target adapter
- LOST handling
- live evaluation

### Vision V3 — Hybrid

Status: PLANNED

- Detector Target
- Manual ROI Target
- common target representation
- unified observation/control pipeline


## P0 — Baseline Architecture

Status: DONE

## P1 — Smart Reacquire

Status: DONE

## P2 — Full Tracking Evaluation

Status: DONE

- P2.1 recorded replay — DONE
- P2.2 replay analyzer — DONE
- P2.3 event diagnostics — DONE
- P2.4 human annotation — DONE
- P2.5 ground-truth metrics — DONE
- P2.6 threshold / geometry evaluation — DONE
- P2.7 dataset baseline evaluation — DONE

## P3 — Appearance / ReID

Status: DEFERRED

Current recorded evidence does not justify the added complexity.

## P4 — 2D Motion-State Estimation

Status: FUTURE


)

P2.1 recorded replay              DONE
P2.2 replay analyzer              DONE
P2.3 recovery event diagnostics   DONE
P2.4 human ground truth           DONE
P2.5 GT metrics                   DONE
P2.6 threshold evaluation         ACTIVE
  P2.6A scenario matrix           DONE
  P2.6B threshold CLI             DONE
  P2.6C automated sweep           DONE
  P2.6E ambiguity diagnostics     DONE
  P2.6F geometry diagnostics      ACTIVE

## P1 — Smart Reacquire

Status: DONE

## P2 — Full tracking evaluation

Status: ACTIVE


## P0 — Baseline architecture

Status: DONE

- camera capture;
- YOLO detection;
- ByteTrack;
- mouse target selection;
- IDLE / LOCKED / LOST target state;
- image-space error;
- dead-zone;
- error filtering;
- P tracking controller;
- slew-rate limiting;
- Null / Serial output;
- RCWS1 protocol;
- PC-side watchdog class;
- ESP32 receiver;
- sequence/replay protection;
- ESP32 timeout failsafe;
- actuator abstraction;
- GPTimer STEP pulse engine.

---

## P1 — Smart Reacquire

Status: ACTIVE

### P1.1
RED tests for new-ID reacquisition.

Status: DONE

Current observed test state:

`11 passed, 2 failed`

Expected RED tests:

- reacquire nearby target with new tracker ID;
- prefer correct nearby same-class candidate when another same-class object exists.

### P1.2
LastTargetMemory.

Store:

- class;
- last track ID;
- bbox;
- center;
- width;
- height;
- frame/time last seen.

### P1.3
Spatial + geometry gate.

Use:

- same class;
- center distance;
- bbox scale;
- aspect ratio;
- reacquire time window.

### P1.4
Candidate scoring.

Combine:

- motion;
- geometry;
- temporal confidence.

### P1.5
Ambiguity rejection.

If top candidates are too similar, remain LOST.

### P1.6
Confirmation hysteresis.

Require consistent candidate evidence across multiple frames before changing selected ID.

---

## P2 — Full tracking evaluation

- recorded full-pipeline replay;
- CSV / JSON diagnostics;
- ID switch count;
- LOST duration;
- target retention;
- reacquire success rate;
- false reacquire rate;
- time to reacquire;
- ambiguous-event count;
- FPS / latency.

Reuse and extend:

- `tools/record_clip.py`;
- `tools/replay_clip.py`;
- `tools/benchmark_detector.py`.

---

## P3 — Appearance / ReID

Only after P1/P2 measurements justify it.

- target crop / appearance descriptor;
- candidate embedding;
- similarity score;
- combine appearance with motion/geometry;
- no face-recognition dependency required.

---

## P4 — 2D motion-state estimation

Start with:

`[x, y, vx, vy]`

Prefer constant-velocity estimator / Kalman baseline.

Add acceleration only after recorded residuals show benefit.

Future:

`[x, y, vx, vy, ax, ay]`

---

## P5 — Predictive camera tracking

Estimate total system latency.

Predict:

`P(t + dt)`

Use predicted target position instead of only current target position.

Goal:

reduce camera trailing during target motion.

---

## P6 — Camera calibration and angular tracking

- camera intrinsics;
- pixel -> line of sight;
- normalized error -> azimuth/elevation error;
- resolution-independent control.

---

## P7 — Real pan/tilt actuator integration

Status: BLOCKED BY HARDWARE

Current postponed step:

physical STEP / DIR / ENABLE verification with DM542 and real motor.

Then:

- steps/rev;
- microstep;
- gear ratio;
- direction;
- velocity mapping;
- acceleration;
- soft limits;
- homing.

---

## P8 — Encoder closed loop

- actual pan angle;
- actual tilt angle;
- zero/calibration;
- position feedback;
- missed-motion detection.

---

## P9 — IMU stabilization

- angular-rate measurement;
- orientation estimate;
- distinguish target motion from platform motion;
- closed-loop stabilization.

---

## P10 — Range / depth

Add one valid range source.

Candidates:

- TOF;
- depth camera;
- stereo;
- radar.

---

## P11 — 3D state estimation

After valid range is available:

`[x, y, z, vx, vy, vz]`

Acceleration only if measurements justify it.

---

## P12 — Multi-sensor fusion

Potential sources:

- RGB;
- thermal;
- radar;
- depth/range;
- encoder;
- IMU.

---

## P13 — HMI / field diagnostics

- web or desktop operator dashboard;
- recording;
- telemetry;
- target state;
- sensor health;
- manual pan/tilt mode;
- calibration tools.

---

## P14 — Reliability / fault injection

Test failures such as:

- camera loss;
- detector stall;
- serial loss;
- stale commands;
- sensor timeout;
- encoder mismatch;
- IMU failure;
- actuator fault;
- process crash.

Fail to a safe stationary state where appropriate.