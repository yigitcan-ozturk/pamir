# Field Validation error analysis

This document records validation failures and limitations without modifying the frozen PAMIR v0.1.0 baseline.

## Snapshot after Batch F

- Accepted real-flight cases: 20 / 50
- Classification balance: 4 incident, 8 healthy controls, 8 unknown
- Deterministic replay: 20 / 20 accepted cases are `pass_exact`
- Accepted healthy controls: 8
- Healthy controls with a material PAMIR root: 4
- Observed corpus-level false-root rate: 4 / 8 = 50.0%

The Batch-F-only false-root rate is 4 / 7 = 57.1%. The corpus-level metric uses all accepted independently labelled healthy controls, including FV-B001, and is therefore 50.0%.

## False-root cases

| Case | Independent label | PAMIR root | Conclusion |
| --- | --- | --- | --- |
| FV-F003 | healthy_control | estimator_status[1].output_tracking_error[2] | deviation_detected |
| FV-F004 | healthy_control | estimator_status.output_tracking_error[0] | deviation_detected |
| FV-F005 | healthy_control | estimator_status.output_tracking_error[0] | deviation_detected |
| FV-F008 | healthy_control | estimator_status.output_tracking_error[0] | deviation_detected |

These source labels are retained. PAMIR output must not relabel a healthy release-test flight as an incident.

## Interpretation boundary

The result is evidence of a current generalisation/calibration limitation in frozen v0.1.0, not evidence that the source flights were incidents. Confidence remains an uncalibrated anomaly-strength heuristic and is not probability of causation.

No v0.1.0 threshold, detection policy, frozen benchmark case, Evidence Pack artefact, or required CI semantic is changed in response to these observations.

## Next analysis lane

1. Compare the four false-root traces against no-root healthy controls without changing v0.1.0.
2. Characterise repeated `estimator_status.output_tracking_error[*]` roots and their downstream evidence.
3. Run a predeclared threshold-sensitivity experiment only in the external field-validation harness.
4. Report whether candidate calibration rules reduce false roots and what incident sensitivity they trade away.
5. Keep any proposed calibration in a separate development lane until independently validated.
