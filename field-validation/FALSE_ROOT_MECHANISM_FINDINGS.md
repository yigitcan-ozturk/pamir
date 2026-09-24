# False-Root Mechanism Findings — Corpus v1

Status: completed from GitHub Actions run 35967176549.

Frozen PAMIR v0.1 remains unchanged.

## Evidence summary

- Healthy controls: 33
- Material roots at frozen threshold 7.0: 16
- No root at threshold 7.0: 17
- Root family split: estimation 15, power 1
- Ten healthy controls exhibit non-monotonic root presence somewhere across the 5/6/7/8/9/10 generic-threshold sweep.

## Mechanism concentration at frozen 7.0

Normalising estimator instance/vector indices gives:

- output_tracking_error: 10 / 16 false roots
- gravity innovation: 2 / 16
- EV position innovation: 1 / 16
- EV velocity innovation: 1 / 16
- magnetic strength: 1 / 16
- battery voltage: 1 / 16

Thus 62.5% of frozen-reference false roots are output-tracking-error mechanisms, while 93.75% are in the broader estimation family.

## Stability observations

A high root score is not sufficient evidence of a true incident. Examples include FV-H002 (score 120.723), FV-F004 (117.108), FV-F005 (85.046), and FV-G003 (20.208), all independently labelled healthy controls.

Some roots are stable across candidate thresholds (for example FV-F005), some disappear (FV-F003/F008/G002/G003), some switch signal/family (FV-M002), and some disappear then reappear at a higher threshold (FV-H002 and FV-J001). This confirms that the observed error is not reducible to a single scalar threshold.

FV-N002 also shows large root-timestamp migration when the generic threshold changes, indicating root-selection instability in addition to detector sensitivity.

## Calibration design constraints

Any candidate calibration must remain outside frozen v0.1 and must:

1. preserve independent source labels;
2. avoid interpreting anomaly score as probability of causation;
3. distinguish detector sensitivity from material-root selection;
4. explicitly test output-tracking-error, innovation, magnetic and power mechanisms;
5. include non-monotonic cases as regression fixtures;
6. be evaluated on incident retention as well as healthy-control false-root suppression;
7. not be promoted until tested on an independent holdout corpus.

## Next experiment

Build a field-validation-only candidate calibration harness that compares:
- frozen reference semantics;
- family-aware root eligibility;
- persistence/support requirements for estimation-family roots;
- corroboration requirements across independent evidence families.

The experiment must report false-root suppression, incident-root retention, no-conclusion changes, root-family migration and timestamp stability. No frozen v0.1 source change is permitted.
