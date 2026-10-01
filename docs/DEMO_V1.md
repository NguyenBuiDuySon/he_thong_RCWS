# SYSTEM V1 DEMO

## Purpose

Demonstrate the current System V1 software baseline:

- live camera perception
- YOLO detection
- ByteTrack tracking
- operator target selection
- Smart Reacquire
- MANUAL_GAMEPAD control
- AUTO_VISION control
- safe mode switching
- Vision failure handling
- live telemetry

Physical actuator integration is not part of this software-only demo
while the pan/tilt hardware is pending.

---

## Preflight

Before starting:

- camera connected
- gamepad connected
- `configs/default.yaml` restored to live camera configuration
- output mode is `null`
- detector model available
- no recording / benchmark process is using the camera

Verification:

```powershell
uv run ruff check .
uv run pytest -q