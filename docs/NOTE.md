1. Current PC vision pipeline
Camera
  ↓
LatestFrameStream
  ↓
YoloDetector
  ↓
ByteTrackAdapter
  ↓
mouse target selection
  ↓
TargetManager
  ↓
TargetObservation
  ↓
TrackingErrorFilter
  ↓
TrackingController
  ↓
CommandSlewRateLimiter
  ↓
CommandWatchdog
  ↓
Null / Serial output

2. Current ESP32 pipeline
Serial input
   ↓
protocol parser
   ↓
validation
   ↓
sequence / replay guard
   ↓
CommandState
   ↓
FreeRTOS handoff
   ↓
ActuatorOutput
   ↓
StepDirActuatorOutput
   ↓
StepPulseEngine / GPTimer
   ↓
STEP / DIR / ENABLE

3. Responsibility boundary
PC
Owns:
    capture;
    detection;
    tracking;
    target identity;
    reacquisition;
    state estimation;
    prediction;
    high-level pan/tilt command generation;
    HMI and telemetry.

ESP32
Owns:
    command reception;
    protocol validation;
    timeout/failsafe;
    real-time motor timing;
    hardware output;
    future encoder/IMU inner-loop handling.

4. Future module layout
Preferred future structure:
    app/
    ├── capture/
    ├── detection/
    ├── tracking/
    ├── targeting/
    ├── estimation/
    ├── prediction/
    ├── sensors/
    ├── control/
    ├── output/
    ├── hud/
    └── telemetry/
5. Stabilization architecture
Future:
    Vision target LOS
        ↓
    outer loop
    20–30 Hz
        ↓
    desired angle / rate
        ↓
    ESP32
        ↓
    inner stabilization loop
        ↙       ↘
    encoder     IMU
        ↘       ↙
        actuator
6. 3D rule
RGB monocular tracking provides image-space position and angular direction after calibration.
Metric 3D state requires a valid additional source such as:
  stereo;
  depth camera;
  TOF/range sensor;
  radar.