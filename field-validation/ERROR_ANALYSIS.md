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

## Batch G independent replication

Batch G added eight PX4 v1.18 release-test flights explicitly marked PASS before PAMIR scoring. All eight original ULogs were SHA256-pinned and all eight produced byte-identical two-run replays in GitHub Actions run 35841073946.

- Healthy controls tested: 8
- False roots: 4 (FV-G001, FV-G002, FV-G003, FV-G008)
- Batch G false-root rate: 4 / 8 = 50.0%
- No-root controls: FV-G004, FV-G005, FV-G006, FV-G007

Observed false-root signals were not confined to one family: `estimator_innovations.ev_vpos`, `battery_status.voltage_v`, `estimator_status[2].output_tracking_error[1]`, and `estimator_status[1].output_tracking_error[1]`. Therefore the current evidence does not support treating the issue as only an output-tracking-error phenomenon.

After Batch G, the accepted corpus contains 28 / 50 real flights: 4 incident, 16 healthy controls and 8 unknown. Eight of the 16 accepted healthy controls produce a material root, giving a corpus-level observed false-root rate of 50.0%. All 28 accepted cases are deterministic `pass_exact` replays.

The independent PASS labels remain unchanged. No frozen v0.1.0 threshold or detection rule is modified.

## Batch H cross-platform replication

Batch H tested four PX4 v1.16 release flights on a Holybro S500 / Pixhawk 4 platform, independently recorded as PASS before PAMIR scoring. All four ULogs were SHA256-pinned and produced byte-identical two-run replays in GitHub Actions run 35857703608.

- Healthy controls tested: 4
- False roots: 2 (FV-H002, FV-H003)
- Batch H false-root rate: 2 / 4 = 50.0%
- No-root controls: FV-H001, FV-H004
- H002 root: `estimator_status[1].output_tracking_error[0]`
- H003 root: `estimator_status.output_tracking_error[1]`

After Batch H, the accepted corpus contains 32 / 50 real flights: 4 incident, 20 healthy controls and 8 unknown. Ten of the 20 accepted healthy controls produce a material root, giving an observed healthy-control false-root rate of 50.0%. All 32 accepted cases are deterministic `pass_exact` replays.

Batch H reproduces the 50% healthy-control false-root observation on a different release series and hardware configuration. This is evidence of a current v0.1 calibration/generalisation limitation; it does not by itself establish a single causal mechanism. Frozen v0.1 remains unchanged.
