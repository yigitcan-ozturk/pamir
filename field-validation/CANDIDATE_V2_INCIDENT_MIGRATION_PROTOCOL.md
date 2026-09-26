# Candidate v2 — Incident migration adjudication protocol

Status: pre-analysis protocol; **no causal adjudication yet**. Scope limited to Corpus v1 FV-E003 and FV-I001. Do not inspect spent Independent Holdout v1.

## Source-reported cases

- FV-E003: [PX4 issue #28776](https://github.com/PX4/PX4-Autopilot/issues/28776) reports a runtime COM_SPOOLUP_TIME change and immediate thrust loss in Stabilized mode. Existing frozen root: estimator_status.output_tracking_error[0].
- FV-I001: [PX4 issue #24665](https://github.com/PX4/PX4-Autopilot/issues/24665) reports Sensirion SDP3x airspeed sensor failure in fixed-wing flight. Existing frozen root: estimator_status[1].output_tracking_error[2].

Source issue narratives are **reported hypotheses**, not independently established causal ground truth. No conclusion about a new root is allowed until the actual event sequence and raw signal lineage are inspected.

## Required inspection for each case

1. Verify original ULog SHA256 against Corpus v1 manifest. Abort on mismatch.
2. Run frozen PAMIR detector at threshold 7.0 and frozen selector; record signal, timestamp, family, score.
3. Apply the two already explored external reselection rules without changing parameters: (a) tracking-error candidates require forward control/actuation; (b) all estimation candidates require forward control/actuation. Record new root and delta time from frozen root.
4. For both frozen and reselected roots, extract a timestamp-ordered 2-second pre-event and 3-second post-event window of **all deviations**. Record raw ULog topic names and which signals are derived estimator diagnostics versus measured physical inputs.
5. Test whether the alleged independent corroboration is merely another field of the same topic or derived estimator output. Distinct signal families alone cannot prove independence.
6. Compare temporal order against the **source-reported** event mechanism. Mark each candidate root as consistent, inconsistent, or indeterminate, with an evidence pointer. Do not equate temporal order with causation.
7. If raw physical channel lineage is unavailable, mark **indeterminate**. Do not infer from an anomaly score.

## Decision gate

Candidate v2 remains unfrozen. If either incident migration is unsupported or indeterminate, no causal-correctness claim. Any candidate freeze must specify deterministic tie-breaks, fallback behavior, incident-retention gate, and a new independent holdout protocol before acquisition. Frozen v0.1.0, existing Evidence Packs and holdout v1 remain untouched.
