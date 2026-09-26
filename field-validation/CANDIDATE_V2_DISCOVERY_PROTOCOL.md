# Candidate v2 — Discovery-Only Research Protocol

Status: pre-implementation research plan. **No Candidate v2 is validated, frozen or promoted.**

## Evidence boundary
- Frozen PAMIR v0.1.0 and threshold 7.0 stay unchanged.
- Corpus v1 (50 cases) is the only permitted development/tuning corpus.
- Independent Holdout v1 (20 cases) is spent: retain its locked report for audit, but do not inspect its per-case outputs, use its case-level features, or tune Candidate v2 to its aggregate results.
- Candidate v1 remains frozen as an unsuccessful comparator, not a development target.
- All future validation requires new real public ULogs with UUID and SHA deduplication against **all** prior Corpus v1 and holdout candidate/acquisition manifests, including quarantined cases.

## Diagnostic hypothesis
Corpus v1's 16 healthy material roots at threshold 7 include 15 estimation roots, of which 10 are output_tracking_error. Candidate v1's corroboration gate was redundant with the frozen requirement for motion and >=3 core families; it changed zero roots. Therefore v2 must test a genuinely independent property rather than rephrase the frozen family-count rule.

## Predeclared discovery experiments (no holdout)
A. **Temporal persistence**: compare root-signal anomaly support across distinct, timestamp-separated observations inside a fixed causal window. Count independent timestamps, not repeated samples from the same instant.
B. **Independent-channel corroboration**: require support from a distinct physical measurement or non-derivative signal rather than merely another signal family; document channel-dependence assumptions. Never treat derived estimator outputs as independent ground truth.
C. **Mechanism-specific diagnostic**: separately report output_tracking_error, innovation, magnetic and power root behaviors. No universal threshold chosen solely from false-root suppression.

Experiments are exploratory and must report: healthy root count, incident root retention, root migration, null-root changes, timestamp stability, and per-case failures on Corpus v1. High anomaly score is not a causation probability.

## Advancement conditions before any new holdout
1. Select and freeze **one** concrete v2 algorithm, parameters, source commit and SHA256 from Corpus v1 only.
2. Verify the algorithm is behaviorally distinct from frozen PAMIR on at least one Corpus v1 case; if not, stop as a redundant candidate.
3. Establish byte-stable deterministic replay and verify no change to frozen baseline or evidence artifacts.
4. Predeclare new holdout size, independent source-label rules, platform/source diversity targets, metrics and stop rules before acquiring or scoring new cases.
5. Stop advancement if a candidate loses any independently labelled incident root retained by frozen PAMIR; healthy false-root reduction alone cannot justify promotion.
6. If results require redesign after new holdout scoring, assign a new version and acquire a further unseen holdout.

## Immediate next deliverable
Build a **Corpus v1-only mechanism and support audit**, not a new selector: for each frozen material root, extract local timestamp support, distinct raw measurement sources, family composition, and evidence gaps. Produce machine-readable diagnostics and aggregate findings without looking at any spent holdout case. Then select a single v2 hypothesis for implementation.
