# PAMIR v0.2 — Evidence Calibration and Generalization

## Boundary

PAMIR v0.1 is frozen as the validated baseline. v0.2 must be developed on a separate branch and must not weaken, bypass, or retune the v0.1 benchmark gate.

The v0.1 contract remains mandatory:

- five pinned public PX4 incident ULogs produce material roots;
- three pinned public healthy/control ULogs produce no material root;
- evidence replay remains exact;
- causal ordering remains timestamp-valid;
- unit/regression and benchmark CI remain green.

## Why v0.2 exists

v0.1 proves that PAMIR can reproducibly identify a meaningful first deviation and build an evidence-backed ordered chain on a small public corpus. Two important limitations remain explicit:

1. `confidence` is an uncalibrated anomaly-strength heuristic, not a probability of correctness;
2. `likely_caused` is a conservative temporal/signal-family relation, not demonstrated causal attribution.

v0.2 targets those limitations without expanding into live vehicle control or operational decision-making.

## v0.2 engineering goals

### 1. Confidence calibration layer

Separate raw anomaly strength from calibrated forensic confidence.

The implementation should expose at least:

- raw anomaly score;
- calibrated confidence bucket/score derived from benchmark evidence;
- provenance describing which calibration dataset/version was used;
- explicit `uncalibrated` fallback when calibration evidence is insufficient.

Calibration must never convert a healthy/control case into a material root merely to improve incident recall.

### 2. Root stability / sensitivity analysis

For each benchmark case, measure whether the selected root remains stable under bounded detector perturbations such as:

- rolling-history length;
- minimum prior observations;
- robust-score threshold;
- evidence-window width.

A root that changes materially under small allowed perturbations must be reported as unstable rather than hidden behind a high confidence value.

### 3. Expanded holdout corpus

Add a second public corpus that is not used for threshold tuning.

The holdout set must contain both:

- incident/fault cases;
- healthy/control cases.

Where labels are ambiguous, mark the case as `review_only` and exclude it from hard pass/fail scoring instead of forcing a ground-truth label.

### 4. Causal-chain validation hardening

Keep strict timestamp ordering and add validation that:

- `likely_caused` never points backward in time;
- every relationship is reproducible from the same evidence window;
- signal-family transition rules are versioned and inspectable;
- unsupported relationships downgrade to `followed_by` rather than being forced.

### 5. Machine-readable validation report

Produce a v0.2 validation summary containing at least:

- v0.1 regression status;
- calibration dataset identity/hash;
- holdout dataset identity/hash;
- incident root-detection results;
- healthy/control false-positive results;
- root-stability metrics;
- causal-order validation errors;
- excluded/review-only cases and reasons;
- final `v0_2_complete` boolean.

## Test-first acceptance gates

v0.2 is not complete unless all of the following are true:

1. the existing v0.1 validation gate passes unchanged;
2. no existing v0.1 benchmark expectation is weakened or deleted;
3. calibration and holdout corpora are explicitly separated;
4. every required binary dataset input is SHA-256 pinned;
5. all healthy/control hard-gate cases produce no material root;
6. all required incident hard-gate cases produce a material root or an explicitly documented review-only exclusion decided before tuning;
7. calibrated confidence includes provenance and an insufficient-evidence fallback;
8. root-stability/sensitivity results are generated for all hard-gate incident cases;
9. every causal link satisfies strict timestamp-order invariants;
10. benchmark output is reproducible in GitHub Actions;
11. all new regression tests pass on the supported Python matrix;
12. the final validation snapshot contains zero unexplained gate errors.

## Non-goals

v0.2 does not add:

- autonomous control;
- command generation for an aircraft;
- targeting, weapon, or engagement logic;
- online mission intervention;
- probabilistic claims that exceed measured calibration evidence.

## Development order

1. lock v0.1 regression workflow as a required compatibility gate;
2. introduce calibration/holdout dataset manifests;
3. add root-stability measurement utilities and tests;
4. add confidence calibration model with explicit provenance/fallback;
5. harden causal-chain validation and relationship versioning;
6. add v0.2 validation runner and machine-readable snapshot;
7. run public holdout benchmark;
8. document measured results and only then mark v0.2 merge-ready.
