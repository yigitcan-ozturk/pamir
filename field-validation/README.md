# PAMIR Field Validation Programme

This lane expands PAMIR validation using real public flight telemetry while preserving the frozen PAMIR v0.1.0 baseline, existing Evidence Pack, benchmark manifests, and validated artefacts unchanged.

## Milestone: Field Validation Corpus v1

Target: 50 real PX4 public ULog flights spanning incidents and healthy controls.

Required coverage:
- EKF / GPS
- attitude / control divergence
- propulsion / motor
- power / battery
- failsafe
- sensor anomaly

Every accepted case must record:
source -> license -> original file -> SHA256 -> provenance -> classification -> acceptance criteria -> PAMIR result -> reproducibility result

## Evaluation axes

Corpus size alone is not a success criterion. The programme measures:
- root-event stability
- false-root rate
- threshold sensitivity
- unknown / no-conclusion behaviour
- cross-platform generalisation

## Non-negotiable boundaries

- No synthetic cases in Field Validation Corpus v1.
- Do not edit frozen v0.1.0 detection policy, thresholds, required benchmark corpus, or Evidence Pack.
- Raw source files are immutable once pinned.
- Ground-truth labels are separated from PAMIR output.
- Ambiguous cases remain unknown/no-conclusion rather than being forced into a failure class.
