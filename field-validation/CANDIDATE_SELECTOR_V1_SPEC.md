# Candidate Selector v1 — Frozen Pre-Holdout Specification

Status: **predeclared and frozen before any PAMIR scoring of the independent holdout**.

## Boundary
This selector is an external field-validation candidate. It does not modify `pamir/engine.py`, PAMIR v0.1.0, the frozen Evidence Pack, or validated baseline artefacts.

## Reference behavior
Frozen PAMIR v0.1 root selection remains the reference. Candidate v1 reproduces the frozen material-root selection ordering and eligibility semantics, then applies exactly one additional rule to an **estimation-family root candidate**.

## Candidate A rule
An estimation-family root candidate may be selected only when the candidate's forward causal cluster, over the same frozen 3,000,000 us causal window, contains:
1. at least one core signal family other than `estimation`; and
2. at least three distinct core signal families in total.

Core families are the frozen PAMIR families: `control`, `estimation`, `power`, `actuation`, `attitude`, and `motion`.

Power, actuation and control root eligibility/ordering remain frozen. Candidate v1 introduces no new score threshold and does not use holdout-derived parameters.

## Fallback semantics
If an estimation candidate fails the added gate, it is skipped and selection continues through the same ordered frozen candidate sequence. A later candidate may therefore become the root if it independently satisfies frozen eligibility plus this estimation gate when applicable. If no candidate qualifies, material root is null.

This is deliberately different from the earlier threshold-survival proxy: Candidate v1 is a selector rule, not a threshold sweep.

## Determinism and evaluation
The implementation must be deterministic. Before holdout scoring it will be validated only against Corpus v1 and its code/commit hash frozen. The independent holdout must not be used to tune, redesign, select thresholds, or alter this rule.

Holdout comparison is frozen PAMIR v0.1 unchanged vs Candidate Selector v1. Predeclared stop rule remains: if Candidate v1 loses an incident material root retained by frozen PAMIR, advancement stops.

Any redesign after viewing holdout PAMIR outcomes becomes a new candidate version and requires a fresh independent holdout.
