# LOONA Communication Protocol (Brain <-> Muscle)
Transport: Persistent WebSocket connection

## 1. Brain -> Muscle: Velocity Command
Ipinapadala nang tuloy-tuloy sa fixed rate (10-20 Hz). Nagsisilbi itong heartbeat signal; kapag walang natanggap ang ESP32 sa loob ng 1000ms, awtomatikong papatayin ng firmware ang mga motor.

{
  "cmd": "VEL",
  "v": 0.5,
  "w": -0.2
}
* v: linear velocity, -1.0 to 1.0 (negative = paatras)
* w: angular velocity, -1.0 to 1.0 (negative = liko pakaliwa, positive = liko pakanan)

## 2. Muscle -> Brain: Telemetry
Pabalik na report mula sa ESP32, ipinapadala sa parehong fixed rate.

{
  "telemetry": {
    "tof_mm": 124,
    "battery_v": 11.4,
    "reflex_active": false,
    "actual_v": 0.48,
    "actual_w": -0.19
  }
}
* tof_mm: raw integer distance (millimeters) direktang mula sa VL53L0X sensor.
* tof_cm: distansya mula sa local ToF/IR sensor (millimeters/centimeters).
* battery_v: kasalukuyang boltahe ng 18650 pack para sa brownout monitoring.
* reflex_active: `true` kapag nag-trigger ang ESP32 local obstacle reflex (override). Dapat huminto ang Brain sa pagpapadala ng bagong VEL commands hanggang bumalik ito sa `false`.
* actual_v / actual_w: aktwal na output ng PID loop para ma-monitor ng Brain ang motor drift.