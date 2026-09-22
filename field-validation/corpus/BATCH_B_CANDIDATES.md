# Batch B — acquisition candidates

Selected from Flight Review discovery run #90. This is an acquisition shortlist, not an accepted corpus label. PAMIR output must not be used to manufacture ground truth.

| Case | Flight Review UUID | Independent narrative basis | Provisional class | Next gate |
|---|---|---|---|---|
| FV-B001 | 60f0a65f-fea3-46cc-b8db-23ac20adb24c | Board-support validation flight explicitly reports takeoff, stable flight, landing and disarm | healthy_control candidate | retrieve ULog, SHA256, telemetry sufficiency, deterministic replay |
| FV-B002 | ef5d183f-b402-4f59-9f45-d83aed560f08 | Description/feedback explicitly reports ROS error setpoint | unknown / attitude-control candidate | retrieve ULog, SHA256, establish whether real flight and evidence sufficiency |
| FV-B003 | 92927d73-ab85-4f89-ba1a-d27d8f0f16c9 | Flight-plan metadata describes takeoff/landing mission | unknown / control candidate | retrieve ULog, SHA256, verify real-flight telemetry before any label |
| FV-B004 | 05331af8-4ebb-4f11-8f00-2ab84fa4891a | Flight-plan metadata describes C-turn trajectory | unknown / control candidate | retrieve ULog, SHA256, verify real-flight telemetry before any label |

## Excluded from Batch B

Run #90 also returned numerous low-information QGroundControl/bench-test records and repeated plan-name-only records. They are not accepted evidence and are not promoted merely to increase corpus size.

## Batch B rule

A case moves from this shortlist to the corpus manifest only after the original public ULog is retrievable, SHA256 is pinned, provenance/licensing is recorded, and the independent classification/evidence question is defensible before interpreting PAMIR output.
