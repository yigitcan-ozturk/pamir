# v0.1 forensic validation review

Initial review: `6e09578a573c2fa4cee48dd22a1f74cb98dd0955` (PR #2).
Integrated concurrent actuator-floor/root-family changes through `c5c7fdd4ee16769b327fc06f7b8570c6092f763c`.

## Result

Not merge-ready. The earlier green benchmark run only proved successful execution.
GitHub Actions run 34659417059 reported crash root score 7.524 and control root
score 12.517, with ten events in both chains, and skipped all five Flight Review
cases after HTTP 403. No comparison failure propagated to CI.

## Reproduction after hardening

Run `python -m pytest -q` (17 passed), then the download and validation scripts.
The strict validator exits 1 and writes `benchmarks/reports/summary.json` before
reporting the blockers. Actual evidence samples are embedded in individual reports.

| Real ULog | Finite samples | Distinct signals | Root | Score | Chain |
| --- | ---: | ---: | --- | ---: | ---: |
| Portable crash | 97,104 | 367 | actuator_outputs.output[0] | 7.257 | 10 |
| Portable non-crash | 427,824 | 350 | actuator_outputs.output[2] | 7.434 | 10 |
| PX4/pyulog parser sample | 555,772 | 196 | estimator_status.states[5] | 19.635 | 7 |

The parser sample is not a labeled incident or a healthy-flight oracle.
Portable pair labels/narratives are inherited from the previous branch; their
original issue URL and timestamped event ordering were not independently recovered.
Do not treat them as reviewed ground truth.

The integrated crash root changes actuator output from 113 to 154 at 602.249435 s.
The non-crash root changes 113 to 155 at 273.808024 s. Both still receive ten-event
failure chains. The independently added actuator floors reduce near-zero score
explosions but do not resolve startup confounding. The first-anomaly-per-signal
detector can hide later incident events. These results do not establish narrative
agreement or a materially lower false-positive burden in the control.

## Verified fixes

- Preserve ULog multi-instance identity instead of interleaving independent sensors.
- Reject non-finite telemetry in ingestion/detection.
- Exclude timing and device metadata from root candidates.
- Classify estimator accuracy as estimation, before generic motion matching.
- Clamp windows to each signal's available observations and export window samples.
- Require strictly positive lag for a likely causal edge.
- Describe confidence as uncalibrated anomaly strength, not causal probability.
- Verify full ULog magic/header and SHA-256 for portable files, including cache hits.
- Fail validation on corrupt evidence, missing required sources, and the portable
  control material-chain regression. The control gate is deliberately conservative;
  it is not a measured population false-positive rate.

## Remaining acceptance work

1. Obtain the five original public logs through authorized source access. All five
   currently return HTTP 403 locally and in CI; no access workaround is used.
2. Establish traceable narrative sources, timestamped incident windows, expected
   predecessor/consequence relationships, and independently reviewed annotations.
3. Address startup/flight-phase confounding, signal-specific units/noise floors,
   and later deviations masked by the first-anomaly policy. Validate on additional
   held-out incident/control flights rather than tuning to this one pair.
4. Re-run full acceptance on the final PR commit. Calibrated causal probabilities
   are not claimed; current links remain temporal/signal-family hypotheses.

## Latest integration through 7dd5585

The rows above describe the c5c7fdd integration. After also integrating the new
estimation/actuation root-direction policy, 17 tests still pass. The crash root is
`battery_status.current_a` (score 77.735); the control root is
`actuator_outputs.output[1]` (10.459). Both retain ten events. All evidence/ordering
invariants pass, but control discrimination, source coverage, and reviewed narrative
annotations remain blocking. `validation_snapshot.json` contains these latest results.
