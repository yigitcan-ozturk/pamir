# Holdout H3 Blind Incident Register

Status: source-labelled; PAMIR not scored.

| Case | PX4 issue | Flight Review UUID | Label |
|---|---:|---|---|
| H3-001 | #23823 | f2a737ec-4436-4806-92e6-f8fc320d4b4c | incident |
| H3-002 | #15289 | 44fcd17a-694d-431e-a02f-74c51f8d3cda | incident |
| H3-003 | #14981 | 116b78e1-7732-4e6e-acf8-88e640d8cdfc | incident |
| H3-004 | #15155 | 379ea7f6-38e4-40ed-829b-6e333d91b053 | incident |
| H3-005 | #22465 | e79ca622-a5d7-4b76-9d08-26e8b75273e6 | incident |
| H3-006 | #12902 | 6431208f-5a4f-4f35-96bd-c2182f644cba | incident |
| H3-007 | #20914 | b3cfc2fb-83ef-431a-890c-e9b905b5fb6f | incident |

Source basis, locked before PAMIR:
- H3-001: real VTOL flight; reporter says crash occurred after offboard velocity control then Return.
- H3-002: mission flight; reporter says motors stopped and octocopter fell from 120 m.
- H3-003: reporter says stale mission waypoint behaviour caused ground crash.
- H3-004: real Convergence VTOL flight; reporter says control problem ended in crash.
- H3-005: unexpected yaw rotations, building strike / near crash; material in-flight control anomaly.
- H3-006: severe RTL landing wobble followed by flip/crash.
- H3-007: reporter-provided flight occurrence of severe estimator anomaly.

All seven UUIDs were absent from the Corpus v1 manifest at pre-registration check. Acquisition must repeat UUID/SHA leakage checks. Unavailable sources are quarantined. PAMIR output cannot alter labels.
