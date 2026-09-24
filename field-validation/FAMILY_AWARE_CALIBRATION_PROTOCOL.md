# Family-Aware Calibration Experiment Protocol

Status: ACTIVE — post Corpus v1 false-root mechanism analysis.

Frozen PAMIR v0.1.0 remains unchanged. This experiment is an external field-validation counterfactual over the already generated deviation evidence.

## Question

Can stricter material-root eligibility for estimation-family events suppress healthy-control false roots without hiding independently labelled incident roots?

## Predeclared candidates

Reference: frozen v0.1 root selection.

Candidate A — estimation corroboration:
- an estimation-family candidate may root only when its 3 s forward cluster contains at least one non-estimation core family and at least three core families total;
- power/actuation/control semantics remain frozen.

Candidate B — output-tracking-error corroboration:
- only estimation signals containing `output_tracking_error` receive the Candidate-A corroboration gate;
- all other frozen root semantics remain unchanged.

Candidate C — estimation corroboration + score floor:
- Candidate A plus estimation candidate score >= 10.0.
- This is diagnostic only; score is not probability of causation.

## Metrics

For each candidate: healthy false roots, incident roots retained, unknown roots, no-conclusion changes, root-family migration, root-signal migration, and root timestamp shift against frozen reference.

## Selection rule

No candidate is promoted from Corpus v1. A candidate may only advance to independent holdout validation if it suppresses healthy false roots without reducing incident-root retention on Corpus v1. Frozen v0.1 is not modified regardless of result.
