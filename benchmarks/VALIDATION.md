# PAMIR v0.1 forensic validation

Final validation head: `18c0553affe2a508f686d2285770bb4172b8b859` (PR #2).
GitHub Actions benchmark run: `34664700248`.

## Result

**PASS — merge-ready validation gate.**

The hard benchmark uses five directly accessible public PX4 incident ULogs and three public healthy/control ULogs. Every required binary is downloaded in CI and SHA-256 checked. The legacy Flight Review corpus remains optional because `logs.px4.io` returns HTTP 403 to hosted runners; it is not used to certify v0.1.

The final workflow printed:

```text
PAMIR v0.1 REPRODUCIBLE VALIDATION GATE PASSED
```

The generated `summary.json` reports:

```text
v0_1_complete: true
validation_passed: true
validation_errors: []
required_incident_count: 5
required_control_count: 3
```

## Required corpus result

| Public ULog | Kind | Samples | Signals | Root | Confidence | Timestamp causal errors |
| --- | --- | ---: | ---: | --- | ---: | --- |
| github-indoor-crash-2025 | incident | 97,104 | 367 | `estimator_status.output_tracking_error[0]` | 0.583 | none |
| follow-me-crash-2020 | incident | 199,152 | 306 | `vehicle_rates_setpoint.pitch` | 0.999 | none |
| position-mode-crash-2023 | incident | 236,478 | 609 | `estimator_status[2].output_tracking_error[0]` | 0.806 | none |
| altitude-hold-crash-2022 | incident | 165,643 | 434 | `estimator_status.output_tracking_error[0]` | 0.768 | none |
| uncontrolled-yaw-incident-2022 | incident | 513,241 | 660 | `estimator_status[2].output_tracking_error[1]` | 0.535 | none |
| github-indoor-control-2025 | control | 427,824 | 350 | none | 0.000 | none |
| follow-me-control-2020 | control | 1,287,057 | 306 | none | 0.000 | none |
| stabilized-control-2022 | control | 864,653 | 434 | none | 0.000 | none |

The pinned PX4/pyulog real binary parser sample also parses and completes the pipeline without a material failure root.

## What is actually enforced

- required public ULogs must download and pass SHA-256 validation;
- ULog instances remain isolated and non-finite telemetry is rejected;
- evidence windows must contain the exact reported observation;
- confidence must be finite and bounded;
- failure-chain timestamps must be monotonic;
- `likely_caused` requires a strictly earlier parent inside the causal window;
- incident roots must have required downstream telemetry families after the root timestamp;
- healthy/control ULogs must produce no material root;
- five incidents and three controls are hard CI gates;
- the unit/regression suite and benchmark workflow must both pass.

## False-positive hardening

Normal battery demand/SOC depletion, estimator state/covariance/reset fields, ordinary actuator commands, healthy estimator-accuracy changes, and sub-threshold estimator test ratios are not accepted as failure roots. Vibration metrics remain evidence-only. Control setpoints remain excluded from the generic detector; a control-family root is permitted only for a narrow multi-axis rate-command discontinuity followed by attitude and motion anomalies.

During hardening, PX4 issue #25762 was deliberately removed from the incident corpus after its discussion established that a motor command reaching zero could be intended yaw-control behavior rather than a fault. PAMIR was not tuned to force that case to pass.

## Interpretation limits

`confidence` is an uncalibrated anomaly-strength heuristic, not a probability of causation. `likely_caused` is a conservative temporal/signal-family relationship, not mathematical proof of causality. v0.1 is an incident-reconstruction and evidence-ordering engine; calibrated causal inference remains future work.

## External clean-log validation batch - 2026-09-14

Frozen PAMIR v0.1.0 was evaluated against three additional external PX4 ULogs as a false-positive check. These logs are not part of the required v0.1 CI corpus and do not change the frozen benchmark gate.

| Case | Result | Samples | Signals | Material root |
| --- | --- | ---: | ---: | --- |
| #010 | PASS | n/a | n/a | none |
| #011 | PASS | n/a | n/a | none |
| #012 | PASS | 91,052 | 475 | none |

Case #012 source: `cb7e343b-1db2-407a-8714-647a1acec12d.ulg`.

PAMIR v0.1.0 reported:

```text
raw_deviation_count: 35
root_event: null
first_deviation: null
failure_chain: []
conclusion: no_deviation_detected
```

Batch result: **3 / 3 CLEAN PASS**.

These results are supplemental external validation evidence only. They do not modify the frozen v0.1 detection policy, thresholds, required corpus, or CI pass/fail semantics.
