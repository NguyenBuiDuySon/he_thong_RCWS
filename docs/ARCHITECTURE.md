# ARCHITECTURE

## 1. Target architecture

```text
RGB Camera ──────┐
Thermal ─────────┤
Radar / Depth ───┤
                 ▼
        SENSOR ACQUISITION
                 │
                 ▼
        DETECTION / PERCEPTION
                 │
                 ▼
          MULTI-OBJECT TRACKER
                 │
                 ▼
            TARGET MANAGER
        ┌────────┴────────┐
        │                 │
      LOCKED            LOST
                          │
                          ▼
                 SMART REACQUISITION
                 motion + geometry
                 appearance + time
                          │
                          ▼
                    TARGET MEMORY
                          │
                          ▼
                  STATE ESTIMATION
            position / velocity / accel
                          │
                          ▼
                 FUTURE POSITION
                     P(t + dt)
                          │
                          ▼
              PREDICTIVE PAN/TILT
                          │
                          ▼
                 GIMBAL CONTROLLER
                          │
                     PC command
                          ▼
                       ESP32
                          │
              real-time actuator layer
                          │
                          ▼
                     PAN / TILT
                          ▲
                          │
                 Encoder + IMU