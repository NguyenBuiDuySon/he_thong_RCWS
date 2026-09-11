# PROJECT CHARTER

## 1. Project identity

**Working name:** Multi-Sensor Stabilized Security Tracking Platform

The repository keeps its historical name `he_thong_RCWS`, but the active project scope is a **security / observation tracking platform**. The project is not defined as a complete RCWS and does not include a weapon or firing subsystem.

## 2. Product goal

Build a modular pan/tilt observation platform that can:

- detect and track moving objects from camera input;
- let an operator select a target to follow;
- preserve target identity through short occlusion and tracker ID changes using intelligent reacquisition;
- estimate target motion state;
- predict short-horizon future target position to reduce tracking lag;
- drive a real pan/tilt gimbal through a PC-to-ESP32 control boundary;
- add encoder and IMU feedback for closed-loop stabilization;
- later fuse RGB, thermal, range/depth and radar information when hardware becomes available;
- provide telemetry, diagnostics, recording and an operator HMI.

## 3. Explicit non-goals

The core project does **not** include:

- a firing mechanism;
- trigger or fire-control logic;
- ballistic or projectile-intercept computation;
- autonomous engagement logic;
- any dependency where target tracking is coupled to a firing action.

Optional demo payloads must remain isolated from the tracking core and must not change the architecture or safety assumptions of the security platform.

## 4. Fixed architecture principles

### 4.1 PC owns high-level perception and tracking

The PC side owns:

`capture -> detection -> tracking -> target management -> reacquisition -> state estimation -> prediction -> pan/tilt command generation`

The PC should not generate hardware-timed step pulses directly.

### 4.2 ESP32 owns real-time actuator execution

The ESP32 side owns:

`command reception -> validation -> sequence guard -> timeout/failsafe -> actuator abstraction -> real-time motor pulse generation`

The MCU must remain able to stop motion safely even if the PC application stalls or the serial link disappears.

### 4.3 Tracking intelligence stays independent from actuator hardware

Vision code must not know DM542 GPIO details, STEP pulse timing, microstepping or motor wiring. It outputs normalized or future angular motion commands through a stable command interface.

### 4.4 Sensor and actuator layers remain modular

Future RGB, thermal, TOF/range, radar, encoder and IMU integrations should enter through explicit modules instead of being hard-coded into `main.py`.

### 4.5 Evidence before complexity

New algorithms are introduced only when recorded tests or hardware measurements show a need.

Examples:

- do not add ReID before spatial/geometry reacquisition is measured;
- do not add acceleration state before constant-velocity estimation is measured;
- do not claim metric 3D position from a monocular RGB bounding box without a valid depth/range source.

## 5. ORCAS reference policy

ORCAS is a **mechanical/electrical/integration benchmark**, not a replacement for the current Vision architecture.

What is worth learning from ORCAS:

- pan/tilt mechanical packaging and belt-reduction ideas;
- modular sensor/observation head design;
- subsystem-by-subsystem electrical bring-up;
- angle feedback and calibration workflow;
- wiring, connectors, BOM and assembly documentation;
- practical HMI/integration workflow.

What must **not** happen:

- replacing the current YOLO -> ByteTrack -> TargetManager architecture merely to match ORCAS;
- importing ORCAS payload/fire-control subsystems into the core project;
- changing project direction silently because a reference system uses a different design.

## 6. Change-control rule

Any change to one of the following is an **architecture change** and must be stated explicitly before implementation:

- product definition;
- PC/ESP32 responsibility boundary;
- target tracking/reacquisition pipeline;
- major sensor-fusion model;
- actuator control model;
- project scope or non-goals.

Do not silently change these while implementing a small feature.

## 7. Development style

Use small, testable stages:

`one small change -> run focused tests -> inspect behavior -> then continue`

Avoid broad rewrites while a subsystem is still being validated.

## 8. Resume rule for future sessions

Before substantial project work, read in this order:

1. `docs/PROJECT_CHARTER.md`
2. `docs/ARCHITECTURE.md`
3. `docs/ROADMAP.md`
4. `docs/DECISIONS.md`
5. `docs/CHECKPOINT.md`

`PROJECT_CHARTER.md` defines what the project is.

`CHECKPOINT.md` defines where work should resume.