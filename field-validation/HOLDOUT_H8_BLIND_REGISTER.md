# Holdout H8 Blind Candidate Register

Status: source-labelled candidates; PAMIR not scored. All UUIDs were checked absent from every Corpus v1 manifest UUID before registration.

| Case | Flight Review UUID | Label | Public PX4 source narrative |
|---|---|---|---|
| H8-001 | a45dca4b-9975-43de-9499-cee5690c984a | incident | RC signal-loss report: actuators remained at last commanded position under configured failsafe behavior. |
| H8-002 | 00d1f070-bc99-4a03-8690-1ac7225a28ee | incident | Follow-me mode setpoint behavior reported to cause vehicle fly-off. |
| H8-003 | 48cd1d4d-2601-454a-a451-92a744e8ceb6 | incident | Unexpected altitude change in Position mode despite reportedly healthy GPS/barometers. |
| H8-004 | 19d5eeee-54f5-461d-990e-f31572208cb4 | incident | Airspeed-selector report documents invalidation/failure behavior in flight data. |
| H8-005 | a3002514-92a7-4156-acf5-420406a5567c | incident | Second real-flight log from the airspeed-selector invalidation report. |
| H8-006 | 7dfd87cc-c486-49c3-8761-b666fdd8f33b | incident | Fixed-wing Offboard report: pitch/throttle setpoints not updated as commanded. |
| H8-007 | 5a4d0d01-8fd6-456a-8522-9a539464bf0f | incident | Second flight log linked to fixed-wing Offboard setpoint failure report. |
| H8-008 | 5cf34fa0-2d32-4668-9abf-8ad93a8a1406 | incident | EKF2 estimator divergence reported after brief sensor/data freezes. |
| H8-009 | 8e2431d5-c942-4196-9ed9-327741afb76c | incident | Takeoff/land without GPS reported not to hold position. |
| H8-010 | ca0d60d8-6dc6-4215-86f4-32fa2ad18f71 | incident | Random thrust reported with no thrust input when optical flow enabled without data. |

Labels are locked from source evidence before PAMIR execution. Acquisition failure or telemetry insufficiency means quarantine; no gate weakening and no post-outcome relabelling.
