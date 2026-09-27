# Harsha raw ULog — first independent extraction (2026-09-28)

Source: user-supplied `452d7328-c961-49d4-b608-33ee82d99133(1).ulg` (67 MB); Flight Review ID 452d7328-c961-49d4-b608-33ee82d99133. Extraction used a minimal custom ULog message/format parser because pyulog could not be installed in the analysis environment. These are exploratory measurements; independently reproduce with pyulog before formal external validation.

## Confirmed from parsed records
- Log coverage for `estimator_innovation_test_ratios`: instance 1 345.741–512.740 s (227 samples); instance 0 345.746–512.740 s (226 samples).
- Both instances have `mag_field[2] > 1` at the **first recorded sample**: instance 1 at 345.741 s (9.894); instance 0 at 345.746 s (9.882). Thus anomaly onset is **left-censored** by recording/sampling, not established at 345.74 s.
- Instance 1 `mag_field[0] > 1` first recorded at 348.243 s (1.159); instance 0 at 348.243 s (1.202).
- Prior to 440 s, instance 1: 113/113 recorded `mag_field[2]` samples >1, 84/113 `mag_field[0]` >1. Instance 0: 112/112 `mag_field[2]` >1, 90/112 `mag_field[0]` >1. These are sampled counts, **not** continuous-time duration estimates.
- Estimator selector: instance 1 selected at first selector sample 345.032 s; switches to instance 0 at 465.712 s, then back to instance 1 at 470.089 s. First identified attitude divergence supplied at 462.123 s precedes both recorded switches.
- `estimator_status_flags.cs_mag_field_disturbed` true in both instances at samples around 385.014, 425.1, 436.11 s; these are sampled flags, not necessarily complete onset/duration.
- `estimator_status.filter_fault_flags` first nonzero 1024 at 464.883 s (instance 0) and 464.886 s (instance 1); firmware-specific bit interpretation pending.
- `failure_detector_status.fd_roll` first true at 467.387741 s, consistent with user-reported 467.388 s.

## Preliminary interpretation
Persistent pre-event magnetometer test-ratio exceedance is observed; this alone does not identify a fault onset or prove that magnetometer behavior caused attitude divergence. Candidate H1 (magnetometer -> selected estimator -> controller) remains UNRESOLVED. The first recorded estimator switch occurs after the supplied divergence, so the observed switch at 465.712 s cannot be assumed to initiate the earlier 462.123 s event; H2 remains UNRESOLVED as a broader hypothesis. Investigate other estimator signals, actuator/attitude dynamics, data gaps and firmware semantics.

## Reproduction / review gates
- Run independent pyulog extraction and compare raw topic timestamps and field values.
- Verify PX4 version and meaning of each innovation ratio/flag. A simple >1 screen is exploratory.
- Check full flight operational phases and whether early magnetic exceedances coincide with actual control issues.
- Quantify detector threshold sensitivity, data gaps and uncertainty; avoid first-sample = onset.
- Preserve raw SHA-256 and tool version in final Evidence Object.
