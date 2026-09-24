# Threshold Sensitivity + False-Root Error Analysis Protocol

Status: ACTIVE — post Corpus v1 (50/50)  
Scope: `field-validation` only  
Engine under test: frozen PAMIR v0.1.0

## Non-negotiable boundary

This experiment does **not** change PAMIR v0.1.0 source thresholds, root-selection policy, frozen benchmark corpus, Evidence Pack, or required CI semantics. Candidate thresholds are injected only by the external analysis harness.

## Predeclared sweep

Generic robust-deviation threshold:

`5.0, 6.0, 7.0, 8.0, 9.0, 10.0`

The frozen reference is **7.0**. All other values are counterfactual analysis settings only.

Everything else remains frozen, including baseline windows, minimum baseline points, magnitude floors, material-direction rules, special multi-axis control-discontinuity logic, root-selection policy, evidence windows, and causal-link rules.

## Primary measurements

For every accepted Corpus v1 case and every threshold:

1. conclusion: deviation / no deviation;
2. selected root signal, family, timestamp and score;
3. root change relative to threshold 7.0;
4. root timestamp shift relative to threshold 7.0;
5. raw deviation count.

Aggregate measurements:

- healthy-control false-root rate;
- incident root-detection rate (descriptive only; not causal accuracy);
- unknown root rate;
- false-root signal/family concentration;
- number of baseline roots suppressed and newly introduced;
- incident roots lost relative to the frozen reference.

## False-root definition

A false root is a material PAMIR root on a case independently labelled `healthy_control`. Source labels are immutable for this analysis. PAMIR output never relabels the source flight.

## Interpretation rules

- Deterministic detection is not proof of causal correctness.
- `confidence` remains an uncalibrated anomaly-strength heuristic.
- Incident root-detection rate is not root-cause accuracy because Corpus v1 does not provide ground-truth causal annotations for every incident.
- Unknown cases are reported separately and never converted into failures or healthy controls.
- No candidate threshold may be promoted into PAMIR v0.1.0 from this experiment.
- A candidate calibration rule requires a separate development lane and independent validation before any product claim.

## Selection discipline

This sweep is diagnostic, not an optimisation contest. Report the complete trade-off surface. Do not choose a threshold solely because it minimizes healthy false roots; any reduction must be reported together with incident roots lost, root-family changes, timestamp shifts, and corpus limitations.

## Reproducibility

Inputs are the 50 SHA256-pinned public PX4 ULogs in `field-validation/corpus/manifest.json`. The analysis harness verifies each hash before scoring and emits machine-readable per-case and aggregate JSON plus a Markdown summary.
