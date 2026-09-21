# Batch A — Candidate Inventory

Status: **candidate collection / pre-replay**

This inventory is intentionally recorded before interpreting PAMIR output. Inclusion here does not mean acceptance into the final corpus.

| Case | Public source | Narrative label | Family | Vehicle / PX4 | Status |
|---|---|---|---|---|---|
| FV-A001 | PX4/PX4-Autopilot #27013 | altitude spikes / near-crash | sensor_anomaly / attitude_control | Fixed wing / v1.17 RC2 | candidate |
| FV-A002 | PX4/PX4-Autopilot #9260 | mission-end position-hold crash | ekf_gps / attitude_control | Multicopter / v1.7.4 beta | candidate |
| FV-A003 | PX4/PX4-Autopilot #21828 | GPS-loss crash narrative | ekf_gps / failsafe | Multicopter | candidate |
| FV-A004 | PX4/PX4-Autopilot #24188 release-flight archive | successful release flight | healthy_control | Quadcopter / v1.16 prerelease | candidate |
| FV-A005 | PX4/PX4-Autopilot #24188 release-flight archive | successful release flight | healthy_control | Fixed wing / v1.16 RC | candidate |
| FV-A006 | PX4/PX4-Autopilot #24188 release-flight archive | no-GPS reported flight | ekf_gps | Quadcopter / v1.16 RC1 | candidate |
| FV-A007 | PX4/PX4-Autopilot #26271 release-flight archive | completed release test | healthy_control | Multicopter / v1.17 prerelease | candidate |
| FV-A008 | PX4/PX4-Autopilot #26271 release-flight archive | crash-log group | unknown / triage | Multicopter / v1.17 prerelease | candidate |

## Batch A gates

A candidate is not promoted to `accepted` until all of the following are captured:

1. direct original ULog download is retrievable;
2. original filename is recorded;
3. SHA256 is computed from the retrieved binary;
4. source provenance and public-use licensing basis are recorded;
5. narrative classification is independent of PAMIR output;
6. telemetry is sufficient for the declared validation question;
7. predeclared acceptance criteria are satisfied.

## Exclusions

- SITL-only or synthetic failure-injection logs are excluded from Field Validation Corpus v1.
- Existing frozen v0.1 benchmark cases are not reused as new field-validation evidence.
- Ambiguous cases remain `unknown` or are quarantined; they are not forced into incident/control classes.
- No PAMIR root result may be used to manufacture a source label.

## Next action

Resolve the direct ULog objects for these candidates, compute SHA256, pin provenance, and promote only qualifying cases into the immutable Batch A accepted manifest. Then replay the frozen PAMIR v0.1.0 pipeline without modifying baseline policy or thresholds.
